#!/usr/bin/env python3
"""Furton Coverage static-site generator.

Reads notes/, scorecard/summary.json, scorecard/{calls,guidance}/*.jsonl,
models/, and config/{universe,calendar}.json, and renders the public site
into docs/ (GitHub Pages serves that directory as-is).

Design rules (PLAN.md par.3):
  - NO network calls: everything comes from files already on disk, so the
    site always builds, even offline.
  - Fail loud: a malformed note frontmatter, an unreadable shard, or a
    ticker/folder mismatch aborts the build with a clear message -- never a
    silently wrong page.
  - docs/ is generated output; never hand-edit it.

Visual language mirrors furton.ai v2 (same palette / type / components) so
the two sites can eventually share a domain. Chart fills use darker steps of
the brand hues, validated with the dataviz palette validator against the
dark surface (#070b14): bars #6d7cff; beat/met/missed #1fa06b/#6d7cff/#e04358.

Usage:  py scripts/build_site.py            (set PYTHONUTF8=1 on Windows)
"""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("build_site.py requires PyYAML (py -m pip install pyyaml)")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score  # noqa: E402  -- the scorecard engine owns validation + grading semantics

ROOT = Path(__file__).resolve().parent.parent
SITE_SRC = ROOT / "site_src"
DOCS = ROOT / "docs"
NOTES_DIR = ROOT / "notes"
MODELS_DIR = ROOT / "models"
SCORECARD_DIR = ROOT / "scorecard"
CONFIG_DIR = ROOT / "config"

CHARTJS_CDN = "https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"
# SRI pin for the file above (sha384 of the published artifact, computed 2026-07-11).
CHARTJS_SRI = "sha384-JUh163oCRItcbPme8pYnROHQMC6fNKTBWtRG3I3I0erJkzNgL7uxKlNwcrcFKeqF"

# Chart palette -- validated (dataviz skill validate_palette.js, dark surface
# #070b14): lightness band, chroma floor, CVD separation, contrast all PASS.
CH_BAR = "#6d7cff"
CH_BEAT, CH_MET, CH_MISS = "#1fa06b", "#6d7cff", "#e04358"
CH_GRID = "rgba(255,255,255,.05)"
CH_TICK = "#7d879e"

NOTE_TYPES = {"preview", "flash", "review", "initiation"}
TYPE_LABEL = {
    "preview": "T−1 Preview",
    "flash": "T+0 Flash",
    "review": "T+2 Review",
    "initiation": "Initiation",
}
TYPE_SHORT = {
    "preview": "Preview",
    "flash": "Flash",
    "review": "Review",
    "initiation": "Initiation",
}
# The 9 fields notes/_templates/SCHEMA.md marks required on every note.
REQUIRED_FRONTMATTER = (
    "ticker", "type", "event_date", "published_at",
    "period", "fiscal_year_end", "basis", "source_filings", "fact_check",
)

# Presentation-only display names: config/universe.json stores names as they
# appear in the SEC ticker map (often ALL CAPS or wrongly cased for branding).
DISPLAY_NAME = {
    "NVDA": "NVIDIA Corporation",
    "AMD": "Advanced Micro Devices, Inc.",
    "AVGO": "Broadcom Inc.",
    "MU": "Micron Technology, Inc.",
    "CRM": "Salesforce, Inc.",
    "PANW": "Palo Alto Networks, Inc.",
    "CRWD": "CrowdStrike Holdings, Inc.",
    "AMZN": "Amazon.com, Inc.",
    "LLY": "Eli Lilly and Company",
    "DE": "Deere & Company",
}


def display_name(u: dict) -> str:
    name = DISPLAY_NAME.get(u["ticker"])
    if name:
        return name
    raw = str(u.get("company", u["ticker"]))
    # fallback for promoted alternates: title-case only the shouty SEC style
    return raw.title() if raw.isupper() else raw


class BuildError(SystemExit):
    def __init__(self, msg: str):
        super().__init__(f"BUILD FAILED: {msg}")


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- data loading

def load_json(path: Path) -> dict:
    if not path.is_file():
        raise BuildError(f"missing required input {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BuildError(f"invalid JSON in {path.relative_to(ROOT)}: {e}")


def load_universe() -> list[dict]:
    data = load_json(CONFIG_DIR / "universe.json")
    roster = [u for u in data.get("universe", []) if u.get("candidate") is True]
    if not roster:
        raise BuildError("config/universe.json has no candidate=true roster entries")
    return roster


def load_calendar() -> dict:
    data = load_json(CONFIG_DIR / "calendar.json")
    if "events" not in data or not isinstance(data["events"], dict):
        raise BuildError("config/calendar.json has no 'events' mapping -- refusing to publish a calendar-less site")
    for t, ev in data["events"].items():
        d = ev.get("next_earnings_date")
        if d is not None and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(d)):
            raise BuildError(f"calendar.json events[{t}].next_earnings_date {d!r} is not YYYY-MM-DD")
    return data["events"]


def load_summary() -> dict:
    data = load_json(SCORECARD_DIR / "summary.json")
    for key in ("totals", "our_calls", "guidance_accuracy", "by_ticker"):
        if key not in data:
            raise BuildError(f"scorecard/summary.json missing '{key}' -- regenerate with py scripts/score.py")
    return data


