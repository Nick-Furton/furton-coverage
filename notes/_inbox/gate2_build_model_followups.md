# Merge Gate 2 — build_model.py follow-ups (deferred, not fixed at the gate)

Surfaced by the Gate 2 `/code-review` pass (2026-07-11). These are real defects in
`scripts/build_model.py` (S3), but they live in an engine with **no unit tests** whose
correct output can only be confirmed against **live EDGAR** for the specific tickers
named below (DE's stale-tag case, Dec-FYE names' missing standalone-Q4 facts). Blind-
editing them at the gate would risk regressing S3's live-validated CRWD/AMZN/DE output,
so they are logged here for a dedicated build_model hardening pass **before Session 6
relies on the Excel models** (Phase 3). None of them touch the scorecard or the S3↔S4
wire contract — the gate's core checks passed independently of these.

Ranked most severe first:

1. **Margin rows render `0.0%` instead of blank when the numerator is blank.** The
   stale-tag design correctly leaves a data cell empty (e.g. DE's GrossProfit/
   OperatingIncomeLoss once its tag goes stale), but the margin formula
   `=IF(rev=0,"-",gp/rev)` treats the empty `gp` cell as `0`, so it prints `0.0%` — a
   fabricated margin in exactly the scenario the anchoring logic advertises it prevents.
   Fix: guard the numerator with `IF(<num_cell>="","-",...)` / `ISBLANK`.

2. **Revenue YoY hard-codes a 4-column offset as "4 quarters,"** but the displayed
   columns are not guaranteed contiguous quarters — companyfacts generally omits the
   standalone Q4 3-month revenue (the 10-K tags the 12-month duration, filtered out), so
   for Dec-FYE names (AMD/AMZN/LLY) "4 columns back" is not the year-ago quarter and the
   growth % is nonsensical. Fix: match the year-ago column by period-end date, not by a
   fixed column offset.

3. **`_period_label` mislabels 52/53-week fiscal calendars.** It derives the quarter from
   the period-END calendar month; when a 13-week quarter ends a few days into the next
   month (DE, October FYE, week-based calendar), the quarter label is off by one (and can
   flip the FY digits at the boundary).

4. **Provenance footnote contradicts the selection.** The Income Statement source note
   says figures are the "most-recently-filed" duration-matched fact, but `_dedup_by_end`
   deliberately keeps the **earliest-filed** (as-originally-reported) value. For a name
   with a restatement (docstring cites AMZN's split-driven EPS restatement) the sheet
   shows the original number while the note claims the latest. Fix: correct the footnote
   wording to "earliest-filed / as-originally-reported."

5. **`named_metric` can pick an annual-only tag and then abort.** It ranks fallback tags
   by the latest period-end regardless of duration; if a filer tags full-year revenue
   under one concept and quarterly under another, the quarterly-duration filter yields
   nothing and the build fails loud ("no quarterly-duration Revenue fact") even though
   quarterly revenue exists under a fallback tag. Fix: prefer the tag that actually
   carries quarterly-duration facts, or merge across fallback tags.

## Also noted (minor, template clarity — not blocking)

- **Direction-call `benchmark` band has no `basis` of its own.** score.py's `_check_basis`
  guards record-vs-actual, not benchmark-vs-actual, so a benchmark copied from a non_gaap
  guide onto a call declared `gaap` would grade a gaap actual against a non_gaap band with
  no guard firing. Convention (documented): the benchmark is always on the record's own
  `basis`; an author must not mix them. Low risk (requires author error); left as a
  documented convention rather than a code change.
