#!/usr/bin/env python
"""EDGAR data spine for Furton Coverage.

This is the ONLY module in the project that touches the network. Everything
downstream (build_model.py, refresh_calendar.py, score.py, the note skills)
reads the cache this module writes into ``data/raw/``.

What it owns
------------
* ticker -> CIK resolution (``resolve_cik``) via sec.gov/files/company_tickers.json
* XBRL companyfacts fetch/cache/parse (``companyfacts``, ``concept_series``,
  ``metric_history``, ``latest_fact``) -- fundamentals + KPIs with full history
* submissions index fetch/cache (``submissions``, ``recent_filings``)
* the earnings 8-K finder (``earnings_8k``): the quarterly 8-K filed under
  **Item 2.02 (Results of Operations)** that carries **Exhibit 99.1** (the
  press release where the printed numbers AND management guidance live). It
  matches on item + exhibit and FAILS LOUD if it cannot identify it uniquely --
  grabbing the wrong 8-K (or the wrong exhibit; big filers attach EX-99.2 CFO
  commentary alongside) would silently poison every number downstream.

SEC etiquette (non-negotiable, enforced here so nobody else has to think about it)
---------------------------------------------------------------------------------
* declared ``User-Agent`` with a contact email on every request
  (``Furton Coverage nicholas@furton.com`` -- overridable via config/settings.json)
* <= 10 requests/second (SEC's cap), single-flight rate limiter
* exponential backoff on 429/503/transient network errors
* every raw response cached under ``data/raw/`` so nothing is fetched twice

The parsing functions (``parse_ticker_map``, ``concept_series``,
``find_earnings_8k_filings``, ``parse_documents``, ``select_press_release``)
are PURE -- they take already-fetched data and return structured results, with
no network access -- so the golden-fixture tests in tests/ can pin their
behaviour against saved real EDGAR payloads and catch format drift.

Windows: run via ``py`` and set ``PYTHONUTF8=1`` (console is cp1252).
"""
from __future__ import annotations

import gzip
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "settings.json"

# Mandated identity from PLAN.md / CLAUDE.md. Used verbatim if config/settings.json
# is absent (it is owned by Session 1 and may not exist yet).
DEFAULT_USER_AGENT = "Furton Coverage nicholas@furton.com"
DEFAULT_RATE_PER_SEC = 10.0
DEFAULT_MAX_RETRIES = 5
DEFAULT_CACHE_REL = "data/raw"

# SEC endpoints
TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik10}.json"
ARCHIVE_BASE = "https://www.sec.gov/Archives/edgar/data/{cik}/{accn}"


def load_settings() -> dict:
    """Read config/settings.json if present; otherwise fall back to the mandated
    defaults. Tolerant of key naming so Session 1 can shape settings.json freely
    (the proposed schema is documented in notes/_inbox/edgar_report.md)."""
    ua = DEFAULT_USER_AGENT
    rate = DEFAULT_RATE_PER_SEC
    retries = DEFAULT_MAX_RETRIES
    cache_rel = DEFAULT_CACHE_REL
    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            cfg = {}
        ua = cfg.get("sec_user_agent") or cfg.get("user_agent") or ua
        rate = (
            cfg.get("rate_limit_per_sec")
            or cfg.get("max_req_per_sec")
            or (cfg.get("rate_limit") or {}).get("max_requests_per_second")
            or rate
        )
        retries = cfg.get("max_retries") or retries
        cache_rel = (cfg.get("paths") or {}).get("raw_cache") or cache_rel
    cache_dir = REPO_ROOT / cache_rel
    return {
        "user_agent": ua,
        "rate_per_sec": float(rate),
        "max_retries": int(retries),
        "cache_dir": cache_dir,
    }


_SETTINGS = load_settings()
USER_AGENT: str = _SETTINGS["user_agent"]
CACHE_DIR: Path = _SETTINGS["cache_dir"]


