---
name: review
description: Draft and publish a Furton Coverage T+2 earnings review note for a covered ticker once its 10-Q is available (e.g. "/review CRWD", "/review DE"). Use this whenever the user wants a full synthesis combining the earnings 8-K actuals with 10-Q/XBRL detail, an updated Excel model, and a thesis update -- the deepest of the three note types. Also use it for backtests. Always run the adversarial fact-check publish gate before treating any review as final.
---

# /review TICKER

Publishes `notes/<TICKER>/<YYYY-MM-DD>_review.md`: the full synthesis, written once the
10-Q lands (or ~48h after the print if the 10-Q genuinely lags) -- 8-K actuals + 10-Q/
companyfacts detail, a refreshed model, and a thesis update.

**Read `../_shared/note_pipeline.md` first** for the shared steps. This file covers
what's specific to a review: pulling the 10-Q, refreshing the Excel model, and
reconciling/adding calls rather than grading a fresh batch.

## 1. Data pull

Find the 10-Q filed after the earnings 8-K:
```python
import sys; sys.path.insert(0, "scripts"); import edgar
subs = edgar.submissions("<TICKER>", force=True)
tenqs = [f for f in edgar.recent_filings(subs) if f.form == "10-Q"]
```
Take the newest one (or confirm none has filed yet -- if so, note the 10-Q is still
pending and write the review from the 8-K + companyfacts alone, flagged as partial,
rather than waiting indefinitely; a dated addendum can follow once the 10-Q lands).

Refresh the model:
```
py scripts/build_model.py <TICKER> --kpi-overrides <path to a JSON file of any
  press-release-extracted KPIs you verified for this quarter, if you have them>
```
This pulls fresh companyfacts (now including whatever the 10-Q updated) and writes
`models/<TICKER>/<TICKER>_model_<date>.xlsx`. Diff it mentally against the last model in
that directory (if one exists) to describe what changed in the note's "Model deltas"
section -- don't just say a model was rebuilt, say what moved.

## 2. Fill the template

Use `notes/_templates/review.md`. Pull the flash note (`notes/<TICKER>/<flash
date>_flash.md`) for the scorecard recap -- restate its grading, don't re-derive
numbers from scratch. Add any `calls:` entries the 10-Q's extra detail lets you refine,
and forward-looking thesis calls (often `kind: qualitative`, though a genuine numeric
next-period call is fine too) for the quarter ahead.

## 3-7. Publish gate, write, report

Follow `../_shared/note_pipeline.md` steps 3-7. Every reconciled or new numeric claim
gets checked against its cited document (8-K, 10-Q, or companyfacts URL); qualitative
thesis calls get the refutation pass. Mention the refreshed model's path in your report
back to the user.
