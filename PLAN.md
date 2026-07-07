# Furton Coverage — Build Plan

An automated sell-side-style earnings desk covering ~10 public companies, built almost entirely
with Claude Code and the Daloopa plugin. Companion project to Furton Research (furton.ai).

Working directory: `C:\Users\Nicholas Furton\Downloads\Miscellaneous Projects\Furton Coverage`

---

## 1. Mission & Goals

**Mission:** Run a real research-desk cadence on a fixed coverage universe — pre-earnings note the
night before, earnings flash within hours of the print, full review after the call — and publish
everything (notes, Excel models, and a public accuracy scorecard) on a dashboard-styled website.

**Goals, in priority order:**

1. **Depth complement to Furton Research.** Furton Research screens 30 Dow names shallowly and
   systematically; Furton Coverage knows ~10 names cold. Resume line target:
   *"Built and operated an automated earnings-coverage desk (pre-earnings notes, same-day flashes,
   guidance-accuracy tracking) across 10 companies for N consecutive quarters."*
2. **Public accountability.** Every call is timestamped and scored. A guidance tracker scores
   *management's* accuracy; a call log scores *ours*. Both are rendered on the site — this is the
   differentiator vs. every "AI writes stock reports" project.
3. **Tangible artifacts.** Downloadable research notes (HTML/PDF) and Excel models per name —
   proof of financial-modeling literacy for VC-club and recruiting conversations.
4. **Heavy use of the new toolkit:** Daloopa MCP + its 20 analyst skills, scheduled agents,
   Workflow fan-outs, docx/xlsx skills, dataviz, design skills.
5. **(Nice-to-have) Revenue:** cross-post flashes/digests to a Substack once the cadence is proven.

**Explicit non-goals:** live trading, price targets marketed as advice, covering more than ~12
names, real-time intraday anything.

---

## 2. Prerequisites — Nick, one-time, before Phase 1

These block everything and only you can do them:

- [ ] **Authorize the Daloopa connector.** Both `daloopa` and `daloopa-docs` MCP servers need
      OAuth. Do this in claude.ai connector settings (or `/mcp` in an interactive `claude`
      session). Until then every Daloopa skill is dead. Verify with `daloopa:setup` in any session.
- [ ] **Check Daloopa plan limits.** Note the request/credit quota — the initiation phase
      (10 names × research note + model) is the heaviest single burst of the whole project.
      If quota is tight, initiations spread across weeks instead of one weekend.
- [ ] **Create the GitHub repo:** `gh repo create Nick-Furton/furton-coverage --public` (gh is
      already authed). Decide now: site will serve from `/docs` on `main`, same as furton.ai.
- [ ] **Universe overlap policy.** Recommendation: at most 3 names overlapping the Furton Research
      Dow roster (overlap enables cross-project comparisons; too much overlap looks like one
      project wearing two hats). Final universe is approved by you at the Phase 1 merge gate.

---

## 3. Architecture

```
Furton Coverage/
├── CLAUDE.md                 # conventions every session must follow (exists from day 0)
├── PLAN.md                   # this file
├── config/
│   ├── universe.json         # tickers: sector, fiscal-year end, earnings dates, daloopa_ok flag
│   └── calendar.json         # next earnings event per ticker (auto-refreshed)
├── notes/<TICKER>/           # 2026-07-21_preview.md, 2026-07-22_flash.md, 2026-07-24_review.md
├── models/<TICKER>/          # <TICKER>_model_<date>.xlsx  (from daloopa:build-model / initiate)
├── scorecard/
│   ├── calls.json            # our timestamped calls: {ticker, date, metric, call, actual, verdict}
│   └── guidance.json         # management guidance items vs. actuals, per quarter
├── scripts/                  # Python (run with `py`; set PYTHONUTF8=1 — console is cp1252)
│   ├── build_site.py         # notes/ + scorecard/ + models/ → docs/ static site
│   ├── refresh_calendar.py   # upcoming earnings dates → config/calendar.json
│   └── score.py              # recompute accuracy stats → scorecard/summary.json
├── site_src/                 # templates/CSS for the generator (matches furton.ai v2 style)
└── docs/                     # generated static site — GitHub Pages serves this; never hand-edit
```

**Design rules (also in CLAUDE.md):**
- All Daloopa-derived numbers flow through skills into *files*; the site generator only reads
  files. No network calls at site-build time → the site always builds, even offline.
- Every note carries frontmatter: `ticker, type (preview|flash|review|initiation), event_date,
  published_at`. The generator and scorecard both key off it.
- Preview server port: **8802** (8801 = website v2, 8899 = Schwab Analysis, 8765 = Furton engine).
- Content standard: every preview note makes falsifiable calls (rev/EPS/key-KPI vs. consensus or
  guidance, plus one qualitative "what matters" call). Flashes must grade the preview's calls.