def parse_note(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise BuildError(f"{path.relative_to(ROOT)}: no frontmatter block")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        raise BuildError(f"{path.relative_to(ROOT)}: unterminated frontmatter block")
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        raise BuildError(f"{path.relative_to(ROOT)}: frontmatter YAML error: {e}")
    if not isinstance(fm, dict):
        raise BuildError(f"{path.relative_to(ROOT)}: frontmatter is not a mapping")
    for key in REQUIRED_FRONTMATTER:
        if not fm.get(key):
            raise BuildError(f"{path.relative_to(ROOT)}: frontmatter missing required '{key}'")
    if fm["type"] not in NOTE_TYPES:
        raise BuildError(f"{path.relative_to(ROOT)}: unknown note type '{fm['type']}'")
    folder = path.parent.name
    if fm["ticker"] != folder:
        raise BuildError(
            f"{path.relative_to(ROOT)}: frontmatter ticker '{fm['ticker']}' != folder '{folder}'"
        )
    return {"path": path, "fm": fm, "body": text[m.end():]}


def load_notes() -> list[dict]:
    notes = []
    if not NOTES_DIR.is_dir():
        return notes
    for tdir in sorted(NOTES_DIR.iterdir()):
        if not tdir.is_dir() or tdir.name.startswith("_"):
            continue
        for md in sorted(tdir.glob("*.md")):
            notes.append(parse_note(md))
    return notes


def load_shards(kind: str) -> dict[str, list[dict]]:
    """kind: 'calls' | 'guidance' -> {ticker: [records]}.

    Delegates to score.py's loaders so the site renders exactly the records the
    scorer accepts: full schema validation, ticker-vs-filename guard, and the
    duplicate-id check all fail the build loudly instead of publishing a wrong row.
    """
    loader = score.load_all_calls if kind == "calls" else score.load_all_guidance
    try:
        records = loader(SCORECARD_DIR / kind)
    except score.ScorecardError as e:
        raise BuildError(f"scorecard/{kind} failed score.py validation: {e}")
    out: dict[str, list[dict]] = {}
    for r in records:
        out.setdefault(r["ticker"], []).append(r)
    return out


# ------------------------------------------------------------ markdown -> html

_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_SAFE_HREF = re.compile(r"^(https?://|mailto:|#|/|\./|\.\./|[\w.\-]+(/|\.html|\.pdf|\.xlsx))", re.IGNORECASE)


def _safe_link(m: re.Match) -> str:
    text, href = m.group(1), m.group(2)
    if not _SAFE_HREF.match(href):
        # javascript:/data:/vbscript: etc. never become live links on a public page
        return text
    return f'<a href="{href}">{text}</a>'


def inline_md(s: str) -> str:
    s = esc(s)
    # pull code spans out first so bold/italic/link markup inside them is inert
    spans: list[str] = []

    def stash(m: re.Match) -> str:
        spans.append(m.group(1))
        return f"\x00{len(spans) - 1}\x00"

    s = _INLINE_CODE.sub(stash, s)
    s = _BOLD.sub(r"<strong>\1</strong>", s)
    s = _ITALIC.sub(r"<em>\1</em>", s)
    s = _LINK.sub(_safe_link, s)
    for i, span in enumerate(spans):
        s = s.replace(f"\x00{i}\x00", f"<code>{span}</code>")
    return s


def md_to_html(md: str) -> str:
    """Minimal Markdown renderer for the constrained subset our notes use:
    headings, hr, pipe tables, ul/ol lists (with indented continuation lines),
    blockquotes, paragraphs, bold/italic/links/inline code."""
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i, n = 0, len(lines)

    def is_table_sep(s: str) -> bool:
        return bool(re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", s)) and "-" in s

    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        # fenced code block
        if stripped.startswith("```"):
            i += 1
            code: list[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            if i >= n:
                raise BuildError("markdown: unterminated ``` code fence in a note body")
            i += 1  # closing fence
            out.append(f'<pre class="tscroll"><code>{esc(chr(10).join(code))}</code></pre>')
            continue
        # heading
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{inline_md(m.group(2))}</h{level}>")
            i += 1
            continue
        # hr
        if re.match(r"^-{3,}$", stripped) or re.match(r"^\*{3,}$", stripped):
            out.append("<hr>")
            i += 1
            continue
        # table
        if stripped.startswith("|") and i + 1 < n and is_table_sep(lines[i + 1]):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            thead = "".join(f"<th>{inline_md(h)}</th>" for h in header)
            tbody = "".join(
                "<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in row) + "</tr>"
                for row in rows
            )
            out.append(
                f'<div class="tscroll"><table><thead><tr>{thead}</tr></thead>'
                f"<tbody>{tbody}</tbody></table></div>"
            )
            continue
        # blockquote
        if stripped.startswith(">"):
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f"<blockquote><p>{inline_md(' '.join(quote))}</p></blockquote>")
            continue
        # lists (with indented continuation lines folded into the item)
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if m:
            ordered = m.group(2)[0].isdigit()
            tag = "ol" if ordered else "ul"
            items: list[str] = []
            while i < n:
                lm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if lm and (lm.group(2)[0].isdigit()) == ordered:
                    items.append(lm.group(3).strip())
                    i += 1
                    # continuation lines: indented, not blank, not a new bullet
                    while (
                        i < n
                        and lines[i].strip()
                        and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i])
                        and lines[i].startswith(" ")
                    ):
                        items[-1] += " " + lines[i].strip()
                        i += 1
                else:
                    break
            lis = "".join(f"<li>{inline_md(it)}</li>" for it in items)
            out.append(f"<{tag}>{lis}</{tag}>")
            continue
        # paragraph: gather until blank line or block starter
        para = [stripped]
        i += 1
        while i < n and lines[i].strip():
            nxt = lines[i].strip()
            if (
                nxt.startswith("#")
                or nxt.startswith("|")
                or nxt.startswith(">")
                or re.match(r"^([-*]|\d+\.)\s+", nxt)
                or re.match(r"^-{3,}$", nxt)
            ):
                break
            para.append(nxt)
            i += 1
        out.append(f"<p>{inline_md(' '.join(para))}</p>")
    return "\n".join(out)


_NON_PARA = re.compile(r"^(#|\||>|```|[-*]\s|\d+\.\s|-{3,}$|\*{3,}$|\*[^*])")


def first_paragraph(md: str, limit: int = 200) -> str:
    """Plain-text teaser: first real paragraph of the body. Skips headings,
    tables, blockquotes, fences, list items, and rules -- but a paragraph
    OPENING with emphasis (**Verdict:** ...) or a negative number is prose."""
    for block in re.split(r"\n\s*\n", md):
        b = block.strip()
        if not b or _NON_PARA.match(b):
            continue
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", b)
        text = re.sub(r"[*`_]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > limit:
            text = text[: limit - 1].rsplit(" ", 1)[0] + "…"
        return text
    return ""


# ------------------------------------------------------------------ templating

def load_base() -> str:
    p = SITE_SRC / "base.html"
    if not p.is_file():
        raise BuildError("site_src/base.html missing")
    return p.read_text(encoding="utf-8")


def render_page(
    base: str,
    *,
    title: str,
    description: str,
    content: str,
    root: str,
    active: str = "",
    extra_head: str = "",
    extra_body: str = "",
    build_stamp: str = "",
) -> str:
    # substitute tokens in the TEMPLATE only, then splice content last, so note
    # bodies that mention {{TOKENS}} are neither replaced nor build-breaking
    if base.count("{{CONTENT}}") != 1:
        raise BuildError("site_src/base.html must contain exactly one {{CONTENT}} token")
    head, tail = base.split("{{CONTENT}}")
    subs = {
        "{{TITLE}}": esc(title),
        "{{DESCRIPTION}}": esc(description),
        "{{ROOT}}": root,
        "{{EXTRA_HEAD}}": extra_head,
        "{{EXTRA_BODY}}": extra_body,
        "{{BUILD_STAMP}}": esc(build_stamp),
    }
    for cur in ("HOME", "RESEARCH", "SCORECARD", "ABOUT"):
        subs["{{CUR_%s}}" % cur] = 'aria-current="page"' if active == cur.lower() else ""
    for k, v in subs.items():
        head = head.replace(k, v)
        tail = tail.replace(k, v)
    leftover = re.search(r"\{\{[A-Z_]+\}\}", head + tail)
    if leftover:
        raise BuildError(f"unreplaced template token {leftover.group(0)} in page '{title}'")
    return head + content + tail


def write_page(rel: str, html_text: str) -> None:
    dest = DOCS / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html_text, encoding="utf-8")


# ------------------------------------------------------------------ formatting

def fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(str(iso).replace("Z", "+00:00")).strftime("%b %d, %Y")
    except ValueError:
        raise BuildError(f"unparseable date {iso!r} in site inputs -- fix the source file")


def json_js(data) -> str:
    """JSON safe to inline inside a <script> element ('<' escaped so a
    data-driven string containing '</script>' can't terminate the block)."""
    return json.dumps(data).replace("<", "\\u003c")


def fmt_pct(x) -> str:
    return "—" if x is None else f"{round(x * 100)}%"


def fmt_num(v, unit: str = "") -> str:
    if v is None:
        return "—"
    if isinstance(v, (int, float)):
        s = f"{v:,.2f}".rstrip("0").rstrip(".")
    else:
        s = str(v)
    if unit == "USD_M":
        return f"${s}M"
    if unit == "USD_B":
        return f"${s}B"
    if unit == "eps_usd":
        return f"${s}"
    if unit == "pct":
        return f"{s}%"
    return s


