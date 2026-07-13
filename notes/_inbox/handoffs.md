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

## [S4] Scorecard engine — 2026-07-08

**Did:** Built the scorecard layer end-to-end. `scorecard/SCHEMA.md` defines the two
per-ticker sharded stores `scorecard/calls/<TICKER>.jsonl` (our calls) and
`scorecard/guidance/<TICKER>.jsonl` (management guidance vs actuals); every entry is
timestamped and carries `basis` (gaap|non_gaap), calls carry `source_note`, guidance
carries `source_filing` (the 8-K URL). `scripts/score.py` reads ALL shards and writes
`scorecard/summary.json`: our hit rate by call_type / metric / period, guidance
beat/met/missed, a confidence calibration curve, per-ticker + aggregate rollups.
**Grading is deterministic (no LLM)** — `grade_call`/`grade_guidance` compare vs actual
in code. **§3 GAAP trap enforced:** `_check_basis` raises `BasisMismatchError` on any
cross-basis compare (non_gaap call vs gaap actual), never silently scores. Fail-loud
(`MalformedRecordError`) on missing/ill-typed fields, invalid basis, unknown kind,
non-finite numbers, malformed *pending* calls, mis-sharded records, and duplicate ids.
`tests/test_score.py` = 46 cases (beat/met/miss, basis-mismatch refusal, malformed
input); **full `pytest` 67 green** (with S2's edgar tests). Ran `/code-review` (medium),
applied the confirmed fixes. Seeded 5-ticker dummy shards (`"dummy": true`, real
universe numbers: AMZN/DE gaap, NVDA/AMD/CRWD non_gaap) + a generated `summary.json` so
S5 can build the site now; `--exclude-dummy` drops them.

**Unfinished / next:** nothing blocking in S4's scope. Merge Gate 2 wire-check is the
next step (needs S3): confirm S3's note frontmatter carries the fields score.py grades on.

**Next session (esp. S3 + Merge Gate 2) must know:**
- **The call schema is the contract.** For a numeric call to be gradable, S3's note
  frontmatter must emit a `scorecard/calls/<TICKER>.jsonl` record with: `id, ticker,
  timestamp, call_type (preview|flash|review|initiation), period (e.g. FY2026Q3),
  metric, unit, basis, source_note`, and a `call` object of kind `direction`
  (value beat|met|miss + `benchmark` band), `range` (low/high), `point` (value/tolerance),
  or `qualitative`. See `scorecard/SCHEMA.md` for the full table + examples.
- **basis MUST match between a call and its `actual`** or score.py raises — S3/S7 must pull
  the grading actual from the 8-K press release (company's own basis), not companyfacts
  (GAAP). AMZN & DE guide GAAP; the other 8 roster names non-GAAP (universe.json).
- **`actual` is filled when the print lands** (flash/review appends it to the record);
  until then the call is `pending` and excluded from hit-rate denominators. Add `confidence`
  (0..1) to calls to populate the calibration curve. `higher_is_better:false` for
  cost/capex/opex metrics so beat/met/miss labels stay correct.
- **ids must be unique** (a correction is a NEW dated record, never a rewrite) — score.py
  fails loud on a duplicate id across shards. Filename ticker must equal the record ticker.
- Run `py scripts/score.py` (set PYTHONUTF8=1) to regenerate summary.json; `--selftest`
  is a quick smoke of the grading core. Merge Gate 3 deletes the dummy rows.

## [S3] Note templates, build_model.py, publish gate, /preview /flash /review, CRWD backtest — 2026-07-09

**Did:** Designed `notes/_templates/{preview,flash,review,SCHEMA}.md` — frontmatter is
byte-shape-identical to S4's `scorecard/{calls,guidance}` records (answers S4's Merge
Gate 2 ask directly: every required field score.py grades on is present). Wrote
`scripts/build_model.py`: pulls companyfacts via edgar.py, builds a 4-tab Excel model
(Cover/Income Statement/KPIs/Our Estimates), anchoring every Income Statement row to
Revenue's period-end set so a metric whose tag went stale (DE's GrossProfit/
OperatingIncomeLoss) renders blank instead of silently misaligned old data — caught this
by testing against DE and AMZN, not just CRWD. Built `.claude/skills/{preview,flash,
review}/` + `_shared/{note_pipeline.md,fact_check_workflow.js}` — the shared publish-gate
Workflow script fans out one agent per numeric claim (re-fetches the cited EDGAR doc) and
one refutation pass per qualitative call. Ran the full pipeline as a real backtest on
CRWD's actual Q1 FY27 print (preview drafted from only pre-print info — the prior 8-K +
trailing XBRL — then flash/review from the real 8-K + 10-Q), and ran the actual publish
gate (Workflow tool, live WebFetch) against all three notes as its first real test.

