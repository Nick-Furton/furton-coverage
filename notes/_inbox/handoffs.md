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