def call_target(call: dict, unit: str = "") -> str:
    kind = call.get("kind")
    if kind == "direction":
        b = call.get("benchmark", {})
        if b.get("kind") == "range":
            band = f"{fmt_num(b.get('low'), unit)}–{fmt_num(b.get('high'), unit)}"
        else:
            band = f"{fmt_num(b.get('value'), unit)} ±{fmt_num(b.get('tolerance'))}"
        return f"{str(call.get('value', '')).upper()} vs {band}"
    if kind == "range":
        return f"{fmt_num(call.get('low'), unit)}–{fmt_num(call.get('high'), unit)}"
    if kind == "point":
        return f"{fmt_num(call.get('value'), unit)} ±{fmt_num(call.get('tolerance'))}"
    if kind == "qualitative":
        v = str(call.get("value", ""))
        return v[:120] + ("…" if len(v) > 120 else "")
    return "—"


def grade_call_record(rec: dict) -> str:
    """Status chip for a call row. Grading itself is score.py's -- the single
    source of the beat/met/miss semantics, the basis guard, and the fail-loud
    rules -- so the public chips can never drift from summary.json."""
    try:
        result = score.grade_call(rec)
    except score.ScorecardError as e:
        raise BuildError(f"call record {rec.get('id', '?')} failed score.py grading: {e}")
    if result["status"] in ("pending", "qualitative"):
        return "qual" if result["status"] == "qualitative" else "pending"
    if result["hit"] is None:
        return "graded"
    return "hit" if result["hit"] else "miss"


def grade_guidance_record(rec: dict) -> str:
    """Beat/met/missed chip for a guidance row, graded by score.py itself."""
    try:
        result = score.grade_guidance(rec)
    except score.ScorecardError as e:
        raise BuildError(f"guidance record {rec.get('id', '?')} failed score.py grading: {e}")
    if result["status"] == "pending":
        return "pending"
    return {"beat": "beat", "met": "met", "miss": "missed"}.get(result["outcome"], "graded")


CHIP_LABEL = {
    "hit": "HIT", "miss": "MISS", "pending": "PENDING", "qual": "QUALITATIVE",
    "graded": "GRADED", "beat": "BEAT", "met": "MET", "missed": "MISSED",
}


def chip(status: str) -> str:
    cls = {"graded": "met"}.get(status, status)
    return f'<span class="chip {cls}">{CHIP_LABEL.get(status, status.upper())}</span>'


def dummy_flag(rec: dict) -> str:
    return ' <span class="badge dim">sample</span>' if rec.get("dummy") else ""


# ------------------------------------------------------------------- fragments

def note_href(note: dict, root: str) -> str:
    p = note["path"]
    return f"{root}notes/{p.parent.name}/{p.stem}.html"


def res_card(note: dict, root: str) -> str:
    fm = note["fm"]
    teaser = first_paragraph(note["body"])
    fc = fm.get("fact_check", {}) or {}
    fc_badge = (
        ' <span class="badge up">fact-checked</span>'
        if fc.get("status") == "passed"
        else ""
    )
    return f"""<a class="res-card reveal" href="{note_href(note, root)}" data-ticker="{esc(fm['ticker'])}" data-type="{esc(fm['type'])}">
  <div class="res-kind">{esc(TYPE_LABEL[fm['type']])} · {esc(fm['ticker'])}</div>
  <h4>{esc(fm['ticker'])} {esc(TYPE_SHORT[fm['type']])} — {esc(fm.get('period', fm['event_date']))}</h4>
  <p>{esc(teaser)}</p>
  <div class="res-meta">Published {esc(fmt_date(fm['published_at']))}{fc_badge}</div>
  <span class="res-link">Read the note →</span>
</a>"""


def countdown_strip(events: list[dict]) -> str:
    chips = []
    for ev in events:
        chips.append(
            f"""<div class="count-chip" data-date="{esc(ev['next_earnings_date'])}">
  <span class="t">{esc(ev['ticker'])}</span>
  <span class="d" data-count>{esc(fmt_date(ev['next_earnings_date']))}</span>
</div>"""
        )
    return '<div class="count-strip" aria-label="Upcoming earnings dates">' + "".join(chips) + "</div>"


COUNTDOWN_JS = """
<script>
(function(){
  const now = new Date(); now.setHours(0,0,0,0);
  document.querySelectorAll('.count-chip').forEach(ch=>{
    // earnings dates are US-market events: anchor to ET (fixed -05:00; the DST
    // hour of slop can't flip a Math.round day count) instead of viewer-local
    const d = new Date(ch.dataset.date + 'T00:00:00-05:00');
    const days = Math.round((d - now) / 86400000);
    const el = ch.querySelector('[data-count]');
    const date = d.toLocaleDateString('en-US',{month:'short',day:'numeric'});
    if (days > 1) el.innerHTML = date + ' \\u00b7 in <b>' + days + ' days</b>';
    else if (days === 1) el.innerHTML = date + ' \\u00b7 <b>tomorrow</b>';
    else if (days === 0) el.innerHTML = date + ' \\u00b7 <b>today</b>';
    else el.innerHTML = date + ' \\u00b7 printed';
    if (days >= 0 && days <= 7) ch.classList.add('soon');
  });
})();
</script>"""


# ------------------------------------------------------------------ page: home

