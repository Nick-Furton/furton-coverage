# EDGAR Data-Spine Report & Universe Validation — Session 2

**Author:** Session 2 (EDGAR data spine) · **Date:** 2026-07-08 · **Status:** for Merge Gate 1

This covers three things the kickoff asked for: (1) the build decision for `scripts/edgar.py`,
(2) two structural EDGAR findings that shape what the desk can and can't do, and (3) the
candidate-universe validation with a recommended final 10.

---

## 1. Build decision: hand-rolled against `data.sec.gov`, not `edgartools`

**Decision: build direct against the SEC REST API (stdlib `urllib` + optional `requests`), do
NOT depend on `edgartools`.** Rationale:

- **Bleeding-edge Python.** This machine runs **Python 3.14.6**. `edgartools` pulls a heavy
  scientific stack (pandas, pyarrow, lxml, …); wheel availability on 3.14 is a real headless-run
  risk for a project whose whole pitch is "runs fully headless on free data." `urllib` is stdlib.
- **The critical logic is bespoke anyway.** The one thing that must not go wrong — picking the
  *Item 2.02 + EX-99.1* earnings 8-K and **failing loud** on ambiguity — is exactly the logic I'd
  have to hand-write and pin with tests regardless of the wrapper. Owning the thin parser makes the
  golden-fixture regression net (the parity feature we were missing vs. Form D Radar) meaningful:
  it pins *our* parse against saved real payloads, not a third-party lib's changing behavior.
- **SEC etiquette is a hard requirement we want to own.** UA-from-settings, ≤10 req/s, backoff,
  and cache-everything-in-`data/raw/` are all enforced in one place (`edgar.py`), rather than bent
  around a library's own identity/caching model.
- The endpoints are stable, documented, plain JSON. There was no heavy lifting to outsource.

`edgartools` remains a fine *optional* accelerator later (same posture as the Daloopa MCP in
PLAN §1) — nothing here is hard to swap. But the spine does not need it.

The module ships with a CLI for by-hand checks (used at the merge gate):
`py scripts/edgar.py cik|facts|earnings8k|docs <TICKER>`.

## 2. Two structural findings that shape the desk

### 2a. companyfacts is headline-only — **segment / product / KPI data is NOT in it**

The XBRL `companyfacts` API returns only the **default (non-dimensional) context** of each concept.
Facts qualified by an axis/member — segment revenue, product revenue, geography — are **excluded**.
Verified on NVDA: companyfacts has **no** Data Center / Gaming revenue, only
`NumberOfReportableSegments`; `Revenues` returns exactly one consolidated value per period.

**Implication for the roster:** every candidate's *headline* financials (revenue, margins, EPS,
net income) with 14–18 years of history are reliably available and are what `build_model.py`
should lean on. But the segment/KPI lines listed in `universe.json` (NVDA Data Center, LLY
Mounjaro/Zepbound, DE segment sales, PANW NGS ARR, etc.) will **not** come from companyfacts. They
have to be extracted from the **8-K press release prose/tables** (the same EX-99.1 workhorse that
carries guidance) or from the financial-statement R-files. This *raises* the importance of the
press-release extraction pipeline (Session 3/7) and should be stated as a methodology limitation.
It does **not** change the guidance verdicts below (guidance is press-release-sourced regardless).

*Not yet built into `edgar.py`:* a dimensional/segment fetcher (would need the frames API or
R-file/`Financial Report` parsing). Flagged for a later session; not required for Phase 1.

### 2b. The earnings press release is **EX-99.1 for most, bare EX-99 for some**

The exhibit **type** (`EX-99.1` vs `EX-99.2` CFO commentary) lives only in the SGML `<DOCUMENT>`
manifest (I read it from `{accn}-index-headers.html`). It is **not** in `index.json` — that file's
`type` field is just a display-icon name (`text.gif`). Anyone matching on `index.json` would grab
the wrong document.