# --------------------------------------------------------------------------- #
# Errors -- all failures are loud and typed (never a silently degraded result)
# --------------------------------------------------------------------------- #


class EdgarError(Exception):
    """Base class for all edgar.py failures."""


class CikNotFound(EdgarError):
    pass


class EdgarHTTPError(EdgarError):
    pass


class MissingEarnings8K(EdgarError):
    """No 8-K carrying Item 2.02 was found in the submissions index."""


class MissingExhibit991(EdgarError):
    """The earnings 8-K was found but carries no Exhibit 99.1 press release."""


class AmbiguousExhibit991(EdgarError):
    """The earnings 8-K carries more than one Exhibit 99.1 (cannot disambiguate)."""


class ConceptNotFound(EdgarError):
    pass


# --------------------------------------------------------------------------- #
# Rate-limited, backing-off, caching HTTP client
# --------------------------------------------------------------------------- #


class _RateLimiter:
    """Single-flight min-interval limiter (<= rate requests/second)."""

    def __init__(self, rate_per_sec: float):
        self._min_interval = 1.0 / rate_per_sec if rate_per_sec > 0 else 0.0
        self._last = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        delta = now - self._last
        if delta < self._min_interval:
            time.sleep(self._min_interval - delta)
        self._last = time.monotonic()


_limiter = _RateLimiter(_SETTINGS["rate_per_sec"])
_MAX_RETRIES = _SETTINGS["max_retries"]


def _http_get(url: str, *, binary: bool = False):
    """GET a URL with SEC etiquette: rate limit, declared UA, gzip, backoff."""
    _limiter.wait()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
        },
    )
    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                encoding = resp.headers.get("Content-Encoding", "")
            if "gzip" in encoding:
                data = gzip.decompress(data)
            return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            last_exc = exc
            # 429 (too many) / 503 (unavailable) are transient -> back off & retry
            if exc.code in (429, 503) and attempt < _MAX_RETRIES - 1:
                time.sleep(_backoff(attempt))
                continue
            raise EdgarHTTPError(f"HTTP {exc.code} for {url}: {exc.reason}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_exc = exc
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_backoff(attempt))
                continue
            raise EdgarHTTPError(f"network error for {url}: {exc}") from exc
    raise EdgarHTTPError(f"exhausted retries for {url}: {last_exc}")


def _backoff(attempt: int) -> float:
    """Exponential backoff: 1s, 2s, 4s, 8s ... (deterministic, no jitter needed
    for a single-flight client)."""
    return float(2 ** attempt)