def build_home(base, stamp, roster, calendar, summary, notes) -> None:
    oc = summary.get("our_calls", {}).get("overall", {})
    ga = summary.get("guidance_accuracy", {}).get("overall", {})
    _d = summary.get("dummy", {})
    dummy = bool(_d.get("included")) and (_d.get("call_records", 0) + _d.get("guidance_records", 0)) > 0
    sample = ' <span class="badge">sample data</span>' if dummy else ""

    events = sorted(
        (e for e in calendar.values() if e.get("next_earnings_date")),
        key=lambda e: e["next_earnings_date"],
    )
    # the hero line is baked into static HTML, so never advertise a past print
    # as upcoming: pick the first event on/after the build date, else say nothing
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    next_ev = next((e for e in events if e["next_earnings_date"] >= today), None)
    next_line = ""
    if next_ev:
        next_line = (
            f'<p class="asof" style="margin-top:18px">Next print: '
            f'<b style="color:var(--acc2)">{esc(next_ev["ticker"])}</b> · '
            f'{esc(fmt_date(next_ev["next_earnings_date"]))} '
            f'({esc(next_ev.get("time_of_day", "").replace("_", " "))})</p>'
        )

    tiles = f"""<div class="tiles reveal">
  <div class="tile"><div class="k">Our hit rate{sample}</div><div class="v">{fmt_pct(oc.get('hit_rate'))}</div><div class="s">{oc.get('n_graded', 0)} calls graded · {oc.get('pending', 0)} pending</div></div>
  <div class="tile"><div class="k">Names covered</div><div class="v">{len(roster)}</div><div class="s">AI infrastructure + 2 decorrelators</div></div>
  <div class="tile"><div class="k">Mgmt guidance record{sample}</div><div class="v">{ga.get('beat', 0)}–{ga.get('met', 0)}–{ga.get('missed', 0)}</div><div class="s">beat–met–missed own guidance</div></div>
  <div class="tile"><div class="k">Published notes</div><div class="v">{len(notes)}</div><div class="s">previews · flashes · reviews</div></div>
</div>"""

    notes_per_ticker: dict[str, int] = {}
    for x in notes:
        notes_per_ticker[x["fm"]["ticker"]] = notes_per_ticker.get(x["fm"]["ticker"], 0) + 1
    cards = []
    for u in roster:
        ev = calendar.get(u["ticker"])
        nxt = (
            f'Next print {esc(fmt_date(ev["next_earnings_date"]))}'
            if ev and ev.get("next_earnings_date")
            else "Next print TBD"
        )
        n_notes = notes_per_ticker.get(u["ticker"], 0)
        note_s = f" · {n_notes} note{'s' if n_notes != 1 else ''}" if n_notes else ""
        cards.append(
            f"""<a class="uni-card reveal" href="tickers/{u['ticker'].lower()}.html">
  <div class="uni-ticker">{esc(u['ticker'])}</div>
  <div class="uni-name">{esc(display_name(u))}</div>
  <div class="uni-sector">{esc(u['sector'])}</div>
  <div class="uni-next">{nxt}{note_s}</div>
  <span class="uni-arrow">Coverage page →</span>
</a>"""
        )

    dow = [u["ticker"] for u in roster if u.get("dow_member")]
    dow_note = (
        f"{len(dow)} name{'s' if len(dow) != 1 else ''} ({', '.join(dow)}) deliberately overlap the "
        if dow
        else "The roster is disjoint from the "
    )

    latest = notes[:3]  # notes arrive sorted newest-first from main()
    latest_cards = "".join(res_card(nt, "") for nt in latest)
    latest_section = (
        f"""
<section id="latest" class="section-pad">
  <div class="wrap">
    <div class="sec-head reveal">
      <h2>Latest <em>research</em></h2>
      <p class="sec-lead">Every note is generated from the primary documents — the 8-K press release and XBRL company facts — and passes an adversarial fact-check gate before it is published.</p>
    </div>
    <div class="res-grid">{latest_cards}</div>
    <p style="margin-top:26px"><a class="btn btn-ghost" href="research.html">Full research library <span class="arr">→</span></a></p>
  </div>
</section>"""
        if latest
        else ""
    )

    content = f"""
<header class="page-head home">
  <div class="wrap">
    <div class="eyebrow">Automated earnings desk · SEC EDGAR sourced · Est. 2026</div>
    <h1>An earnings desk that <span class="grad">grades its own calls</span> in public.</h1>
    <p class="hero-sub">{len(roster)} companies covered on a real research-desk cadence — preview the night before, flash within hours of the print, full review after the filing — built entirely on free, public SEC data. Every call is timestamped, scored against management's own written guidance, and published either way.</p>
    <div class="hero-cta">
      <a href="scorecard.html" class="btn btn-primary">See the scorecard <span class="arr">→</span></a>
      <a href="#universe" class="btn btn-ghost">The coverage universe</a>
    </div>
    {next_line}
  </div>
</header>

<section id="stats" class="section-pad" style="padding-top:0">
  <div class="wrap">
    {tiles}
    <div style="margin-top:26px" class="reveal">
      <p class="asof" style="margin-bottom:12px">Upcoming prints</p>
      {countdown_strip(events)}
    </div>
  </div>
</section>

<section id="universe" class="section-pad light">
  <div class="wrap">
    <div class="sec-head reveal">
      <h2>The coverage <em>universe</em></h2>
      <p class="sec-lead">An AI-infrastructure book — the accelerator supply chain, the software layer on top of it, and the one hyperscaler that writes its guidance down — plus two deliberate decorrelators so the scorecard can't be one lucky sector run. Every name earns its slot the same way: it publishes quantitative forward guidance in its 8-K press release, so every one of our calls is gradable against a public document.</p>
    </div>
    <div class="uni-grid">{''.join(cards)}</div>
    <p class="note">Universe frozen 2026-07-08. Changes require a dated note. {esc(dow_note)}<a href="https://furton.ai" style="color:#077ea3">Furton Research</a> Dow 30 screen for cross-project comparison.</p>
  </div>
</section>
{latest_section}
<section id="how" class="section-pad">
  <div class="wrap">
    <div class="sec-head reveal">
      <h2>How the desk <em>works</em></h2>
    </div>
    <div class="grid2">
      <div class="card reveal"><h3>T−1 · Preview</h3><p class="note" style="margin-top:0">The night before a print: the guidance table from the prior quarter's 8-K, our falsifiable calls against it, and what actually matters going in.</p></div>
      <div class="card reveal"><h3>T+0 · Flash</h3><p class="note" style="margin-top:0">Within hours of the earnings 8-K hitting EDGAR: headline actuals versus our calls, guidance changes, and a first-read verdict. Preview calls get graded the same day.</p></div>
      <div class="card reveal"><h3>T+2 · Review</h3><p class="note" style="margin-top:0">Once the 10-Q lands: full synthesis with XBRL detail, an updated Excel model, and the thesis update — the deepest of the three notes.</p></div>
      <div class="card reveal"><h3>The scorecard</h3><p class="note" style="margin-top:0">score.py grades every numeric call deterministically — no model grades its own work — and management's guidance accuracy is tracked with the same rigor. Misses stay published.</p></div>
    </div>
  </div>
</section>
"""
    write_page(
        "index.html",
        render_page(
            base,
            title="Furton Coverage · An earnings desk that grades its own calls",
            description="Automated earnings coverage on 10 names — previews, same-day flashes, reviews, Excel models, and a public accuracy scorecard — built entirely on free SEC EDGAR data.",
            content=content,
            root="",
            active="home",
            extra_body=COUNTDOWN_JS,
            build_stamp=stamp,
        ),
    )


# -------------------------------------------------------------- page: research

def build_research(base, stamp, notes) -> None:
    tickers = sorted({x["fm"]["ticker"] for x in notes})
    tick_pills = "".join(
        f'<button class="fpill" data-filter-ticker="{esc(t)}" aria-pressed="false">{esc(t)}</button>'
        for t in tickers
    )
    type_pills = "".join(
        f'<button class="fpill" data-filter-type="{k}" aria-pressed="false">{esc(v)}</button>'
        for k, v in TYPE_LABEL.items()
    )
    cards = "".join(res_card(nt, "") for nt in notes)  # pre-sorted newest-first
    content = f"""
<header class="page-head">
  <div class="wrap">
    <div class="eyebrow">Research library</div>
    <h1>Every note, <span class="grad">timestamped</span>.</h1>
    <p class="hero-sub">All published research, newest first. Previews are written before the print, flashes the same day, reviews once the 10-Q is filed — and a missed deadline becomes an honestly-timestamped delayed note, never a backdated one.</p>
  </div>
</header>
<section class="section-pad" style="padding-top:24px">
  <div class="wrap">
    <div class="fpills" role="group" aria-label="Filter notes">
      <div class="fgroup"><span class="lab">Ticker</span><button class="fpill active" data-filter-ticker="all" aria-pressed="true">All</button>{tick_pills}</div>
      <div class="fgroup" style="margin-left:14px"><span class="lab">Type</span><button class="fpill active" data-filter-type="all" aria-pressed="true">All</button>{type_pills}</div>
    </div>
    <div class="res-grid" id="lib">{cards}</div>
    <div class="fempty" id="libEmpty" style="display:none;margin-top:14px">No notes match this filter yet.</div>
  </div>
</section>
"""
    filter_js = """
<script>
(function(){
  const sel={ticker:'all', type:'all'};
  const cards=[...document.querySelectorAll('#lib .res-card')];
  const empty=document.getElementById('libEmpty');
  function apply(){
    let shown=0;
    cards.forEach(c=>{
      const ok=(sel.ticker==='all'||c.dataset.ticker===sel.ticker)&&(sel.type==='all'||c.dataset.type===sel.type);
      c.style.display=ok?'':'none'; if(ok)shown++;
    });
    empty.style.display=shown?'none':'';
  }
  for (const facet of ['ticker','type']){
    const attr='filter'+facet[0].toUpperCase()+facet.slice(1);
    document.querySelectorAll('[data-filter-'+facet+']').forEach(b=>b.addEventListener('click',()=>{
      sel[facet]=b.dataset[attr];
      b.closest('.fgroup').querySelectorAll('.fpill').forEach(x=>{
        const on=x===b;
        x.classList.toggle('active',on);
        x.setAttribute('aria-pressed',on?'true':'false');
      });
      apply();
    }));
  }
})();
</script>"""
    write_page(
        "research.html",
        render_page(
            base,
            title="Research library · Furton Coverage",
            description="All published Furton Coverage research notes — previews, flashes, reviews, and initiations — filterable by ticker and type.",
            content=content,
            root="",
            active="research",
            extra_body=filter_js,
            build_stamp=stamp,
        ),
    )


