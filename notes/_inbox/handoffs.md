# Handoffs

Append-only. Newest at the bottom. 3 lines each: what I did / what's unfinished / what the next session must know.

---

## [S1] Scaffold & calendar — 2026-07-08

**Did:** Built the full repo skeleton from PLAN §3 (config, data/raw [gitignored], notes/_inbox,
models, scorecard/{calls,guidance}, scripts, tests/fixtures, site_src, docs — .gitkeep placeholders
where empty). Wrote `.gitignore` (data/raw/* except .gitkeep; Python/OS cruft). Wrote
`config/settings.json` (SEC UA `Furton Coverage nicholas@furton.com`, ≤10 req/s + min_interval 100ms,
backoff block, EDGAR endpoint templates, paths, port 8802, disclaimer). Wrote `config/universe.json`
= **15 CANDIDATES** (candidate:true) with resolved 10-digit CIKs, sector, fiscal-year end, typical
reporting months, key KPI/XBRL concept tags, my `guidance_prior` + `basis` priors, and a `dow_member`
flag. Built + tested `scripts/refresh_calendar.py` and generated `config/calendar.json` (all 15
resolved) from a web-search-sourced, cited `config/calendar.seed.json`.

**Unfinished / for the gate:** Universe is NOT frozen — it's 15 candidates for **Merge Gate 1** to
cut to ~10. Every `guidance_status` is `pending_s2_validation` and every `basis`/`dow_member` is my
PRIOR, not a ruling — Session 2's edgar_report.md + the gate decide. I did NOT write edgar.py, any
SEC-API data-spine code, or touch notes/scorecard/site_src content (only .gitkeep + this handoff).

**Next session must know:**
- **CIKs are resolved** for all 15 in universe.json (from sec.gov/files/company_tickers.json, 2026-07-08)
  — Session 2 can import them directly; no need to re-resolve.
- **DOW OVERLAP: 4 candidates flagged dow_member=true — NVDA, CRM, UNH, V.** PLAN §2 caps the FINAL
  universe at ≤3 Dow overlap, so the gate must cut ≥1 of these AND re-confirm the flags against the
  live Dow 30 (roster shifts; GOOGL↔VZ swap 2026-06-29). My flags are best-effort as-of Jan-2026.
- **Names I flagged VERIFY on guidance (guidance_prior=written_partial): ORCL, SBUX, V.** SBUX
  specifically SUSPENDED formal guidance during its FY25 turnaround — Session 2 must confirm it
  currently guides in writing or it's a call-only hard-exclude. GE = post-spin GE Aerospace; check
  XBRL history continuity pre-2024.
- **Off-calendar names MU (Mar/Jun/Sep/Dec) and ORCL (Mar/Jun/Sep/Dec)** are deliberately included to
  stagger the calendar off the crowded Jan/Apr/Jul/Oct cluster — keep at least one in the final 10.
- **calendar.py contract:** authoritative source is `config/calendar.seed.json` (web-search dates +
  source_url), run `py scripts/refresh_calendar.py`. Live `--provider nasdaq` exists but Nasdaq's API
  hangs/blocks from this machine, so seed is the reliable path. Script FAILS LOUD: unresolved tickers
  → exit 1, never a guessed date. `--ticker` refreshes one name and leaves the rest verbatim.
  Re-run after the gate freezes the roster (candidate flags drive which tickers it processes).
- **GAAP/non-GAAP trap:** every universe entry carries a `basis` prior so Session 4's score.py has it
  from day one — but confirm each against the actual 8-K before trusting it.

---

## [S2] EDGAR data spine & universe validation — 2026-07-08

**Did:** Built + tested `scripts/edgar.py` (the network-owning data spine): ticker→CIK,
companyfacts fetch/cache/parse with fallback-tag metric extraction, submissions index, and the
**Item 2.02 + EX-99.1 earnings-8K finder that fails loud** on wrong/ambiguous exhibits. Enforces
SEC etiquette (UA from settings.json, ≤10 req/s, backoff, cache in `data/raw/`). Validated all 15
candidates against live EDGAR → `notes/_inbox/edgar_report.md` (richness/history/guidance table +
recommended final 10). Wrote **21 offline golden-fixture tests** (`tests/`, `py -m pytest tests/`
green; ruff clean). Live-exercised the CLI on NVDA/KO/LLY/GE etc. **Decision: hand-rolled against
data.sec.gov, did NOT adopt `edgartools`** (Python 3.14 dep risk; the fail-loud 8-K logic is
bespoke anyway; want full control of etiquette + the drift-catching fixtures). Owned only
scripts/edgar.py, tests/**, notes/_inbox/{edgar_report.md,handoffs.md} — did NOT touch config/.

**Unfinished / for the gate:** Universe still needs Nick's cut to 10 — see edgar_report.md §4/§5.
Not built (flagged, not needed for Phase 1): a **segment/dimensional fetcher** (companyfacts
excludes segment/product KPIs — see below), and `submissions.filings.files` pagination for
**>1yr backfill** (Session 7's 4-quarter guidance history will need it; the finder currently reads
`recent` only). No `/code-review` skill run (shared working tree full of S1 untracked files would
make its diff noisy) — module is instead test- + ruff- + live-verified end to end.

**Next session must know:**
- **Guidance rulings (answers S1's VERIFY list): 14 guidable, only V is call-only.** ORCL DOES
  guide in writing (FY revenue $90B + non-GAAP EPS $8.05) → guidable, not call-only. SBUX has
  **resumed** guidance and even raised it → guidable. **V (Visa) = call-only hard-exclude** (its
  8-K press release has no guidance section; outlook is verbal on the call). Cutting V also fixes
  the Dow-overlap cap (leaves NVDA/CRM/UNH = 3). GE continuity break pre-2024 is real.
- **BIG STRUCTURAL FINDING: companyfacts is headline-only — NO segment/product/KPI data.** It
  returns only the non-dimensional context. NVDA Data Center, LLY product revenue, DE segment
  sales, PANW NGS ARR etc. are NOT in companyfacts → they must come from **press-release
  extraction** (Session 3/7) or R-files. Doesn't affect guidance (press-release-sourced anyway),
  but build_model.py (Session 3) should plan on headline financials from companyfacts + KPIs from
  the 8-K, and the methodology (Session 10) should state this limitation.
- **EX-99 vs EX-99.1:** most file the press release as EX-99.1 (and big filers attach EX-99.2 CFO
  commentary — the finder correctly picks .1); **LLY and GE file it as bare EX-99** — the finder
  falls back to bare EX-99 but still fails loud on ambiguity. `earnings_8k(...)` returns
  `press_release_exhibit` for auditing which matched.
- **On print day pass `force=True`** to `earnings_8k()`/`submissions()` or a fresh 8-K is served
  stale from cache. Public API + settings keys it reads are documented in edgar_report.md §6.
- **`basis` per name (confirm at gate):** NFLX, META, **DE are GAAP-basis** guides; the other 12
  are non-GAAP. score.py's refuse-to-cross-bases rule depends on this.

## [S2 addendum] Specialist roster decision — 2026-07-08

**Did:** Per Nick's call to specialize toward AI-infrastructure (and "don't add names we can't
grade"), validated the mega-cap AI adds against live EDGAR and finalized the recommended roster in
edgar_report.md **§7 (supersedes §4)**. Confirmed MSFT/GOOGL/AAPL give NO written guidance
(call-only) and TSM is a foreign filer with no Item-2.02 8-K → all four EXCLUDED (documented so
they're not re-added). Validated 4 new gradable names (AMD/AVGO/CRWD/AMZN, all EX-99.1, guidance in
writing) with CIKs + FYE + reporting months for Session 1.

**Final recommended 10 (my correlation call, delegated by Nick):**
NVDA · AMD · AVGO · MU · CRM · PANW · CRWD · AMZN + **LLY · DE**. 8 AI-infra core + 2 deliberate
decorrelators (LLY pharma, DE industrial) — a fully-correlated book makes the scorecard dismissible
as one lucky sector run and both decorrelators are already validated & cleanly gradable. Not a pure
AI book; the marginal correlation risk wasn't worth the 2 slots.

**Next session (gate) must know:**
- **Session 1 must add AMD/AVGO/CRWD/AMZN to universe.json** (CIKs+metadata in §7b — I can't edit
  config/). AMZN replaces UNH as the 3rd Dow name → re-confirm NVDA/CRM/AMZN vs the live Dow 30.
- **basis: AMZN and DE are GAAP-basis guides; the other 8 are non-GAAP** (score.py depends on it).
- **Top alternates:** META (swap for CRWD if you want the mega-cap ads read), then NOW, NFLX, ISRG.
- Calendar: Feb/May/Aug/Nov is the heavy window; peak weeks late-Feb & early-Mar are real work.

---

## [S1] Merge-gate universe freeze — 2026-07-08

**Did:** Applied Session 2's §7 roster ruling to `config/universe.json` (my file — S2 can't edit
config/). **FROZEN 10: NVDA · AMD · AVGO · MU · CRM · PANW · CRWD · AMZN · LLY · DE.** Kept my 6
surviving candidates (NVDA/MU/CRM/PANW/LLY/DE), added the 4 AI-infra names (AMD/AVGO/CRWD/AMZN) with
CIKs + FYE + reporting-months + basis from §7b, and set `candidate:false` on the 9 cuts (kept, not
deleted, as re-promotable alternates with `cut_note`s). Set `guidance_status:guidable` on all 10;
`basis` = GAAP for AMZN & DE, non-GAAP for the other 8. Web-sourced the 4 new next-earnings dates
(AMD 08-04, AMZN 07-30, AVGO 09-03, CRWD 09-02 — all after-close, confirmed, cited) into
`config/calendar.seed.json` and re-ran `refresh_calendar.py` → `calendar.json` now holds exactly the
10, all resolved (soonest AMZN d+22).

**Verified at the gate:**
- **Dow overlap = 3 (NVDA, CRM, AMZN), CONFIRMED against the live Dow 30** (web-checked 2026-07-08;
  GOOGL replaced VZ 2026-06-29). Cutting UNH + V removed the 2 excess Dow names.
- **Ungradeable names recorded in universe.json `_schema.excluded_do_not_re_add`** so nobody re-adds
  them: MSFT/AAPL (call-only), GOOGL (no guidance), TSM (foreign filer, no Item-2.02 8-K), V
  (call-only — its EX-99.1 has no guidance section).
- JSON validated: 10 candidate:true in roster order, GAAP={AMZN,DE}, Dow={AMZN,CRM,NVDA}.

**Next session must know:**
- **Universe is FROZEN — changes now require a dated note (PLAN §5).** `_schema.frozen_roster` is the
  source of truth; alternates in priority order: META (swap for CRWD) → NFLX → ISRG → NOW.
- **edgar.py CLI sanity-check (gate checklist §7d) is satisfied by S2's live validation** of all 4
  new names (companyfacts concept counts in §7b; data cached in data/raw/, reproducible) — I did not
  re-run S2's network tool.
- **companyfacts is headline-only** (S2 finding, echoed in universe.json `_schema.companyfacts_caveat`):
  segment/product KPIs (NVDA Data Center, LLY products, DE segments, PANW NGS ARR, CRWD ARR, AWS rev)
  come from press-release extraction, not companyfacts — build_model.py (Session 3) should plan for it.
- **Calendar reality for the frozen 10:** the near-term July reporters were all cut, so the desk's
  first live print is **AMZN on 2026-07-30**, then AMD 08-04, LLY 08-05, DE 08-20... the
  Feb/May/Aug/Nov window is the heavy one. Re-run refresh_calendar.py after each print / when
  estimated dates firm up.