NVDA's earnings 8-K carries **both** EX-99.1 (press release) and EX-99.2 (CFO commentary) — so
matching `EX-99.1` exactly is what avoids the CFO-commentary trap. **But LLY and GE type their
press release as bare `EX-99`** (filenames literally `…lillysalesandearningsp.htm`,
`ge1q2026earningsrelease.htm`). The finder therefore prefers exactly-one `EX-99.1`, falls back to
exactly-one bare `EX-99`, and **fails loud** (`MissingExhibit991` / `AmbiguousExhibit991`) if it
can't land on one — never guesses. This is the wrong-8-K guard PLAN §7 calls out, and it fired
correctly during validation (it's what surfaced the LLY/GE case).

## 3. Candidate-universe validation

For each of Session 1's 15 candidates I pulled companyfacts (richness + history) and the latest
earnings 8-K's EX-99.1/EX-99 press release, then read the actual outlook section to rule guidance
in or out. All 15 resolved with zero fetch/parse failures — the spine handles every name.

**XBRL richness note:** the `us-gaap` concept count is a coarse proxy (all names tag 450–940
headline concepts with 14–18y history — all deep enough). Real KPI/segment depth is *uniformly
unavailable via companyfacts* per §2a, so richness is **not** a differentiator here and did not
drive cuts. Guidance-in-writing and diversification did.

| Ticker | Dow | us-gaap concepts | Headline history | Earnings PR exhibit | **Guidance in the release?** | Basis | Evidence (latest release) |
|---|---|---|---|---|---|---|---|
| NVDA | ✓ | 626 | 17y | EX-99.1 | **guidable** | non-GAAP | "Outlook … Revenue expected to be **$91.0B ±2%**; GAAP/non-GAAP gross margins 74.9%/75.0%; opex ~$8.5B/$8.3B" |
| MU | — | 629 | 17y | EX-99.1 | **guidable** | non-GAAP | "Business Outlook" table: FQ4 revenue **$50.0B ±$1.0B**, GM ~86%, diluted EPS $30.73/$31.00 (GAAP/non-GAAP) |
| CRM | ✓ | 690 | 17y | EX-99.1 | **guidable** | non-GAAP | "full year FY27 revenue **$45.9–46.2B**"; GAAP & non-GAAP op-margin; OCF/FCF growth; cRPO |
| ORCL | — | 535 | 17y | EX-99.1 | **guidable** | non-GAAP | "for fiscal 2027 we confirm prior revenue guidance of **$90B** and raise non-GAAP **EPS guidance to $8.05**" |
| PANW | — | 507 | 14y | EX-99.1 | **guidable** | non-GAAP | Q4+FY: NGS ARR **$8.90–8.95B**, total revenue $3.345–3.355B, non-GAAP EPS $0.96–0.98 |
| NFLX | — | 490 | 18y | EX-99.1 | **guidable** | GAAP | "full year 2026 … revenue of **$50.7B–$51.7B** (12–14% growth)"; guides op-margin & EPS |
| META | — | 456 | 15y | EX-99.1 | **guidable** | GAAP | "Q2 2026 total revenue **$58–61B**"; "full year 2026 total expenses $162–169B"; capex range |
| LLY | — | 548 | 18y | **EX-99** | **guidable** | non-GAAP | "2026 full-year revenue guidance **$82.0–85.0B** and non-GAAP EPS **$35.50–37.00**" |
| ISRG | — | 577 | 18y | EX-99.1 | **guidable** | non-GAAP | "2026 Financial Outlook … da Vinci **procedure growth 13.5–15.5%**, non-GAAP GM 67.5–68.5%" |
| UNH | ✓ | 573 | 18y | EX-99.1 | **guidable** | non-GAAP | "expects full year 2026 **adjusted net earnings of greater than $18.25/share**" |
| DE | — | 662 | 18y | EX-99.1 | **guidable** | GAAP | "Outlook for Fiscal 2026 … net income **forecasted $4.5–5.0B**" (clean GAAP $ range) |
| GE | — | 941 | 18y* | **EX-99** | **guidable** | non-GAAP | "Total Company Results & Guidance" (Adj EPS/FCF); "holding full-year guidance, trending to high-end" |
| SBUX | — | 557 | 18y | EX-99.1 | **guidable** | non-GAAP | "**Raises** FY2026 Guidance for **comp store sales growth (5.0%+)** and non-GAAP EPS" |
| PEP | — | 611 | 18y | EX-99.1 | **guidable** | non-GAAP | "organic revenue growth **4–6%** and core EPS growth ~**5–7%** in fiscal 2026" |
| **V** | ✓ | 625 | 18y | EX-99.1 | **CALL-ONLY** | (n/a) | **No guidance section.** Every "expects/outlook" hit is safe-harbor boilerplate; net-revenue/EPS-growth outlook is given verbally on the call. |

\* GE = post-spin **GE Aerospace**; companyfacts spans the legacy conglomerate pre-2024, so its
history has a **continuity break** — the model must treat pre-2024 with care (Session 1's flag,
confirmed as a real caveat).

**Verdict tally:** 14 **guidable** (quantitative forward numbers, on a stated basis, in the written
release) · 1 **call-only** (V) · 0 pure no-guidance. The universe Session 1 assembled is strong —
almost everything guides in writing. Notable corrections to the priors: **ORCL** was flagged
"verify" but *does* put full-year revenue + non-GAAP EPS in the release (guidable); **SBUX** was
flagged for its FY2025 guidance suspension but has **resumed** and in fact *raised* guidance
(guidable); **V** is the only genuine call-only casualty.

## 4. Recommended final 10

Hard constraints: **cut V** (call-only ⇒ ungradeable; PLAN Merge Gate 1 says reject call-only unless
deliberately accepted — I do not recommend accepting it). That also fixes the Dow-overlap cap: the
remaining Dow members are **NVDA, CRM, UNH = exactly 3** (≤3 ✅). Five names must be cut from 15;
one (V) is forced, the other four are diversification calls among all-guidable names.

**Recommended roster (10):**

1. **NVDA** — semis; the reference KPI-rich name, multi-line written guidance; marquee Furton
   Research cross-compare (allowed Dow overlap #1).
2. **MU** — memory semis; only clean **Mar/Jun/Sep/Dec** reporter in the set (fills the calendar
   gap the Dec-FY crowd leaves) and prints a full GAAP+non-GAAP guidance table.
3. **CRM** — enterprise software; textbook full-year revenue/margin/cRPO guidance (Dow overlap #2).
4. **PANW** — cybersecurity; unusually rich guide (NGS ARR, RPO, revenue, EPS); July FY staggers.
5. **NFLX** — streaming/media; clean revenue/op-margin/EPS guidance in the 8-K shareholder letter.
6. **META** — mega-cap advertising; rare guided total-revenue **and** expense **and** capex ranges.
7. **LLY** — pharma; full-year revenue + non-GAAP EPS guidance; GLP-1 franchise (healthcare anchor).
8. **ISRG** — med-device; distinctive **procedure-growth %** KPI is explicitly guided — a
   non-financial number to grade that nobody else in the set offers.
9. **UNH** — managed care; reaffirm/raise adjusted-EPS cadence, very gradable (Dow overlap #3).
10. **DE** — industrials/ag; guides **full-year net income as a GAAP $ range** — the cleanest,
    least-basis-ambiguous number to grade in the whole universe; Oct FY staggers.

**Cut (5):** V (forced — call-only), plus **ORCL, GE, SBUX, PEP** on diversification/quality:
- **ORCL** — enterprise-SW slot already held by CRM (richer written guide); Oracle's RPO is
  distorted by a few mega AI contracts and much of its quarterly color is call-driven.
- **GE** — strong, but the post-spin XBRL continuity break complicates the model, and aerospace
  overlaps industrials (DE), which has cleaner data + a plain GAAP number.
- **SBUX** — guidance only just un-suspended; thinner track record for a day-one accuracy scorecard.
- **PEP** — solid defensive name but the lowest-variance guide; marginal on KPI interest.

**Top alternates, in order: GE, PEP, ORCL, SBUX.**

⚠️ **One judgment call for Nick:** the recommended 10 is **tech-heavy (6/10: NVDA, MU, CRM, PANW,
NFLX, META)** and has no consumer-staples ballast. If you want a defensive sleeve, the clean swap is
**PEP in for MU** — you lose MU's off-calendar Mar/Jun/Sep/Dec stagger but gain non-cyclical
diversification. I lean toward keeping MU (the calendar stagger is genuinely useful for a small
desk and memory is its own cycle), but this is exactly the kind of call the gate exists to make.

## 5. Merge-gate checklist (for whoever runs Gate 1)

- [ ] Pick the final 10; set `candidate:false` on the 5 cuts in `config/universe.json` (Session 1's file).
- [ ] Set each survivor's `guidance_status` to `guidable` (all 10 recommended are); if you keep any
      call-only name, set `call-only` and add a dated note accepting it as ungradeable.
- [ ] **Re-confirm Dow flags against the live Dow 30** (not an EDGAR fact — use web). Session 1
      flagged NVDA/CRM/UNH/V as Dow; cutting V leaves 3, at the cap. All four are long-standing Dow
      members by general knowledge, but confirm (rosters shift — cf. the GOOGL↔VZ swap 2026-06-29).
- [ ] Confirm `basis` per name matches the table above — note NFLX/META/**DE are GAAP-basis**
      guides, the rest non-GAAP. score.py's refuse-to-cross-bases rule depends on this being right.
- [ ] Run `refresh_calendar.py` on the frozen roster; sanity-check 2 names by hand with
      `py scripts/edgar.py earnings8k <T>` (does it find the right Item-2.02 + EX-99.1/EX-99?).
- [ ] Freeze the universe (changes thereafter need a dated note).

## 6. Notes for downstream sessions

- **`config/settings.json` keys `edgar.py` reads** (all optional; safe mandated defaults if the file
  is absent): `sec_user_agent` (default `Furton Coverage nicholas@furton.com`),
  `rate_limit_per_sec` (10), `max_retries` (5), `paths.raw_cache` (`data/raw`). Session 1: if your
  schema differs, either rename to these or tell me and I'll widen the reader.
- **Caching & freshness:** every fetch is cached under `data/raw/` and reused. On **print day**,
  pass `force=True` to `earnings_8k(...)` / `submissions(...)` so a fresh 8-K isn't served stale.
- **`recent`-only:** the 8-K finder reads `submissions.filings.recent` (~1y+/1000 filings), ample
  for ~4 earnings 8-Ks/yr. Deep backfill (>~1y, Session 7's 4-quarter history) may need the
  paginated `filings.files` shards — not yet wired; flagged.
- **Public API surface:** `resolve_cik`, `companyfacts`, `concept_series`, `named_metric`
  (+ `REVENUE_TAGS`/`EPS_DILUTED_TAGS`/… fallback lists), `latest_fact`, `metric_history`,
  `submissions`, `find_earnings_8k_filings`, `earnings_8k`, `press_release_text`, `html_to_text`.
- **Tests:** `py -m pytest tests/` (21 golden-fixture tests, offline, ~0.1s) — the drift net.