# ------------------------------------------------------------- page: scorecard

def build_scorecard(base, stamp, summary) -> None:
    oc = summary.get("our_calls", {})
    ga = summary.get("guidance_accuracy", {})
    overall = oc.get("overall", {})
    g_over = ga.get("overall", {})
    totals = summary.get("totals", {})
    _d = summary.get("dummy", {})
    dummy = bool(_d.get("included")) and (_d.get("call_records", 0) + _d.get("guidance_records", 0)) > 0

    banner = ""
    if dummy:
        banner = """<div class="dummy-banner reveal" role="note"><span aria-hidden="true">⚠</span><div><b>Sample data.</b> The scorecard is currently seeded with schema-validation dummy records so the pipeline can be exercised end-to-end. They are flagged in the store, excluded from any real claims, and will be deleted when the first real coverage cycle publishes (Merge Gate 3).</div></div>"""

    # ---- chart data (computed here so the page stays static + offline-safe)
    ct = oc.get("by_call_type", {})
    ct_order = [k for k in ("preview", "flash", "review", "initiation") if k in ct]
    ct_data = {
        "labels": [TYPE_LABEL[k] for k in ct_order],
        "rates": [
            None if ct[k].get("hit_rate") is None else round(ct[k]["hit_rate"] * 100, 1)
            for k in ct_order
        ],
        "n": [ct[k].get("n_graded", 0) for k in ct_order],
    }
    bm = {
        k: v
        for k, v in oc.get("by_metric", {}).items()
        if v.get("n_graded", 0) > 0 and v.get("hit_rate") is not None
    }
    bm_sorted = sorted(bm.items(), key=lambda kv: kv[1]["hit_rate"], reverse=True)
    bm_data = {
        "labels": [k.replace("_", " ") for k, _ in bm_sorted],
        "rates": [round(v["hit_rate"] * 100, 1) for _, v in bm_sorted],
        "n": [v["n_graded"] for _, v in bm_sorted],
    }
    gt = ga.get("by_ticker", {})
    gt_order = sorted(gt.keys())
    gt_data = {
        "labels": gt_order,
        "beat": [gt[t].get("beat", 0) for t in gt_order],
        "met": [gt[t].get("met", 0) for t in gt_order],
        "missed": [gt[t].get("missed", 0) for t in gt_order],
    }
    calib = [
        {
            "x": round(b["mean_confidence"] * 100, 1),
            "y": round(b["empirical_rate"] * 100, 1),
            "n": b["n"],
        }
        for b in oc.get("calibration", {}).get("bins", [])
        if b.get("n", 0) > 0
        and b.get("empirical_rate") is not None
        and b.get("mean_confidence") is not None
    ]

    tiles = f"""<div class="tiles reveal">
  <div class="tile"><div class="k">Overall hit rate</div><div class="v">{fmt_pct(overall.get('hit_rate'))}</div><div class="s">{overall.get('hits', 0)} of {overall.get('n_graded', 0)} graded calls</div></div>
  <div class="tile"><div class="k">Calls pending</div><div class="v">{overall.get('pending', 0)}</div><div class="s">graded when the print lands</div></div>
  <div class="tile"><div class="k">Mgmt vs own guidance</div><div class="v">{g_over.get('beat', 0)}–{g_over.get('met', 0)}–{g_over.get('missed', 0)}</div><div class="s">beat–met–missed · {g_over.get('n_graded', 0)} graded</div></div>
  <div class="tile"><div class="k">Records tracked</div><div class="v">{totals.get('call_records', 0)} + {totals.get('guidance_records', 0)}</div><div class="s">our calls + guidance entries</div></div>
</div>"""

    # per-ticker table (the accessible table-view of the charts)
    bt = summary.get("by_ticker", {})
    rows = []
    for t in sorted(bt.keys()):
        c = bt[t].get("our_calls", {})
        g = bt[t].get("guidance", {})
        rows.append(
            f"<tr><td><a href='tickers/{t.lower()}.html' style='color:inherit'>{esc(t)}</a></td>"
            f"<td>{c.get('n_graded', 0)}</td><td>{c.get('hits', 0)}</td>"
            f"<td>{fmt_pct(c.get('hit_rate'))}</td><td>{c.get('pending', 0)}</td>"
            f"<td>{g.get('beat', 0)}</td><td>{g.get('met', 0)}</td><td>{g.get('missed', 0)}</td></tr>"
        )
    table = f"""<div class="tscroll"><table>
<caption class="small" style="text-align:left;padding-bottom:10px">Per-ticker detail — the table view of every chart above.</caption>
<thead><tr><th>Ticker</th><th>Graded</th><th>Hits</th><th>Hit rate</th><th>Pending</th><th>Guid. beat</th><th>Guid. met</th><th>Guid. missed</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""

    content = f"""
<header class="page-head">
  <div class="wrap">
    <div class="eyebrow">Accuracy scorecard</div>
    <h1>The calls, <span class="grad">graded in code</span>.</h1>
    <p class="hero-sub">Numeric calls are graded deterministically by <code style="font-family:var(--mono);font-size:.9em">score.py</code> against management's own written guidance — no model grades its own work. Management's accuracy against its own guidance is tracked with the same rigor. Misses stay on the board.</p>
    <p class="asof" style="margin-top:16px">Generated {esc(fmt_date(summary.get('generated_at', '')))} · scorecard/summary.json</p>
  </div>
</header>
<section class="section-pad" style="padding-top:24px">
  <div class="wrap">
    {banner}
    {tiles}
    <div class="grid2" style="margin-top:26px">
      <div class="card reveal">
        <h3>Our hit rate by note type <small>graded calls only</small></h3>
        <div class="chartbox"><canvas id="chType" role="img" aria-label="Bar chart of our hit rate by note type">Chart unavailable — the per-ticker table below carries the data.</canvas></div>
        <p class="note">Share of graded calls that landed, split by the note that made them. Bar labels carry the sample size — early on these are small.</p>
      </div>
      <div class="card reveal">
        <h3>Our hit rate by metric <small>graded calls only</small></h3>
        <div class="chartbox"><canvas id="chMetric" role="img" aria-label="Horizontal bar chart of our hit rate by metric">Chart unavailable — the per-ticker table below carries the data.</canvas></div>
        <p class="note">Which lines we read well — and which we don't. A 0% bar is a published miss, left visible on purpose.</p>
      </div>
      <div class="card reveal">
        <h3>Management vs. its own guidance <small>by ticker</small></h3>
        <div class="chartbox"><canvas id="chGuide" role="img" aria-label="Stacked bar chart of management guidance outcomes by ticker">Chart unavailable — the per-ticker table below carries the data.</canvas></div>
        <p class="note">Did the company beat, meet, or miss the guidance it published in its own prior 8-K? This is the desk's benchmark — and a dataset in its own right.</p>
      </div>
      <div class="card reveal">
        <h3>Calibration <small>confidence vs. outcome</small></h3>
        <div class="chartbox"><canvas id="chCalib" role="img" aria-label="Scatter chart of stated confidence versus empirical hit rate">Chart unavailable — the per-ticker table below carries the data.</canvas></div>
        <p class="note">Each point is a confidence decile: stated confidence (x) against the share of those calls that actually hit (y). Points on the dashed line mean we're exactly as confident as we should be.</p>
      </div>
    </div>
  </div>