def _cached_text(url: str, cache_rel: str, *, force: bool = False) -> str:
    """Fetch text with an on-disk cache under data/raw/. ``cache_rel`` is a path
    relative to the cache dir. Pass ``force=True`` to bypass the cache (used on
    print day when a fresh submissions index / 8-K must not be served stale)."""
    path = CACHE_DIR / cache_rel
    if path.exists() and not force:
        return path.read_text(encoding="utf-8")
    text = _http_get(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text


def _cached_json(url: str, cache_rel: str, *, force: bool = False) -> dict:
    return json.loads(_cached_text(url, cache_rel, force=force))


# --------------------------------------------------------------------------- #
# ticker -> CIK
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CikInfo:
    ticker: str
    cik: int
    cik10: str
    title: str


def parse_ticker_map(raw_json: dict) -> dict[str, CikInfo]:
    """PURE. company_tickers.json (a dict of numbered rows) -> {TICKER: CikInfo}."""
    out: dict[str, CikInfo] = {}
    for row in raw_json.values():
        ticker = str(row["ticker"]).upper()
        cik = int(row["cik_str"])
        out[ticker] = CikInfo(
            ticker=ticker, cik=cik, cik10=str(cik).zfill(10), title=row.get("title", "")
        )
    return out


def _ticker_map(force: bool = False) -> dict[str, CikInfo]:
    raw = _cached_json(TICKER_MAP_URL, "company_tickers.json", force=force)
    return parse_ticker_map(raw)


def resolve_cik(ticker: str, *, force: bool = False) -> CikInfo:
    """Resolve a ticker to its CIK. Raises CikNotFound if unknown."""
    mapping = _ticker_map(force=force)
    info = mapping.get(ticker.upper())
    if info is None:
        raise CikNotFound(f"ticker {ticker!r} not found in SEC company_tickers.json")
    return info


def _coerce_cik(ticker_or_cik) -> int:
    """Accept a ticker ('NVDA'), a CIK int (1045810), or a CIK string
    ('1045810' / '0001045810') and return the integer CIK."""
    if isinstance(ticker_or_cik, int):
        return ticker_or_cik
    s = str(ticker_or_cik).strip()
    if s.isdigit():
        return int(s)
    return resolve_cik(s).cik


# --------------------------------------------------------------------------- #
# XBRL companyfacts
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Fact:
    """One XBRL data point for a concept."""

    end: str
    val: float
    unit: str
    accn: str = ""
    fy: int | None = None
    fp: str | None = None
    form: str | None = None
    filed: str | None = None
    frame: str | None = None
    start: str | None = None


def companyfacts(ticker_or_cik, *, force: bool = False) -> dict:
    """Fetch (and cache) the full XBRL companyfacts payload for a company."""
    cik = _coerce_cik(ticker_or_cik)
    cik10 = str(cik).zfill(10)
    url = COMPANYFACTS_URL.format(cik10=cik10)
    return _cached_json(url, f"companyfacts/CIK{cik10}.json", force=force)


def available_taxonomies(facts_json: dict) -> list[str]:
    """PURE. Taxonomies present, e.g. ['us-gaap', 'dei', 'srt', 'nvda']. A
    company-specific namespace (its ticker/name) signals custom segment/KPI tags."""
    return sorted((facts_json.get("facts") or {}).keys())


def list_concepts(facts_json: dict, taxonomy: str = "us-gaap") -> list[str]:
    """PURE. All concept names tagged under a taxonomy."""
    return sorted(((facts_json.get("facts") or {}).get(taxonomy) or {}).keys())


def concept_facts(facts_json: dict, concept: str, taxonomy: str = "us-gaap") -> dict | None:
    """PURE. The raw concept node ({'label','description','units': {...}}) or None."""
    return ((facts_json.get("facts") or {}).get(taxonomy) or {}).get(concept)


def concept_series(
    facts_json: dict,
    concept: str,
    *,
    taxonomy: str = "us-gaap",
    unit: str | None = None,
) -> list[Fact]:
    """PURE. Flatten one concept's history into Facts, sorted by period end.

    If ``unit`` is None, prefers USD, then USD/shares, then the first unit
    available. Raises ConceptNotFound if the concept is absent (callers that
    want a fallback should use ``named_metric``)."""
    node = concept_facts(facts_json, concept, taxonomy)
    if node is None:
        raise ConceptNotFound(f"{taxonomy}:{concept} not in companyfacts")
    units = node.get("units") or {}
    if not units:
        return []
    if unit is None:
        for pref in ("USD", "USD/shares", "shares", "pure"):
            if pref in units:
                unit = pref
                break
        else:
            unit = next(iter(units))
    rows = units.get(unit) or []
    facts = [
        Fact(
            end=r.get("end", ""),
            val=r.get("val"),
            unit=unit,
            accn=r.get("accn", ""),
            fy=r.get("fy"),
            fp=r.get("fp"),
            form=r.get("form"),
            filed=r.get("filed"),
            frame=r.get("frame"),
            start=r.get("start"),
        )
        for r in rows
    ]
    facts.sort(key=lambda f: (f.end or "", f.filed or ""))
    return facts


# Fallback tag lists -- companies tag the same economic concept under different
# us-gaap names across eras/industries. First hit wins.
REVENUE_TAGS = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "SalesRevenueNet",
]
EPS_DILUTED_TAGS = ["EarningsPerShareDiluted", "IncomeLossFromContinuingOperationsPerDilutedShare"]
EPS_BASIC_TAGS = ["EarningsPerShareBasic"]
NET_INCOME_TAGS = ["NetIncomeLoss", "ProfitLoss"]
OPERATING_INCOME_TAGS = ["OperatingIncomeLoss"]
GROSS_PROFIT_TAGS = ["GrossProfit"]