- Disclaimer on every page: educational research, not investment advice.

---

## 4. Working Agreements for Paired Sessions

Two Claude Code terminals run concurrently in this repo. To keep that safe:

1. **Path ownership.** Each session's kickoff prompt lists the paths it owns. A session writes
   *only* inside its owned paths (plus its own scratch). Never edit CLAUDE.md mid-pair — propose
   changes in `notes/_inbox/` and merge them solo between phases.
2. **Commit discipline.** Commit only your owned files, with a `[S<n>]` prefix (e.g.
   `[S3] preview/flash/review templates`). If a commit or push races the paired session:
   `git pull --rebase`, retry. Never `git add -A`.
3. **Merge gates.** Each phase ends with a solo 10-minute gate (either terminal): review both
   sessions' output, resolve anything in `_inbox/`, commit, push, tick the phase checkbox below.
4. **Session hygiene.** Start every session with "Read CLAUDE.md and PLAN.md first." End every
   session with: commit, push, and a 3-line handoff appended to `notes/_inbox/handoffs.md`.

---

## 5. Build Phases — five pairs, ten sessions

Each phase = two terminals running simultaneously. Kickoff prompts are copy-paste ready:
open two terminals, `cd` into this folder, run `claude`, paste one prompt into each.

---

### ☐ Phase 1 — Foundation ∥ Data validation

**Session 1 — Scaffold & calendar** *(owns: `config/`, `scripts/refresh_calendar.py`, repo scaffold, `.gitignore`)*

> Read CLAUDE.md and PLAN.md. You are Session 1 (scaffold). Create the full directory skeleton
> from PLAN.md §3 with .gitkeep files. Write the `universe.json` and `calendar.json` schemas and a
> candidate list of ~15 tickers as universe.json entries flagged `candidate: true` — optimize for
> KPI-rich names, sector spread, and staggered earnings dates (list each candidate's typical
> reporting month). Then write and test `scripts/refresh_calendar.py`: given universe.json, fetch
> upcoming earnings dates (web search is fine as the source) and write calendar.json. Windows
> notes: run Python via `py`, set PYTHONUTF8=1. Do NOT touch notes/, scorecard/, site_src/, or
> anything Daloopa. Commit as [S1], push, and append a handoff to notes/_inbox/handoffs.md.

**Session 2 — Daloopa validation** *(owns: `notes/_inbox/daloopa_report.md`)*

> Read CLAUDE.md and PLAN.md. You are Session 2 (Daloopa validation). Run daloopa:setup and
> confirm the connection. Then, for each candidate ticker you find in config/universe.json (if
> Session 1 hasn't committed it yet, use: NVDA MSFT AMZN GOOGL META COST JPM LLY CAT NFLX AMD UNH
> DE PANW CRM), assess Daloopa data depth — run daloopa:tearsheet on 3–4 representative names and
> spot-check the rest for KPI coverage (segment detail, guidance capture, history length). Write
> notes/_inbox/daloopa_report.md: a table of candidates scored on data depth, plus your
> recommended final 10 with one line of rationale each, respecting the ≤3-Dow-overlap policy in
> PLAN.md §2. Note any rate/credit limits you hit. Do NOT edit config/ — the merge gate finalizes
> the universe. Commit as [S2], push, append a handoff.

**Merge gate 1:** Nick picks the final 10 → set `candidate: false→true/remove` in universe.json,
run refresh_calendar.py, commit. *Universe is now frozen; changes require a dated note.*

---

### ☐ Phase 2 — Deliverable pipeline ∥ Scorecard engine

