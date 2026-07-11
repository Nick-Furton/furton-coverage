<!--
REVIEW TEMPLATE — published T+2 (once the 10-Q is available, or ~48h after the print
if the 10-Q lags). Full synthesis: 8-K actuals + 10-Q/companyfacts XBRL detail, model
deltas, thesis update. See SCHEMA.md for the full frontmatter contract.
-->
---
ticker: "{{TICKER}}"
type: review
event_date: "{{YYYY-MM-DD}}"            # the original print date this reviews
published_at: "{{ISO-8601 datetime}}"
period: "{{FY20XXQn}}"
fiscal_year_end: "{{month}}"
basis: "{{gaap|non_gaap}}"
source_filings:
  - description: "{{FY20XXQn}} earnings 8-K (EX-99.1)"
    url: "{{EDGAR URL}}"
  - description: "{{FY20XXQn}} 10-Q"
    url: "{{EDGAR URL}}"
  - description: "companyfacts XBRL (post-10-Q, for the model refresh)"
    url: "{{data.sec.gov companyfacts URL}}"
  - description: "prior flash note"
    url: "notes/{{TICKER}}/{{flash date}}_flash.md"
fact_check:
  status: pending
  run_at: null
  notes: ""
calls:
  # Reconcile any flash calls the 10-Q refines (e.g. a KPI only in the 10-Q's tables),
  # and/or add new thesis-level calls for the NEXT period. Same shape as flash.md.
  - id: "{{TICKER}}-{{FY20XXQn}}-review-{{metric}}"
    ticker: "{{TICKER}}"
    timestamp: "{{ISO-8601 datetime}}"
    call_type: review
    period: "{{FY20XXQn}}"
    metric: "{{metric}}"
    unit: "{{unit}}"
    basis: "{{gaap|non_gaap}}"
    source_note: "notes/{{TICKER}}/{{YYYY-MM-DD}}_review.md"
    higher_is_better: true    # true for revenue/EPS/ARR/margins; set to false for cost/capex/opex or score.py inverts beat/miss
    call:
      kind: qualitative
      value: "{{thesis statement, falsifiable in plain language}}"
    rationale: "{{why}}"
---

# {{TICKER}} — Review: {{Company Name}} {{FY20XXQn}} full synthesis

## What the 10-Q added

{{What detail the 10-Q/XBRL refresh surfaced beyond the 8-K headline (segment color,
balance-sheet items, updated share count, etc.). Cite `source_filings`.}}

## Model deltas

{{What changed in models/{{TICKER}}/ this quarter vs. the last build — call out the
specific line items. Link the refreshed model.}}

## Scorecard recap

{{Restate how this quarter's preview→flash calls graded (pull from the flash note —
do not re-derive numbers, just summarize) and note anything the flash under-called.}}

## Thesis update

{{2-4 sentences: does this print change the multi-quarter thesis on this name? State
it as a falsifiable, dated view — if it's a genuine forward call, add it to `calls:`
above as `kind: qualitative` (or numeric if possible) so it can be tracked next quarter.}}

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