def named_metric(
    facts_json: dict, tags: list[str], *, taxonomy: str = "us-gaap", unit: str | None = None
) -> tuple[str | None, list[Fact]]:
    """PURE. Choose the best fallback tag and return (tag_used, series).

    Companies migrate the same economic concept between us-gaap tags over time
    (e.g. NVDA tagged revenue under RevenueFromContractWithCustomerExcludingAssessedTax
    through FY2022, then switched to Revenues). Picking merely the first *existing*
    tag would return a stale, dead series. So among the tags that exist we pick
    the one whose history reaches the most recent period end; ties break toward
    the earlier (more specific) tag in the list. Returns (None, []) if none
    exist."""
    best = None  # (max_end, -list_index, tag, series)
    for idx, tag in enumerate(tags):
        if concept_facts(facts_json, tag, taxonomy) is None:
            continue
        series = concept_series(facts_json, tag, taxonomy=taxonomy, unit=unit)
        max_end = series[-1].end if series else ""
        cand = (max_end, -idx, tag, series)
        if best is None or cand[:2] > best[:2]:
            best = cand
    if best is None:
        return None, []
    return best[2], best[3]


def latest_fact(facts_json: dict, tags: list[str], *, form: str | None = None) -> Fact | None:
    """PURE. Most recent Fact (by period end) among the fallback tags, optionally
    filtered to a form (e.g. '10-K' for annual, '10-Q' for quarterly)."""
    _tag, series = named_metric(facts_json, tags)
    if form is not None:
        series = [f for f in series if f.form == form]
    return series[-1] if series else None


def metric_history(
    facts_json: dict, tags: list[str], *, forms: tuple[str, ...] | None = None
) -> list[Fact]:
    """PURE. Full history for a metric (via fallback tags), optionally limited to
    certain forms."""
    _tag, series = named_metric(facts_json, tags)
    if forms is not None:
        series = [f for f in series if f.form in forms]
    return series


# --------------------------------------------------------------------------- #
# Submissions index + the earnings 8-K finder
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Filing:
    accession: str
    accession_nodash: str
    form: str
    filing_date: str
    report_date: str
    items: str
    primary_document: str
    primary_doc_description: str
    acceptance_datetime: str


def submissions(ticker_or_cik, *, force: bool = False) -> dict:
    """Fetch (and cache) the submissions index for a company."""
    cik = _coerce_cik(ticker_or_cik)
    cik10 = str(cik).zfill(10)
    url = SUBMISSIONS_URL.format(cik10=cik10)
    return _cached_json(url, f"submissions/CIK{cik10}.json", force=force)


def recent_filings(submissions_json: dict) -> list[Filing]:
    """PURE. Zip the parallel arrays in submissions.filings.recent into records.

    Note: this covers only the 'recent' block (~1000 filings / ~1yr+), which is
    ample for finding the latest earnings 8-Ks (~4/yr). Deep history would also
    need the paginated 'files' shards; not required here and documented as a
    limitation."""
    recent = (submissions_json.get("filings") or {}).get("recent") or {}
    forms = recent.get("form") or []
    n = len(forms)

    def col(name):
        vals = recent.get(name) or []
        return list(vals) + [""] * (n - len(vals))

    accns = col("accessionNumber")
    fdates = col("filingDate")
    rdates = col("reportDate")
    items = col("items")
    pdocs = col("primaryDocument")
    pdescs = col("primaryDocDescription")
    accepts = col("acceptanceDateTime")

    out = []
    for i in range(n):
        out.append(
            Filing(
                accession=accns[i],
                accession_nodash=str(accns[i]).replace("-", ""),
                form=forms[i],
                filing_date=fdates[i],
                report_date=rdates[i],
                items=items[i] or "",
                primary_document=pdocs[i],
                primary_doc_description=pdescs[i] or "",
                acceptance_datetime=accepts[i] or "",
            )
        )
    return out