**Session 3 — Note templates & desk workflow** *(owns: `notes/` templates + one test ticker's notes, `.claude/skills/` if used)*

> Read CLAUDE.md and PLAN.md. You are Session 3 (deliverables). Design the three note templates —
> preview (T-1: setup, consensus/guidance table, our falsifiable calls, what-matters), flash
> (T+0: headline vs. our calls graded, guidance changes, first-read verdict), review (T+2: full
> daloopa:earnings-review synthesis, model deltas, thesis update) — with the frontmatter schema
> from PLAN.md §3. Then prove the pipeline end-to-end as a backtest: pick one universe ticker
> whose last earnings already happened; write its preview using ONLY pre-print information
> (daloopa:earnings-prep + web search restricted to pre-print dates), then its flash and review
> from the actual results. This validates the templates against reality. Package the repeatable
> procedure as three project slash commands (skills): /preview <TICKER>, /flash <TICKER>,
> /review <TICKER>. Do NOT touch scorecard/ or scripts/. Commit as [S3], push, append a handoff.

**Session 4 — Scorecard engine** *(owns: `scorecard/`, `scripts/score.py`)*

> Read CLAUDE.md and PLAN.md. You are Session 4 (scorecard). Define scorecard/calls.json and
> scorecard/guidance.json schemas per PLAN.md §3 — every entry timestamped, with a
> source_note field pointing at the note file that made the call. Write scripts/score.py to
> compute per-ticker and aggregate stats: our hit rate by call type, management guidance accuracy
> (beat/met/missed own guidance), calibration over time; output scorecard/summary.json for the
> site. Seed with realistic dummy data, test, then leave the dummies clearly flagged
> `"dummy": true` so the site pair can build against real structure. Fail loudly on malformed
> entries — same fail-loud philosophy as Furton Research's vote parser. Do NOT touch notes/
> templates. Commit as [S4], push, append a handoff.

**Merge gate 2:** wire check — do Session 3's frontmatter fields carry everything score.py needs
to link a call to its note? Fix mismatches now, solo. Delete nothing; flag dummies.

---

### ☐ Phase 3 — Website ∥ Initiations batch 1

**Session 5 — Site generator & design** *(owns: `site_src/`, `scripts/build_site.py`, `docs/`, `.claude/launch.json`)*

> Read CLAUDE.md and PLAN.md. You are Session 5 (website). Build scripts/build_site.py +
> site_src/ templates: a static site generated from notes/, scorecard/summary.json, and models/.
> Pages: home (coverage universe grid + next-earnings countdown + headline scorecard stats),
> per-ticker page (note timeline, call record, model download), research library (all notes,
> filterable), scorecard page (charts — use the dataviz skill), about/methodology stub. Visual
> language: match furton.ai v2's dashboard style (reference: ..\..\Furton Research\
> furton_website\) but it must read as a sibling brand, not a clone — different accent color.
> Output to docs/ for GitHub Pages. Add .claude/launch.json serving docs/ on port 8802 and verify
> with the preview tools, including dark mode and mobile widths. Build against Session 4's dummy
> scorecard data and Session 3's backtest notes. Do NOT run any Daloopa skills (the paired
> session is consuming the quota). Commit as [S5], push, append a handoff.

**Session 6 — Initiate coverage, names 1–5** *(owns: `notes/<first-5-tickers>/`, `models/<first-5>/`, scorecard entries for those tickers)*

> Read CLAUDE.md and PLAN.md. You are Session 6 (initiations, batch 1). For the first 5 tickers
> in config/universe.json (alphabetical): run daloopa:initiate to produce the research note and
> Excel model; save per PLAN.md §3 conventions with type: initiation frontmatter. From each
> note, extract our baseline view into scorecard/calls.json entries (thesis-level calls, flagged
> call_type: "initiation"). Keep a running cost/quota tally in notes/_inbox/daloopa_usage.md and
> STOP if you hit plan limits — partial coverage is fine, silent failure is not. Do NOT touch
> site_src/, scripts/, or the other 5 tickers. Commit as [S6] after EACH completed ticker (the
> paired session is building the site against your output live), push, append a handoff.

**Merge gate 3:** rebuild the site with real batch-1 content, delete Session 4's dummy scorecard
entries, fix rendering issues, enable GitHub Pages from /docs, first deploy.

---

### ☐ Phase 4 — Initiations batch 2 + guidance backfill ∥ Automation

**Session 7 — Initiations 6–10 & guidance history** *(owns: `notes/<last-5>/`, `models/<last-5>/`, `scorecard/guidance.json`)*

> Read CLAUDE.md and PLAN.md. You are Session 7 (initiations batch 2 + backfill). First: initiate
> the remaining 5 universe tickers exactly as Session 6 did (read its handoff and
> daloopa_usage.md; keep the tally going). Second: backfill scorecard/guidance.json — for ALL 10
> names, use daloopa:guidance-tracker to capture the last 4 quarters of management guidance vs.
> actuals, so the scorecard shows real accuracy stats from day one instead of an empty chart.
> Commit as [S7] per ticker, push, append a handoff.

**Session 8 — Automation & runbook** *(owns: `scripts/refresh_calendar.py` (extend), `.claude/skills/`, `RUNBOOK.md`, scheduled tasks)*