</section>
<section class="section-pad light" style="padding-top:64px;padding-bottom:64px">
  <div class="wrap">
    <div class="sec-head reveal"><h2>Per-ticker <em>detail</em></h2></div>
    <div class="card reveal">{table}</div>
    <p class="note">Pending calls are excluded from hit-rate denominators until the print lands. Every record carries its GAAP/non-GAAP basis and the grader refuses to compare across bases.</p>
  </div>
</section>
"""
    chart_js = f"""
<script src="{CHARTJS_CDN}" integrity="{CHARTJS_SRI}" crossorigin="anonymous"></script>
<script>
(function(){{
  if (typeof Chart === 'undefined') return;  // offline: tables still carry the data
  const MONO = "'JetBrains Mono', monospace";
  Chart.defaults.color = '{CH_TICK}';
  Chart.defaults.font.family = MONO;
  Chart.defaults.font.size = 10.5;
  Chart.defaults.borderColor = '{CH_GRID}';
  const GRID = {{color:'{CH_GRID}'}};
  const TT = {{backgroundColor:'rgba(10,14,26,.96)',borderColor:'rgba(255,255,255,.12)',borderWidth:1,titleFont:{{family:MONO}},bodyFont:{{family:MONO}},padding:10,cornerRadius:8}};
  const pctAxis = {{beginAtZero:true,max:100,grid:GRID,ticks:{{callback:v=>v+'%'}}}};

  const ct = {json_js(ct_data)};
  new Chart(document.getElementById('chType'), {{
    type:'bar',
    data:{{labels:ct.labels,datasets:[{{data:ct.rates,backgroundColor:'{CH_BAR}',borderRadius:4,borderSkipped:'bottom',maxBarThickness:34}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}},tooltip:{{...TT,callbacks:{{label:c=>c.parsed.y+'% hit rate \\u00b7 n='+ct.n[c.dataIndex]}}}}}},scales:{{y:pctAxis,x:{{grid:{{display:false}}}}}}}}
  }});

  const bm = {json_js(bm_data)};
  new Chart(document.getElementById('chMetric'), {{
    type:'bar',
    data:{{labels:bm.labels,datasets:[{{data:bm.rates,backgroundColor:'{CH_BAR}',borderRadius:4,borderSkipped:'left',maxBarThickness:18}}]}},
    options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}},tooltip:{{...TT,callbacks:{{label:c=>c.parsed.x+'% hit rate \\u00b7 n='+bm.n[c.dataIndex]}}}}}},scales:{{x:pctAxis,y:{{grid:{{display:false}}}}}}}}
  }});

  const gt = {json_js(gt_data)};
  const seg = {{borderColor:'#0d1322',borderWidth:2,borderRadius:4,maxBarThickness:26}};
  new Chart(document.getElementById('chGuide'), {{
    type:'bar',
    data:{{labels:gt.labels,datasets:[
      {{label:'Beat',data:gt.beat,backgroundColor:'{CH_BEAT}',...seg}},
      {{label:'Met',data:gt.met,backgroundColor:'{CH_MET}',...seg}},
      {{label:'Missed',data:gt.missed,backgroundColor:'{CH_MISS}',...seg}}
    ]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'bottom',labels:{{boxWidth:10,boxHeight:10,borderRadius:2,useBorderRadius:true,padding:16}}}},tooltip:TT}},
      scales:{{x:{{stacked:true,grid:{{display:false}}}},y:{{stacked:true,grid:GRID,ticks:{{precision:0}}}}}}}}
  }});

  const calib = {json_js(calib)};
  new Chart(document.getElementById('chCalib'), {{
    type:'scatter',
    data:{{datasets:[
      {{label:'Perfect calibration',data:[{{x:0,y:0}},{{x:100,y:100}}],type:'line',borderColor:'rgba(139,147,167,.45)',borderDash:[5,5],borderWidth:1.5,pointRadius:0,order:2}},
      {{label:'Confidence deciles',data:calib,backgroundColor:'{CH_BAR}',pointRadius:6,pointHoverRadius:8,order:1}}
    ]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{...TT,filter:i=>i.dataset.type!=='line',callbacks:{{label:c=>'stated '+c.parsed.x+'% \\u2192 hit '+c.parsed.y+'% (n='+calib[c.dataIndex].n+')'}}}}}},
      scales:{{x:{{...pctAxis,title:{{display:true,text:'stated confidence'}}}},y:{{...pctAxis,title:{{display:true,text:'empirical hit rate'}}}}}}}}
  }});
}})();
</script>"""
    write_page(
        "scorecard.html",
        render_page(
            base,
            title="Scorecard · Furton Coverage",
            description="The public accuracy scorecard: our hit rate by note type and metric, management's record against its own guidance, and our calibration curve.",
            content=content,
            root="",
            active="scorecard",
            extra_body=chart_js,
            build_stamp=stamp,
        ),
    )


# ---------------------------------------------------------- page: ticker pages

def build_ticker_pages(base, stamp, roster, calendar, summary, notes, calls, guidance) -> None:
    bt = summary.get("by_ticker", {})
    for u in roster:
        t = u["ticker"]
        ev = calendar.get(t)
        t_notes = sorted(
            (x for x in notes if x["fm"]["ticker"] == t),
            key=lambda x: (str(x["fm"]["event_date"]), str(x["fm"]["published_at"])),
            reverse=True,
        )
        t_calls = calls.get(t, [])
        t_guid = guidance.get(t, [])
        stats_c = bt.get(t, {}).get("our_calls", {})
        stats_g = bt.get(t, {}).get("guidance", {})
        any_dummy = any(r.get("dummy") for r in t_calls + t_guid)

        # models -- "latest" is decided by the dated filename convention
        # (<TICKER>_model_<YYYY-MM-DD>.xlsx, CLAUDE.md), so an off-convention
        # file fails the build instead of silently winning a string sort
        model_dir = MODELS_DIR / t
        xlsx = sorted(model_dir.glob("*.xlsx")) if model_dir.is_dir() else []
        dated = []
        for x in xlsx:
            m = re.match(rf"^{re.escape(t)}_model_(\d{{4}}-\d{{2}}-\d{{2}})\.xlsx$", x.name)
            if not m:
                raise BuildError(
                    f"models/{t}/{x.name} does not match <TICKER>_model_<YYYY-MM-DD>.xlsx -- "
                    "rename it or the site can't pick the current model"
                )
            dated.append((m.group(1), x))
        if dated:
            latest = max(dated)[1]
            model_html = (
                f'<a class="btn btn-ghost" href="../models/{t}/{esc(latest.name)}" download>'
                f'Download the Excel model <span class="arr">↓</span></a>'
                f'<p class="note">{esc(latest.name)} — built from XBRL company facts by build_model.py. '
                f"Headline financials from companyfacts; segment/KPI lines from the 8-K press release.</p>"
            )
        else:
            model_html = '<p class="note" style="margin-top:0">Excel model publishes with this name’s initiation note.</p>'

        next_html = (
            f"{esc(fmt_date(ev['next_earnings_date']))} · {esc(ev.get('time_of_day', '').replace('_', ' '))} · {esc(ev.get('confidence', ''))}"
            if ev and ev.get("next_earnings_date")
            else "TBD"
        )

        tiles = f"""<div class="tiles reveal">
  <div class="tile"><div class="k">Next print</div><div class="v" style="font-size:16px">{next_html}</div><div class="s">refresh_calendar.py · cited source</div></div>
  <div class="tile"><div class="k">Our record here</div><div class="v">{stats_c.get('hits', 0)}/{stats_c.get('n_graded', 0)}</div><div class="s">hits / graded · {stats_c.get('pending', 0)} pending</div></div>
  <div class="tile"><div class="k">Mgmt vs own guide</div><div class="v">{stats_g.get('beat', 0)}–{stats_g.get('met', 0)}–{stats_g.get('missed', 0)}</div><div class="s">beat–met–missed</div></div>
  <div class="tile"><div class="k">Guidance basis</div><div class="v" style="font-size:16px">{esc(u.get('basis', '').replace('_', '-').upper())}</div><div class="s">how this company guides</div></div>