# Item 2.02 = "Results of Operations and Financial Condition" -- the earnings item.
EARNINGS_ITEM = "2.02"


def _items_tokens(items: str) -> list[str]:
    return [t.strip() for t in (items or "").split(",") if t.strip()]


def find_earnings_8k_filings(submissions_json: dict) -> list[Filing]:
    """PURE. All 8-Ks carrying Item 2.02, newest first (by acceptance datetime,
    then filing date). This is the candidate set; the exhibit check in
    ``earnings_8k`` confirms the EX-99.1 press release."""
    filings = [
        f
        for f in recent_filings(submissions_json)
        if f.form == "8-K" and EARNINGS_ITEM in _items_tokens(f.items)
    ]
    filings.sort(key=lambda f: (f.acceptance_datetime or "", f.filing_date or ""), reverse=True)
    return filings


@dataclass(frozen=True)
class Document:
    type: str
    sequence: str
    filename: str
    description: str


_DOC_BLOCK_RE = re.compile(r"<DOCUMENT>(.*?)</DOCUMENT>", re.DOTALL)
_TYPE_RE = re.compile(r"<TYPE>\s*([^\r\n<]+)")
_SEQ_RE = re.compile(r"<SEQUENCE>\s*([^\r\n<]+)")
_FILENAME_RE = re.compile(r"<FILENAME>\s*([^\r\n<]+)")
_DESC_RE = re.compile(r"<DESCRIPTION>\s*([^\r\n<]+)")


def parse_documents(index_headers_text: str) -> list[Document]:
    """PURE. Parse the SGML <DOCUMENT> manifest out of an ``{accn}-index-headers.html``
    payload. The exhibit TYPE (e.g. 'EX-99.1', 'EX-99.2') lives here and NOWHERE
    in index.json (whose 'type' field is just a display-icon name)."""
    text = html.unescape(index_headers_text)
    docs: list[Document] = []
    for block in _DOC_BLOCK_RE.findall(text):
        tm = _TYPE_RE.search(block)
        fm = _FILENAME_RE.search(block)
        if not tm or not fm:
            continue
        sm = _SEQ_RE.search(block)
        dm = _DESC_RE.search(block)
        docs.append(
            Document(
                type=tm.group(1).strip(),
                sequence=(sm.group(1).strip() if sm else ""),
                filename=fm.group(1).strip(),
                description=(dm.group(1).strip() if dm else ""),
            )
        )
    if not docs:
        raise EdgarError(
            "no <DOCUMENT> blocks parsed from index-headers (EDGAR format drift?)"
        )
    return docs


def _norm_exhibit(t: str) -> str:
    """Normalize an exhibit TYPE for matching: uppercase, drop spaces, and
    collapse a zero-padded sub-index ('EX-99.01' -> 'EX-99.1')."""
    t = t.upper().replace(" ", "")
    m = re.fullmatch(r"EX-99\.0*(\d+)", t)
    return f"EX-99.{m.group(1)}" if m else t


