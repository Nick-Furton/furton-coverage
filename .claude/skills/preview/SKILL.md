---
name: preview
description: Draft and publish a Furton Coverage T-1 earnings preview note for a covered ticker (e.g. "/preview CRWD", "/preview NVDA"). Use this whenever the user wants a pre-earnings note the night before a covered name reports -- a guidance table built from the PRIOR quarter's 8-K, our falsifiable calls graded against that guidance, and a what-matters section. Also use it for backtests ("write a preview as if it were the night before CRWD's last print, using only pre-print information"). Always run the adversarial fact-check publish gate before treating any preview as final -- never hand-write a preview note directly without this command's pipeline.
---

# /preview TICKER

Publishes `notes/<TICKER>/<YYYY-MM-DD>_preview.md`: the pre-earnings note, T-1 (the
evening before, or -- for a backtest -- using only information that would have been
available before the print).

**Read `../_shared/note_pipeline.md` first** -- it defines steps 0/2 through 7 (ticker
resolution, drafting against the template, the claims list, the publish gate, applying
its verdict, writing the file, reporting back). This file only covers what's specific
to a preview: which data to pull and what the guidance table / calls actually are.

## What makes a preview different

A preview's whole job is to build a **guidance table from the PRIOR quarter's earnings
8-K** and state **falsifiable calls graded against it** (PLAN §3's benchmark decision --
grade against management's own guidance, not consensus). Getting "prior quarter" right
matters: if the ticker is about to report Q2, the guidance you want is what management
gave for Q2 back when they reported Q1.

## 1. Data pull (this note type's step 1)

```
py scripts/edgar.py earnings8k <TICKER> --which 1   # sanity-check by hand first
```
`which=0` is the most recent (upcoming/just-happened) earnings 8-K; `which=1` is the one
before it -- the release that GUIDED the period you're previewing. Confirm the CLI finds
exactly one EX-99.1/EX-99 press release before trusting it (it fails loud if it can't).

Then, in a short Python one-liner (`py -c "..."` or a scratch script, `PYTHONUTF8=1` set):
```python
import sys; sys.path.insert(0, "scripts"); import edgar
e, text = edgar.press_release_text("<TICKER>", which=1)
```
Read `text` for the "Outlook" / "Guidance" / "Financial Outlook" section -- extract
every quantitative line (revenue, margin, EPS, company-specific KPIs like ARR) with its
low/high or point+tolerance, and note the exact basis (gaap/non_gaap) the release states.
Also pull `edgar.companyfacts("<TICKER>")` for headline history context (recent trend,
YoY growth) to inform your calls -- but the guidance TABLE itself must come from the
press release text, not from companyfacts (companyfacts has no forward guidance at all,
and no segment/KPI detail per the universe.json `companyfacts_caveat`).

**Backtest mode:** if you're previewing a print that already happened (proving the
pipeline end-to-end, not a live upcoming print), restrict yourself to information a real
T-1 preview would have had: the guidance 8-K (`which=1` relative to the print being
tested) and the 10-Q/10-K filed before it, plus web sources dated before the print date.
Do not peek at the actual results 8-K (`which=0`) while drafting -- that defeats the
point of a backtest. State the backtest framing explicitly in the note's Setup section.

## 2. Fill the template

Use `notes/_templates/preview.md`. The `guidance:` block is the table you just extracted
(one entry per guided metric, `period` = the period being previewed, `guided_at_period`
= the period whose 8-K issued it). The `calls:` block is your own view -- typically
`kind: direction` (beat/met/miss vs. the guidance band you just built), though a metric
you have independent conviction on can be `range` or `point`. Don't call every guided
metric just because it's there -- a call with no real conviction behind it is noise on
the scorecard; call the ones that matter to the thesis.

## 3-7. Publish gate, write, report

Follow `../_shared/note_pipeline.md` steps 3-7 exactly. The gate re-verifies your
guidance-table figures AND your calls' benchmarks against the cited 8-K -- a
transcription slip in the guidance table is just as damaging as a wrong call, since
everything downstream (the flash's grading, the scorecard) inherits it.