</div>"""

        if t_notes:
            items = []
            for nt in t_notes:
                fm = nt["fm"]
                items.append(
                    f"""<div class="tl-item">
  <div class="tl-date">{esc(fmt_date(fm['event_date']))} · {esc(TYPE_LABEL[fm['type']])}</div>
  <div class="tl-title"><a href="{note_href(nt, '../')}">{esc(t)} {esc(fm.get('period', ''))} {esc(fm['type'])}</a></div>
  <div class="tl-sub">{esc(first_paragraph(nt['body'], 150))}</div>
</div>"""
                )
            timeline = f'<div class="timeline">{"".join(items)}</div>'
        else:
            timeline = '<div class="fempty">No notes yet — coverage initiates with this name’s first cycle.</div>'

        # call record table
        if t_calls:
            rows = []
            for r in sorted(t_calls, key=lambda r: str(r.get("timestamp", "")), reverse=True):
                status = grade_call_record(r)
                actual = r.get("actual") or {}
                rows.append(
                    f"<tr><td>{esc(r.get('metric', '').replace('_', ' '))}{dummy_flag(r)}</td>"
                    f"<td>{esc(r.get('period', ''))}</td>"
                    f"<td>{esc(r.get('call_type', ''))}</td>"
                    f"<td style='white-space:normal'>{esc(call_target(r.get('call', {}), r.get('unit', '')))}</td>"
                    f"<td>{esc(fmt_num(actual.get('value'), r.get('unit', '')))}</td>"
                    f"<td>{chip(status)}</td></tr>"
                )
            calls_html = f"""<div class="tscroll"><table>
<thead><tr><th>Metric</th><th>Period</th><th>From</th><th>Our call</th><th>Actual</th><th>Result</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""
        else:
            calls_html = '<div class="fempty">No calls recorded yet.</div>'

        if t_guid:
            rows = []
            for r in sorted(t_guid, key=lambda r: str(r.get("timestamp", "")), reverse=True):
                g = r.get("guidance", {})
                actual = r.get("actual") or {}
                outcome = grade_guidance_record(r)
                src = r.get("source_filing", "")
                src_a = f'<a href="{esc(src)}" target="_blank" rel="noopener" style="color:var(--acc2)">8-K ↗</a>' if src else "—"
                rows.append(
                    f"<tr><td>{esc(r.get('metric', '').replace('_', ' '))}{dummy_flag(r)}</td>"
                    f"<td>{esc(r.get('period', ''))}</td>"
                    f"<td style='white-space:normal'>{esc(call_target(g, r.get('unit', '')) if g else '—')}</td>"
                    f"<td>{esc(fmt_num(actual.get('value'), r.get('unit', '')))}</td>"
                    f"<td>{chip(str(outcome))}</td>"
                    f"<td>{src_a}</td></tr>"
                )
            guid_html = f"""<div class="tscroll"><table>
<thead><tr><th>Metric</th><th>Period</th><th>Guided</th><th>Actual</th><th>Outcome</th><th>Source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""
        else:
            guid_html = '<div class="fempty">No guidance history yet — backfilled from the last four 8-Ks in Phase 4.</div>'

        sample_note = (
            '<p class="note"><b style="color:var(--warn)">Sample data:</b> rows marked '
            '<span class="badge dim">sample</span> are schema-validation dummies, deleted at first real publish.</p>'
            if any_dummy
            else ""
        )

        content = f"""
<header class="page-head">
  <div class="wrap">
    <div class="eyebrow">{esc(u['sector'])}</div>
    <h1>{esc(t)} <span class="grad" style="font-size:.55em;font-weight:700">{esc(display_name(u))}</span></h1>
    <p class="hero-sub">{esc(u.get('one_liner', ''))}</p>
  </div>
</header>
<section class="section-pad" style="padding-top:24px">
  <div class="wrap">
    {tiles}
    <div class="grid2" style="margin-top:26px">
      <div class="card reveal">
        <h3>Note timeline</h3>
        {timeline}
      </div>
      <div class="card reveal">
        <h3>The model</h3>
        {model_html}
        <h3 style="margin-top:26px">Fiscal profile</h3>
        <p class="note" style="margin-top:0">FY ends {esc(u.get('fiscal_year_end', '?'))} · typically reports {esc(', '.join(u.get('typical_reporting_months', [])))} · guides on a {esc(u.get('basis', '').replace('_', '-'))} basis{' · Dow 30 member' if u.get('dow_member') else ''}.</p>
      </div>
    </div>
  </div>
</section>
<section class="section-pad light" style="padding-top:64px;padding-bottom:64px">
  <div class="wrap">
    <div class="sec-head reveal"><h2>Call <em>record</em></h2>
      <p class="sec-lead">Every call we've published on {esc(t)}, graded against management's written guidance. Pending calls grade when the print lands.</p>
    </div>
    <div class="card reveal">{calls_html}</div>
    <div class="sec-head reveal" style="margin-top:44px"><h2>Guidance <em>tracker</em></h2>
      <p class="sec-lead">Management's own record: what {esc(t)} guided in its 8-K press releases, versus what it later reported.</p>
    </div>
    <div class="card reveal">{guid_html}</div>
    {sample_note}
  </div>
</section>
"""
        write_page(
            f"tickers/{t.lower()}.html",
            render_page(
                base,
                title=f"{t} · Furton Coverage",
                description=f"Furton Coverage on {display_name(u)}: note timeline, graded call record, guidance tracker, and downloadable Excel model.",
                content=content,
                root="../",
                active="",
                build_stamp=stamp,
            ),
        )


# ------------------------------------------------------------ page: note pages

def build_note_pages(base, stamp, notes) -> None:
    for nt in notes:
        fm, body = nt["fm"], nt["body"]
        t = fm["ticker"]
        fc = fm.get("fact_check", {}) or {}
        fc_html = ""
        if fc.get("status"):
            ok = fc["status"] == "passed"
            fc_html = (
                f'<span class="factcheck{"" if ok else " failed"}">'
                f'{"✓ fact-check passed" if ok else "⚠ fact-check " + esc(fc["status"])}</span>'
            )
        srcs = fm.get("source_filings") or []
        src_html = ""
        if srcs:
            links = []
            for s in srcs:
                url = s.get("url", "")
                desc = s.get("description", url)
                if url.startswith("http"):
                    links.append(f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(desc)} ↗</a>')
                else:
                    links.append(f"<span class='small'>{esc(desc)}</span>")
            src_html = f'<div class="src-list"><h4>Source documents</h4>{"".join(links)}</div>'

        content = f"""