def select_press_release(docs: list[Document]) -> Document:
    """PURE. Return the earnings press-release exhibit.

    Preference order:
      1. exactly one EX-99.1 (the standard earnings press-release exhibit;
         when a filer also attaches EX-99.2 CFO commentary this is what picks
         the right one),
      2. else exactly one bare EX-99 -- some large filers (e.g. LLY, GE) type
         the press release as EX-99 with no sub-index.

    FAILS LOUD (MissingExhibit991 / AmbiguousExhibit991) rather than guessing if
    it cannot land on exactly one press release -- a wrong exhibit silently
    poisons every extracted number downstream."""
    ex991 = [d for d in docs if _norm_exhibit(d.type) == "EX-99.1"]
    if len(ex991) == 1:
        return ex991[0]
    if len(ex991) > 1:
        raise AmbiguousExhibit991(
            f"{len(ex991)} EX-99.1 documents in this 8-K: "
            + ", ".join(d.filename for d in ex991)
        )
    ex99 = [d for d in docs if _norm_exhibit(d.type) == "EX-99"]
    if len(ex99) == 1:
        return ex99[0]
    available = ", ".join(sorted({d.type for d in docs})) or "(none)"
    if len(ex99) > 1:
        raise AmbiguousExhibit991(
            f"{len(ex99)} bare EX-99 documents in this 8-K (cannot disambiguate "
            f"the press release): " + ", ".join(d.filename for d in ex99)
        )
    raise MissingExhibit991(
        f"no EX-99.1 or EX-99 press release in this 8-K; exhibits present: {available}"
    )


@dataclass(frozen=True)
class Earnings8K:
    cik: int
    accession: str
    accession_nodash: str
    filing_date: str
    report_date: str
    items: str
    filing_index_url: str
    press_release_filename: str
    press_release_url: str
    press_release_exhibit: str


def _index_headers(cik: int, accession_nodash: str, *, force: bool = False) -> str:
    accession = _redash(accession_nodash)
    url = f"{ARCHIVE_BASE.format(cik=cik, accn=accession_nodash)}/{accession}-index-headers.html"
    return _cached_text(url, f"index_headers/{accession}.html", force=force)


def _redash(accession_nodash: str) -> str:
    """0001045810-26-000051 <- 000104581026000051."""
    s = accession_nodash
    if "-" in s:
        return s
    return f"{s[0:10]}-{s[10:12]}-{s[12:]}"


def earnings_8k(ticker_or_cik, *, which: int = 0, force: bool = False) -> Earnings8K:
    """Locate a company's earnings 8-K: the Item-2.02 8-K carrying Exhibit 99.1.

    ``which=0`` is the most recent, ``which=1`` the one before it, etc. -- useful
    for backfilling prior quarters. FAILS LOUD (typed EdgarError) if no Item-2.02
    8-K exists, or if the chosen one has no unique EX-99.1 press release.

    Pass ``force=True`` to bypass the cache (print-day freshness)."""
    cik = _coerce_cik(ticker_or_cik)
    subs = submissions(cik, force=force)
    candidates = find_earnings_8k_filings(subs)
    if not candidates:
        raise MissingEarnings8K(
            f"no 8-K with Item {EARNINGS_ITEM} in recent submissions for CIK {cik}"
        )
    if which >= len(candidates):
        raise MissingEarnings8K(
            f"requested earnings 8-K #{which} but only {len(candidates)} found for CIK {cik}"
        )
    filing = candidates[which]
    docs = parse_documents(_index_headers(cik, filing.accession_nodash, force=force))
    pr = select_press_release(docs)
    base = ARCHIVE_BASE.format(cik=cik, accn=filing.accession_nodash)
    return Earnings8K(
        cik=cik,
        accession=filing.accession,
        accession_nodash=filing.accession_nodash,
        filing_date=filing.filing_date,
        report_date=filing.report_date,
        items=filing.items,
        filing_index_url=f"{base}/{filing.accession}-index.html",
        press_release_filename=pr.filename,
        press_release_url=f"{base}/{pr.filename}",
        press_release_exhibit=_norm_exhibit(pr.type),
    )


# --------------------------------------------------------------------------- #
# Document text (press-release body -- used to detect written guidance)
# --------------------------------------------------------------------------- #

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t ]+")


