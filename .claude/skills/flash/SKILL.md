---
name: flash
description: Draft and publish a Furton Coverage T+0 earnings flash note for a covered ticker within hours of its earnings 8-K filing (e.g. "/flash CRWD", "/flash AMZN"). Use this whenever the user wants headline actuals graded against a prior preview's calls, any guidance changes, and a first-read verdict right after a print. Also use it for backtests ("write the flash for CRWD's last actual print"). A missed same-day flash still uses this command -- it becomes an honestly late-timestamped delayed flash, never backdated. Always run the adversarial fact-check publish gate before treating any flash as final.
---

# /flash TICKER

Publishes `notes/<TICKER>/<YYYY-MM-DD>_flash.md`: headline actuals vs. the preview's
calls, guidance changes, first-read verdict -- written within hours of the earnings 8-K
(Exhibit 99.1) hitting EDGAR.

**Read `../_shared/note_pipeline.md` first** for the shared steps (ticker resolution,
drafting, the claims list, the publish gate, applying its verdict, writing, reporting).
This file covers what's specific to a flash: fetching the just-filed release with
freshness guarantees, and grading the preview's calls rather than inventing new ones
from scratch.

## What makes a flash different

A flash's job is speed and accuracy on the ACTUALS, not new analysis -- EDGAR posts the
8-K within minutes of the release, so the flash is often faster than a vendor-fed desk
gets the same numbers (PLAN §3). Its calls block isn't written fresh; it's the prior
preview's calls **with `actual` filled in**, so score.py can grade them.

## 1. Data pull -- ALWAYS force-refetch on print day

```
py -c "import sys; sys.path.insert(0,'scripts'); import edgar; e,t = edgar.press_release_text('<TICKER>', force=True); print(e.press_release_url)"
```
`force=True` is not optional here -- without it you risk reading a cached pre-print
version if this ticker's submissions index or 8-K happened to be fetched earlier today
for any reason. Read the release text for the headline actuals (revenue, margins, EPS,
the company's own KPIs) and any new/updated guidance section for the NEXT period.

Find the prior preview: `notes/<TICKER>/<most recent prior date>_preview.md`. If none
exists (this ticker has no preview on file yet -- e.g. the very first print covered),
say so plainly in the note and skip the "vs. our calls" grading -- do not fabricate a
retroactive call to grade against.

## 2. Fill the template

Use `notes/_templates/flash.md`. For each call in the preview's `calls:` block, copy it
into this note's `calls:` block with the SAME `id` and add its `actual` (value, basis,
asof, source_filing = this release's URL). If the release also issues new guidance for
the next period, add it as a fresh `guidance:` entry (same shape as the preview
template, `guided_at_period` = this note's `period`).

## Backtest mode

If flashing a print that already happened, this step is simple: the "just filed"
release IS the historical one, and `event_date`/`published_at` should reflect the
original print date, not today -- state clearly in the note that this is a backtest
reconstruction, not a same-day flash, so nobody mistakes the timestamp for a live one.

## 3-7. Publish gate, write, report

Follow `../_shared/note_pipeline.md` steps 3-7. Every grading number (actual figures,
any new guidance) gets independently re-verified against the just-filed 8-K -- this is
the highest-stakes moment for the fact-check gate, since a flash is read while the
market is actively reacting to the same print.