**The gate caught two genuine issues** (not just theoretical): a review-note qualitative
call cited only one filing to support a claim that really needed two (a cross-document
sequential comparison), and a flash-note prose figure had no frontmatter record to trace
to. Both fixed in the notes. **Also surfaced an infra quirk to watch for:** under
parallel load, at least 2 of ~16 WebFetch-based verifier agents received content from a
DIFFERENT CRWD filing than the URL they were given (same failure mode both times — an
agent's "evidence quote" was verbatim from a different accession's document). Confirmed
via isolated (non-parallel) single-agent re-checks that the original claims were correct
in both cases. **If a future gate run shows a fail whose evidence_quote doesn't match the
cited document's actual content/dateline, suspect this before trusting the fail** — re-run
that one claim in isolation before cutting real content from a note.

Ran `/code-review` (medium) on the full diff: 13 findings, all fixed — a hardcoded `<CIK10>`
placeholder shipped in every model's footnote, `--kpi-overrides` silently dropping data on
a ticker/metric-name mismatch, a missing fail-loud guard for a ticker whose Revenue tag is
itself empty, two dead functions, an overclaiming docstring, and three doc-only schema
ambiguities (`call_type` persistence across notes, `published_at` for backtests, `actual`
on qualitative calls). `pytest` 67 green throughout (untouched — didn't touch edgar.py/
score.py/tests/). Did NOT touch `scorecard/` or `score.py`.

**Unfinished / for the gate:** Backtest notes' `calls:`/`guidance:` are NOT yet appended
into `scorecard/calls|guidance/CRWD.jsonl` — that's explicitly Session 6/7's job per their
kickoff (extraction from notes into shards). **One gotcha for whoever wires that:** a
preview call and its later flash grading share one `id` on purpose (same call, `actual`
added later) — extract each `id` exactly once, from whichever note first resolves it, or
score.py's `_assert_unique_ids` raises the moment both get appended. Documented in
`.claude/skills/_shared/note_pipeline.md`'s "Not yet wired" section.

**Next session must know:**
- **Merge Gate 2 wire-check should now pass:** notes/_templates/SCHEMA.md's `calls:`/
  `guidance:` shapes were built directly against scorecard/SCHEMA.md's field list (id,
  ticker, timestamp, call_type, period, metric, unit, basis, source_note/source_filing,
  call, actual, higher_is_better, confidence, rationale) — verified by hand, not just by
  intent. `basis`/`higher_is_better` are present on every CRWD backtest record.
- **build_model.py works for any resolvable ticker**, not just the frozen 10 — tested
  live against CRWD, AMZN, and DE. `--kpi-overrides <json>` is the mechanism for
  press-release-sourced KPIs (never fabricated; TBD/yellow-flagged otherwise, with a
  loud warning if an override's `metric` string doesn't match universe.json).