def html_to_text(raw_html: str) -> str:
    """Cheap HTML -> text for scanning a press release for guidance language.
    Not a full renderer; drops tags, unescapes entities, collapses whitespace."""
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw_html)
    text = re.sub(r"(?i)<(br|/p|/div|/tr|/h[1-6])[^>]*>", "\n", text)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _WS_RE.sub(" ", text)
    lines = [ln.strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def fetch_document(cik: int, accession_nodash: str, filename: str, *, force: bool = False) -> str:
    """Fetch a single document from a filing's archive folder (cached)."""
    url = f"{ARCHIVE_BASE.format(cik=cik, accn=accession_nodash)}/{filename}"
    return _cached_text(url, f"documents/{accession_nodash}_{filename}", force=force)


def press_release_text(ticker_or_cik, *, which: int = 0, force: bool = False) -> tuple[Earnings8K, str]:
    """Convenience: the earnings 8-K plus its EX-99.1 press release as plain text."""
    e = earnings_8k(ticker_or_cik, which=which, force=force)
    raw = fetch_document(e.cik, e.accession_nodash, e.press_release_filename, force=force)
    return e, html_to_text(raw)


# --------------------------------------------------------------------------- #
# CLI -- for by-hand sanity checks (merge-gate step) and the verify skill
# --------------------------------------------------------------------------- #


def _main(argv: list[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(description="EDGAR data spine sanity CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("cik").add_argument("ticker")
    fp = sub.add_parser("facts")
    fp.add_argument("ticker")
    ep = sub.add_parser("earnings8k")
    ep.add_argument("ticker")
    ep.add_argument("--which", type=int, default=0)
    dp = sub.add_parser("docs")
    dp.add_argument("ticker")
    dp.add_argument("--which", type=int, default=0)
    args = p.parse_args(argv)

    if args.cmd == "cik":
        info = resolve_cik(args.ticker)
        print(f"{info.ticker}  CIK {info.cik}  ({info.cik10})  {info.title}")
        return 0

    if args.cmd == "facts":
        facts = companyfacts(args.ticker)
        taxes = available_taxonomies(facts)
        print(f"{args.ticker}: taxonomies={taxes}")
        print(f"  us-gaap concepts: {len(list_concepts(facts, 'us-gaap'))}")
        tag, rev = named_metric(facts, REVENUE_TAGS)
        if rev:
            last = rev[-1]
            print(f"  revenue via {tag}: {last.val:,.0f} {last.unit} (end {last.end}, {last.form})")
        etag, eps = named_metric(facts, EPS_DILUTED_TAGS)
        if eps:
            last = eps[-1]
            print(f"  diluted EPS via {etag}: {last.val} {last.unit} (end {last.end}, {last.form})")
        return 0

    if args.cmd == "earnings8k":
        e = earnings_8k(args.ticker, which=args.which)
        print(f"{args.ticker} earnings 8-K #{args.which}")
        print(f"  accession   : {e.accession}")
        print(f"  filed       : {e.filing_date}   period: {e.report_date}")
        print(f"  items       : {e.items}")
        print(f"  press release: {e.press_release_filename}")
        print(f"  URL         : {e.press_release_url}")
        return 0

    if args.cmd == "docs":
        cik = _coerce_cik(args.ticker)
        subs = submissions(cik)
        cands = find_earnings_8k_filings(subs)
        if not cands:
            raise MissingEarnings8K(f"no Item 2.02 8-K for {args.ticker}")
        filing = cands[args.which]
        docs = parse_documents(_index_headers(cik, filing.accession_nodash))
        print(f"{args.ticker} 8-K {filing.accession} documents:")
        for d in docs:
            print(f"  [{d.type:12}] {d.filename}  ({d.description})")
        return 0

    return 1


if __name__ == "__main__":
    try:
        sys.exit(_main(sys.argv[1:]))
    except EdgarError as exc:
        print(f"EDGAR ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
