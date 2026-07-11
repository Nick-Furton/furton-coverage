<!--
FLASH TEMPLATE — published T+0 (within hours of the earnings 8-K / EX-99.1 filing).
See SCHEMA.md for the full frontmatter contract. A missed T+0 becomes an honestly
timestamped delayed flash (published_at tells the truth) — never backdated (PLAN §6).
-->
---
ticker: "{{TICKER}}"
type: flash
event_date: "{{YYYY-MM-DD}}"           # the print date (== the 8-K filing date)
published_at: "{{ISO-8601 datetime}}"   # honest — flag delayed flashes here, don't backdate
period: "{{FY20XXQn}}"                  # the fiscal period just reported
fiscal_year_end: "{{month}}"
basis: "{{gaap|non_gaap}}"
source_filings:
  - description: "{{FY20XXQn}} earnings 8-K (EX-99.1) — just filed, the actuals source"
    url: "{{EDGAR URL, force=True fetch — never served stale from cache on print day}}"
  - description: "{{prior preview note, for the calls being graded}}"
    url: "notes/{{TICKER}}/{{prior date}}_preview.md"
fact_check:
  status: pending
  run_at: null
  notes: ""
calls:
  # (a) GRADE the preview's calls: copy each preview call's id/shape VERBATIM, add `actual`.
  #     Carry EVERY field from the preview call unchanged — id, call_type, source_note,
  #     higher_is_better, AND confidence. This is the copy that gets extracted to the
  #     scorecard shard; drop confidence here and the calibration curve loses it forever.
  # (b) Optionally ADD new forward calls (e.g. reaction to updated guidance).
  - id: "{{TICKER}}-{{FY20XXQn}}-preview-{{metric}}"   # same id as the preview call being graded
    ticker: "{{TICKER}}"
    timestamp: "{{ISO-8601 datetime}}"
    call_type: preview            # unchanged — this IS the preview call, now with actual filled
    period: "{{FY20XXQn}}"
    metric: "{{metric}}"
    unit: "{{unit}}"
    basis: "{{gaap|non_gaap}}"
    source_note: "notes/{{TICKER}}/{{prior date}}_preview.md"
    higher_is_better: true    # true for revenue/EPS/ARR/margins; set to false for cost/capex/opex or score.py inverts beat/miss
    confidence: 0.0           # copy the SAME value from the preview call (omit only if the preview had none)
    call:
      kind: direction
      value: "{{beat|met|miss}}"
      benchmark:
        kind: range
        low: 0.0
        high: 0.0
    actual:
      value: 0.0
      basis: "{{gaap|non_gaap}}"    # must match the record's basis or score.py refuses to grade
      asof: "{{YYYY-MM-DD}}"
      source_filing: "{{EDGAR 8-K URL the actual was read from}}"
guidance:
  # Optional: if this release ALSO issues NEW guidance for the next period, record it
  # here in the same shape as the preview template's guidance: block (guided_at_period
  # == this note's period).
---

# {{TICKER}} — Flash: {{Company Name}} {{FY20XXQn}} actuals ({{event_date}})

## Headline actuals vs. our calls

| Metric | Guided | Actual | Vs. guidance | Our call | Graded |
|---|---|---|---|---|---|
| {{metric}} | {{low}}–{{high}} {{unit}} | {{actual}} {{unit}} | {{beat/met/miss}} | {{our call}} | {{HIT/MISS}} |

*Source: [{{FY20XXQn}} earnings 8-K EX-99.1]({{url}}).*

## Guidance changes

{{Did the company raise/cut/reaffirm guidance for the next period? Quote the release.
If new guidance was issued, it belongs in the `guidance:` frontmatter block above.}}

## First-read verdict

{{2-4 sentences: what this print means, in plain English, written within hours of the
release — this is the "flash," not the full synthesis (that's the T+2 review).}}

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