<header class="page-head" style="padding-bottom:10px">
  <div class="wrap">
    <div class="eyebrow"><a href="../../tickers/{t.lower()}.html" style="color:inherit">{esc(t)}</a> · {esc(TYPE_LABEL[fm['type']])}</div>
  </div>
</header>
<section style="padding:10px 0 96px">
  <div class="wrap">
    <article class="article">
      <div class="note-meta">
        <span>Event {esc(fmt_date(fm['event_date']))}</span><span class="sep">·</span>
        <span>Published {esc(fmt_date(fm['published_at']))}</span><span class="sep">·</span>
        <span>{esc(fm.get('period', ''))}</span><span class="sep">·</span>
        <span>basis: {esc(str(fm.get('basis', '')).replace('_', '-'))}</span>
        {fc_html}
      </div>
      {md_to_html(body)}
      {src_html}
      <p class="note" style="margin-top:30px">Structured call and guidance records for this note live in its frontmatter and are graded deterministically by score.py — see the <a href="../../scorecard.html">scorecard</a>.</p>
    </article>
  </div>
</section>
"""
        write_page(
            f"notes/{t}/{nt['path'].stem}.html",
            render_page(
                base,
                title=f"{t} {fm['type']} · {fm.get('period', fm['event_date'])} · Furton Coverage",
                description=f"{t} {TYPE_LABEL[fm['type']]} for {fm.get('period', fm['event_date'])} — {first_paragraph(body, 150)}",
                content=content,
                root="../../",
                active="research",
                build_stamp=stamp,
            ),
        )


# ----------------------------------------------------------------- page: about

def build_about(base, stamp) -> None:
    content = """
<header class="page-head">
  <div class="wrap">
    <div class="eyebrow">Methodology</div>
    <h1>How the desk is <span class="grad">built</span>.</h1>
    <p class="hero-sub">A stub of the full methodology note (which publishes in Phase 5). The short version: public data in, falsifiable calls out, deterministic grading in between.</p>
  </div>
</header>
<section class="section-pad" style="padding-top:24px">
  <div class="wrap">
    <article class="article">
      <h2>The data spine</h2>
      <p>Every number on this site comes from SEC EDGAR: XBRL company facts for financial history, the submissions index for filings, and the quarterly earnings 8-K (Exhibit 99.1 press release) for reported actuals and management guidance. One module owns all network access, enforces the SEC's fair-use etiquette (declared User-Agent, ≤10 requests/second, caching), and fails loudly rather than guessing — if it can't uniquely identify the right earnings 8-K, nothing downstream runs. EDGAR data is public domain, which is why every note and model here is fully ours to publish.</p>
      <h2>The cadence</h2>
      <p>Preview the night before a print (T−1), flash within hours of the 8-K hitting EDGAR (T+0), full review once the 10-Q lands (T+2), plus an initiation note and Excel model per name. A missed deadline becomes an honestly-timestamped delayed note — never backdated — and a skipped print gets a dated skip note. The scorecard counts skips.</p>
      <h2>Grading</h2>
      <p>Calls are graded against <strong>management's own written guidance</strong> — itself an EDGAR artifact (the prior quarter's press release) — so the benchmark is free, public, and auditable end to end. Numeric grading is deterministic code, not model judgment. Every call and guidance record carries its GAAP or non-GAAP basis, and the grader refuses to compare across bases: companies guide on their own basis, and grading a non-GAAP guide against a GAAP actual would silently bias the whole board.</p>
      <h2>Honest limitations</h2>
      <ul>
        <li>Guidance lives in press-release prose and is phrased differently every quarter; extraction is verified adversarially against the source document, and "no quantitative guidance given" is recorded honestly rather than invented.</li>
        <li>EDGAR carries no earnings-call transcripts and no sell-side consensus — qualitative color leans on cited web sources, and consensus appears only as cited color, never as the grading benchmark.</li>
        <li>XBRL tagging quality varies by company; segment and KPI detail comes from press-release extraction, not company facts.</li>
        <li>Only companies that publish quantitative guidance in their 8-K are coverable — that constraint shaped the universe.</li>
      </ul>
      <h2>The family</h2>
      <p>Furton Coverage is the depth complement to <a href="https://furton.ai" target="_blank" rel="noopener">Furton Research</a> (a systematic 30-name Dow screen run by a simulated investment committee) and a sibling of <a href="https://nick-furton.github.io/form-d-radar/" target="_blank" rel="noopener">Form D Radar</a> (a private-markets tracker). All three run on the same free SEC EDGAR spine.</p>
    </article>
  </div>
</section>
"""
    write_page(
        "about.html",
        render_page(
            base,
            title="Methodology · Furton Coverage",
            description="How Furton Coverage works: the SEC EDGAR data spine, the T−1/T+0/T+2 note cadence, deterministic grading against written guidance, and honest limitations.",
            content=content,
            root="",
            active="about",
            build_stamp=stamp,
        ),
    )


# ---------------------------------------------------------------------- assets

def clean_docs() -> None:
    """Remove previously generated output so renamed/deleted inputs can't leave
    stale pages live on Pages. Only the paths this script generates are removed;
    anything else (e.g. a future CNAME, .gitkeep) is preserved."""
    if not DOCS.is_dir():
        return
    for sub in ("assets", "notes", "tickers", "models"):
        shutil.rmtree(DOCS / sub, ignore_errors=True)
    for f in DOCS.glob("*.html"):
        f.unlink()


def copy_assets() -> None:
    assets = DOCS / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    css = SITE_SRC / "style.css"
    if not css.is_file():
        raise BuildError("site_src/style.css missing")
    shutil.copy2(css, assets / "style.css")
    # GitHub Pages: serve files/dirs starting with underscore too, skip Jekyll
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")


def copy_models(roster) -> None:
    for u in roster:
        src = MODELS_DIR / u["ticker"]
        if not src.is_dir():
            continue
        for x in src.glob("*.xlsx"):
            dest = DOCS / "models" / u["ticker"] / x.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(x, dest)


# ------------------------------------------------------------------------ main

def main() -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    base = load_base()
    roster = load_universe()
    calendar = load_calendar()
    summary = load_summary()
    notes = load_notes()
    notes.sort(key=lambda x: str(x["fm"]["published_at"]), reverse=True)
    calls = load_shards("calls")
    guidance = load_shards("guidance")

    clean_docs()
    DOCS.mkdir(exist_ok=True)
    copy_assets()
    copy_models(roster)
    build_home(base, stamp, roster, calendar, summary, notes)
    build_research(base, stamp, notes)
    build_scorecard(base, stamp, summary)
    build_ticker_pages(base, stamp, roster, calendar, summary, notes, calls, guidance)
    build_note_pages(base, stamp, notes)
    build_about(base, stamp)

    n_pages = 4 + len(roster) + len(notes)
    print(f"built {n_pages} pages -> docs/ ({len(notes)} notes, {len(roster)} tickers)")


if __name__ == "__main__":
    main()