> Read CLAUDE.md and PLAN.md. You are Session 8 (automation). Build the operating loop around one
> hard constraint: Daloopa is an interactively-authenticated MCP connector and may be ABSENT in
> headless/scheduled cloud runs — so scheduled automation must never assume Daloopa access.
> Design accordingly: (1) a scheduled task (schedule skill) that runs refresh_calendar.py daily
> and, when a universe name reports within 48h, sends a notification telling Nick which command
> to run; (2) make /preview, /flash, /review one-command interactive runs that end by rebuilding
> the site and pushing (earnings-day effort = open terminal, type /flash NVDA); (3) a /digest
> weekly skill: what reported, how our calls scored, what's next week — output a site post +
> a Substack-pasteable version; (4) write RUNBOOK.md covering the full cadence: T-1 preview,
> T+0 flash, T+2 review, weekly digest, quarterly model refresh + score.py rerun. Test the
> scheduled task fires. Verify whether a locally-scheduled claude session retains Daloopa auth —
> document the answer in RUNBOOK.md; if yes, automate more; if no, the notify-then-manual design
> stands. Commit as [S8], push, append a handoff.

**Merge gate 4:** full dress rehearsal — pick the next real earnings event on the calendar and
walk RUNBOOK.md end-to-end for it (even if that means waiting a few days; the gate closes when
one real cycle has run).

---

### ☐ Phase 5 — Polish ∥ Publish

**Session 9 — Design & data-viz polish** *(owns: `site_src/`, `docs/`)*

> Read CLAUDE.md and PLAN.md. You are Session 9 (polish). Run the impeccable audit and polish
> passes plus the dataviz skill over the site: scorecard charts, per-ticker pages, responsive
> behavior, dark mode, favicon/OG tags. Beware the curly-apostrophe JS gotcha from the furton.ai
> polish pass. Verify everything on port 8802 with preview tools before committing. Do NOT touch
> content in notes/ or scorecard data. Commit as [S9], push, append a handoff.

**Session 10 — Publishing & positioning** *(owns: `docs/CNAME`, `README.md`, methodology one-pager, `notes/_inbox/resume_bullets.md`)*

> Read CLAUDE.md and PLAN.md. You are Session 10 (publishing). (1) Set up
> coverage.furton.ai: CNAME file in docs/, then walk Nick through the Porkbun DNS record —
> remember the hidden parking-ALIAS gotcha from the furton.ai setup. (2) Add a cross-link on
> furton.ai to the new site (edit lives in ..\..\Furton Research\furton_website\). (3) Write a
> 2-page methodology note (docx via the docx skill → PDF via Word COM, no LibreOffice here)
> mirroring the Furton Research methodology paper's tone: universe selection, note cadence,
> scorecard math, honest limitations. (4) Draft resume_bullets.md: 3 bullet variants + a
> 90-second interview narrative connecting Furton Research and Furton Coverage. (5) Write the
> Substack setup checklist (manual for Nick) and a digest cross-post procedure. Commit as [S10],
> push, append a handoff.

**Merge gate 5:** DNS verified with DoH (eduroam gotcha), HTTPS enforced, site linked both ways,
PDF renders. Project is live.

---

## 6. Steady-State Cadence (post-build)

| When | What | Command |
| --- | --- | --- |
| Daily (automated) | Calendar refresh + 48h-warning notification | scheduled task |
| T-1 before a print | Preview note published | `/preview <TICKER>` |
| Print day | Flash within hours; preview calls graded | `/flash <TICKER>` |
| T+2 after call | Full review, model updated, scorecard updated | `/review <TICKER>` |
| Friday | Weekly digest → site + Substack | `/digest` |
| Quarterly | Model refresh all 10, score.py recalibration, methodology addendum | manual session |

Sustained load estimate: earnings cluster weeks ≈ 3–5 events → roughly 1–2 hrs of terminal
babysitting per week during season, near-zero off-season.

## 7. Risks & Honest Caveats

- **Daloopa auth in headless runs** is the load-bearing risk for "automation"; the plan assumes
  notify-then-manual until Session 8 proves otherwise.
- **Daloopa quota** could throttle Phases 3–4; the per-ticker commit rule means partial progress
  is always preserved and visible.
- **Consensus data** (for "vs. expectations" tables) isn't Daloopa's job — previews should lean
  on management guidance + web-sourced consensus with the source cited, or frame calls vs.
  guidance only. Decide once at merge gate 2 and note it in the methodology.
- **Credibility cuts both ways:** a public scorecard that shows misses is the feature, not a bug.
  Never quietly edit a published call — corrections get dated addenda, same as the paper.
- **Two sessions, one repo** works only with the §4 discipline; if conflicts happen anyway,
  fall back to running pairs in separate git worktrees.

## 8. Revenue Path (optional, after one full quarter)

1. Quarter 1: publish everything free on the site; digests cross-posted to a free Substack.
2. If open rate justifies it: flashes stay free (distribution), full reviews + models move to a
   paid tier (~$10/mo). Models are the paywall-worthy artifact.
3. Do not gate the scorecard — transparency is the brand.