- **Skipped skill-creator's full eval/benchmark harness** (parallel subagent test runs +
  browser viewer) as disproportionate for these internal, deterministic-pipeline
  commands — the real backtest + live publish-gate run served as the actual validation.
  Flagging in case a later session wants to run that harness anyway for triggering-
  accuracy tuning (the SKILL.md descriptions haven't been eval-optimized).
- **A concurrent session (not S3) has an in-progress, uncommitted addition to CLAUDE.md**
  (a cross-project status-board section referencing `..\status-dashboard.html`) sitting
  in the shared working tree as of this handoff — I did not commit, stage, or touch it
  (stashed and restored it cleanly to run my own `git pull --rebase`). Whoever owns that
  work should commit it themselves.
- `requirements.txt` (repo root) is new — added `openpyxl` (build_model.py's dependency)
  alongside `pytest`/`ruff`. No LibreOffice on this machine, so `build_model.py` can't run
  `scripts/recalc.py`-style formula recalculation; it does its own pure-Python data/
  div-by-zero self-check instead (documented limitation — open the .xlsx in Excel to
  confirm formulas compute, don't just trust the build-time check for cell references).

## [Merge Gate 2] Phase 2 closed — 2026-07-11 (run by S4, solo)

**Did:** Ran Merge Gate 2 end to end. (1) **Wire-check GREEN** — extracted the real CRWD
backtest notes' `calls:`/`guidance:` frontmatter and round-tripped every record through
score.py (validate + grade); grades match the flash note's own table (revenue HIT, EPS
HIT, ARR MISS), every call carries `source_note`, every guidance carries `source_filing`,
every record carries `basis`, the basis guard raises on a crossed-basis actual, and
compute_summary rolls up with no duplicate-id error. (2) **pytest 67 green** (edgar + score
suites). (3) **`/code-review` (medium)** over the combined S3+S4 phase diff (2 finder
lenses: build_model correctness + S3↔S4 integration).

**Fixed at the gate (low-risk, scorecard-contract doc/template edits):**
- `higher_is_better` caveat added to all three note templates + note SCHEMA.md — a
  cost/capex/opex call left at the default `true` would invert score.py's beat/miss.
- Flash template now carries `confidence:` forward when it copies a preview call (and
  note_pipeline.md's extraction gotcha spells this out) — otherwise the flash copy that
  gets extracted drops confidence and the calibration curve stays empty.
- Note SCHEMA.md now documents the **initiation** note shape (reuse preview frontmatter,
  drop `guidance:`, `call_type: initiation`) so Session 6 isn't blocked.

**Deferred (logged, NOT fixed at the gate):** 5 real `build_model.py` defects (margin
`0.0%`-instead-of-blank, YoY fixed-column offset, 52/53-week period label, provenance
footnote wording, annual-tag abort) → `notes/_inbox/gate2_build_model_followups.md`. They
sit in an untested, live-EDGAR-dependent engine; they touch neither the scorecard nor the
S3↔S4 wire contract, and need a dedicated build_model hardening pass with live validation
**before Session 6 relies on the Excel models**. Dummy scorecard rows kept (deleted at
Gate 3, per plan).

**Next:** Phase 3 is unblocked — Session 5 (site generator) ∥ Session 6 (initiations 1–5).
Standing residual from Gate 1: Nick still needs to run `/fewer-permission-prompts` in an
interactive session. S6 must read `gate2_build_model_followups.md` before trusting model
output, and follow note SCHEMA.md's new initiation section + the unique-id extraction rule
in note_pipeline.md.

## [S5] Site generator & design — 2026-07-11

**Did:** Built `scripts/build_site.py` + `site_src/{base.html,style.css}` → `docs/` (17 pages,
committed + pushed): home (universe grid, next-print countdown, headline stats), per-ticker pages
(note timeline, call record, guidance tracker, Excel-model download), filterable research library,
scorecard page (4 Chart.js charts w/ dataviz-skill-validated palette + accessible table view),
methodology stub, and every note rendered to HTML. Visual language = furton.ai v2's design system
**deliberately verbatim** (Nick's kickoff override of PLAN's "different accent" — the sites may
share a domain); the sibling cue is the cyan favicon mark + "Furton Coverage" wordmark.
`.claude/launch.json` serves docs/ on **8802**; verified with preview tools (structure snapshots,
CSS inspection, mobile 375px, dark-native, filter/countdown interactions, zero console/network
errors). Ran /code-review (8 finder angles) and fixed everything confirmed: grading chips + shard
loading now **delegate to score.py** (no presentation-side re-implementation to drift; build fails
loud on any record score.py rejects), fail-loud calendar/summary/frontmatter validation (all 9
SCHEMA.md fields), markdown hardening (code-span isolation, `javascript:` links neutralized,
fenced blocks, `</script>`-safe JSON), SRI-pinned Chart.js, display-name map (NVIDIA not "Nvidia"),
unit-labeled call targets, stale-`docs/` cleanup each build, ET-anchored countdown, noscript +
aria-pressed a11y. `pytest` 67 green, ruff clean, `pyyaml` added to requirements.txt.

**Unfinished:** Universe prose on home is still hand-written copy (counts/Dow-overlap now derive
from config, but the sector narrative is static — fine until the roster changes). Scorecard/ticker
tables render ONLY dummy shards (real CRWD backtest calls live in note frontmatter until S6/S7
extract them — the site labels every dummy row "sample" + banner, and tiles carry a "sample data"
badge, so Gate 3's dummy deletion will visibly empty the boards until real records land).
`preview_screenshot` times out on this machine this session (tool issue, not the site — pages are
fully interactive; verified via snapshot/inspect/eval instead).

**Next session must know:** `docs/` is fully generated — rebuild with `PYTHONUTF8=1 py
scripts/build_site.py` after ANY notes/scorecard/models/config change; the build DELETES generated
docs/ subtrees first (preserves .gitkeep/CNAME/unknown files). It fails loud by design on: notes
missing any of the 9 required frontmatter fields, shard records score.py rejects (incl. duplicate
ids), model files not named `<TICKER>_model_<YYYY-MM-DD>.xlsx`, non-YYYY-MM-DD calendar dates,
unterminated ``` fences — if S6's initiation notes break the build, the note (not the generator)
is almost certainly violating SCHEMA.md. score.py is imported by the generator; if S8+ changes
score.py's grading API (grade_call/grade_guidance/load_all_* signatures), build_site.py must
follow. Chart.js is SRI-pinned to 4.4.3 — bumping the CDN version requires recomputing the hash
in CHARTJS_SRI. Site preview: launch config "coverage-site" (port 8802) in THIS repo's
.claude/launch.json (a duplicate entry also sits in Furton Research's gitignored launch.json
because preview tools read the primary session dir).

## [S6] Initiations batch 1 (AMD/AMZN/AVGO/CRM/CRWD) — 2026-07-11

**Did:** Initiated the first 5 tickers alphabetically from the frozen 10
(`notes/<TICKER>/2026-07-11_initiation.md`, `models/<TICKER>/<TICKER>_model_2026-07-11.xlsx`,
`scorecard/calls/<TICKER>.jsonl`), each sourced from that ticker's latest 10-K (business/
segment narrative + MD&A) plus its most recent earnings 8-K (EX-99.1, for current-quarter
actuals and next-quarter/full-year guidance) via `edgar.py`. Each note carries 2 forward
numeric calls (graded against the company's own next-print guidance) + 2 forward
qualitative theses, all `call_type: initiation`. Ran the full adversarial fact-check
Workflow gate on every note (per `notes/_templates/SCHEMA.md` §"PUBLISH GATE") — **it
earned its keep**: across the 5 notes it caught a real factual reversal (an AMD call said
Data Center "sustains growth meaningfully above" Client & Gaming when C&G actually grew
faster in FY2025, 51% vs. 32%), a margin-direction error (an AMZN call framed AWS margin
as "continues to expand" when the segment table shows it contracted 37.0%→35.4%), an
annual-vs-quarterly trend confusion (a CRWD call claimed the GAAP operating loss was
"continuing to narrow" citing only a Q1-over-Q1 comparison, when full-year losses actually
widened every year through FY2026), and a self-inflicted data-deletion (a CRM correction
round wrongly removed a real, verified $2.2B Informatica-RPO figure after a false-negative
fact-check pass claimed it didn't exist — restored after directly re-reading the cached
filing text). All were corrected and re-verified; CRM's attrition-rate thesis is published
flagged `verification: unverified` after being refuted twice on purely structural grounds
(an inherently unconfirmable forward bet against the filing's own risk-factor hedging) —
see note_pipeline.md's guidance on directionally-reasonable claims the gate can't settle.
Committed + pushed as 5 separate `[S6]` commits (one per ticker, immediately after each
passed its gate) so S5's site build could pick up real data incrementally. Cleaned up
~30 stray scratch/debris files (`amd10k.htm`, `scratch_*.htm/.txt`, `search*.py`, etc.)
left in the repo root by the Workflow gate's WebFetch-using subagents before each commit —
did not touch `CLAUDE.md` (modified, uncommitted) or `.claude/settings.json` (untracked),
both belonging to a concurrent session.

**Unfinished / for the gate:** CRWD already had a preview/flash/review backtest series
(S3, same Q1 FY2027 print) — this initiation note is deliberately broader/forward-looking
(FY2027 as a whole, not that one quarter) with non-overlapping call ids; Merge Gate 3
reviewers should sanity-check the two note types read as complementary, not redundant, on
the built site. `scorecard/calls/CRWD.jsonl` was **appended to** (not overwritten) since
S4's dummy CRWD rows already lived there — verify `score.py`'s duplicate-id guard stays
green after Gate 3 deletes the dummies (it does; ids don't collide).

**Next session (S7 + Merge Gate 3) must know:**
- **Recurring infra quirk, confirmed again this session:** WebFetch-based verifier agents
  in the fact-check Workflow occasionally return content from a DIFFERENT document than
  the cited URL (e.g. an AMZN net-income claim initially "failed" because the fetch
  returned a TTM-through-Q1-2026 rendering instead of the FY2025 10-K; a CRM RPO figure
  first came back "not in the filing," then a later independent re-check found it verbatim
  in the same URL). Same failure mode S3 flagged at the CRWD backtest. **Before cutting
  content off a failed verdict, grep your own cached raw text (or re-run that one claim in
  isolation) — don't trust a lone fail whose evidence_quote doesn't match the cited
  document's actual dateline/content.**
- **`--kpi-overrides` was NOT used this session** — all 5 initiation notes rely on
  companyfacts headline financials (via `build_model.py`) plus 10-K/8-K-cited prose for
  segment/KPI detail (Data Center, AWS, Semiconductor Solutions, cRPO, ARR — none of which
  are in companyfacts). S7 should follow the same pattern for the guidance backfill unless
  it needs the KPI override mechanism for a specific extracted press-release figure.
- **Model quirks documented per-ticker, not fixed:** AMZN's `GrossProfit` XBRL tag has no
  post-2009 data (blank row, by design); AVGO's FY2024 EPS/GrossProfit/OperatingIncomeLoss
  disagree pre/post its 2024 stock split (model keeps earliest-filed, i.e. pre-split);
  CRWD's Q1-FY2026 figures disagree slightly between two later filings (model keeps
  earliest-filed). None of these are new build_model.py bugs — they're the documented
  anchoring-to-earliest-filed behavior surfacing on real names; see
  `gate2_build_model_followups.md` for the *actual* deferred defects if S7/S8 pick those up.
- **`py scripts/score.py` run after each ticker** — summary.json now reflects real batch-1
  data (26 calls / 8 guidance across 7 tickers as of this handoff, dummy CRWD rows still
  included per plan; Gate 3 deletes them).
- Universe order used (alphabetical, frozen 10): AMD, AMZN, AVGO, CRM, CRWD done this
  session; **S7 owns DE, LLY, MU, NVDA, PANW** for batch 2, plus the guidance backfill.

## [S7] Initiations batch 2 + guidance backfill (all 10 names) — 2026-07-13

**Did:** (1) Initiated the remaining 5 tickers alphabetically — **NVDA, DE, LLY, MU,
PANW** (`notes/<T>/2026-07-13_initiation.md`, `models/<T>/<T>_model_2026-07-13.xlsx`,
`scorecard/calls/<T>.jsonl`), same pattern as S6: each from its latest 10-K (business/
segment/MD&A) + latest earnings 8-K (EX-99.1, current-quarter actuals + forward
guidance), with 2 forward numeric calls (graded vs the company's own next-print guidance)
+ 2 qualitative theses, all `call_type: initiation`. Ran the S3 adversarial fact-check
Workflow gate on every note (13–17 claims each). All 10 universe names now have an
initiation. (2) Backfilled `scorecard/guidance/` for **ALL 10 names** — 74 records from
the last ~5 earnings 8-Ks per name (guidance in quarter N's release, actual in N+1's),
every figure re-verified verbatim against its source release. Committed as 7× `[S7]` per
completed ticker (initiations) + 2× `[S7]` guidance commits; pushed after each.

**The fact-check gate earned its keep again — and the WebFetch wrong-document quirk
(S3/S6) recurred:** DE's ag-cycle qualitative call and two PANW Q3 prose figures "failed"
first pass because verifier agents fetched 10-K content for a cited 8-K URL. All were
FALSE fails — confirmed by (a) parallel claims on the same URL that passed and (b)
isolated single-agent re-runs that fetched the right doc. **One GENUINE fix:** PANW's
FY2025 RPO prose asserted a prior-year "$12.7B (+24%)" comparative not in the cited
FY2025 10-K → removed (kept the sourced $15.8B + ~$7.0B-within-12-months). Details in
each note's `fact_check.notes`. NVDA/LLY/MU passed clean first-pass.

**Next session (S8 + Merge Gate 3) must know:**
- **Guidance backfill is real and complete (74 records, 10 shards).** score.py:
  `beat 59 / met 12 / missed 0 / 3 pending`. The 0-missed / strong-beat skew is the real
  AI+pharma up-cycle over this window (Feb-2025→mid-2026), NOT a bug — but see the caveat.
- **METHODOLOGY CAVEAT for S10's methodology paper (and any "management is always right"
  read of the scorecard):** CRM/CRWD/PANW **non-GAAP EPS guides EXCLUDE strategic-
  investment gains that the reported actuals INCLUDE** (e.g. CRM Q4 FY26 actual $3.81
  includes ~$0.67 of investment gains vs a $3.02–3.04 guide). Both sides are labeled
  "non-GAAP" so score.py's cross-basis guard does not fire — this is a *within-non-GAAP*
  definitional gap that inflates software-name EPS "beats." **Revenue beats are clean.**
  Consider excluding investment gains from the EPS actual, or footnoting it, in the
  methodology. AMD's Q4'25 57% non-GAAP GM is REAL (one-time MI308 reserve release; ex
  that, ~55%).
- **Annual guiders (DE, LLY) yield fewer completed pairs by design** — they guide full-
  year (not next-quarter), so only the completed FY (FY2025) has an actual; the open FY
  (FY2026) is recorded as a `pending` guidance record (no `actual`). DE=2 records, LLY=4.
- **S4 dummy guidance rows fully replaced** (AMD/AMZN/CRWD/NVDA/DE shards overwritten with
  real data). S4 dummy CALL rows still live in `scorecard/calls/{DE,NVDA}.jsonl` alongside
  my real initiation calls (I appended, matching S6's CRWD handling) — **Merge Gate 3
  should delete all remaining `"dummy": true` rows** (calls: DE, NVDA, + S6's AMD/AMZN/
  CRWD/NVDA dummy calls; guidance: none left). `score.py --exclude-dummy` confirms real-
  only totals.
- **Note-drafting + guidance-extraction were parallelized via subagents** (one per ticker;
  each self-verified figures against the cached release text, I re-verified independently
  against `data/raw`-equivalent local dumps and via the fact-check gate). All source docs
  are cached under `data/raw/` (gitignored) — reproducible.
- **build_model quirks surfaced on real names (documented in each note's Model section, not
  fixed — see `gate2_build_model_followups.md`):** NVDA/PANW pre-split EPS retained
  (earliest-filed anchoring; NVDA 10:1 Jun-2024, PANW 2:1 Dec-2024); DE Gross/Operating
  margin rows render a spurious `0.0%` off blank stale-tag cells (gate2 item 1) — flagged
  in the DE note as "ignore the 0.0% margin rows." MU model built clean.
- Universe order (alphabetical 10): S6 did AMD/AMZN/AVGO/CRM/CRWD; **S7 did DE/LLY/MU/NVDA/
  PANW + the full guidance backfill.** Phase 3/4 initiation+backfill work is DONE.
