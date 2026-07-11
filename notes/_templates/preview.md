<!--
PREVIEW TEMPLATE — published T-1 (the day/evening before the print).
See SCHEMA.md in this directory for the full frontmatter contract. Fill every
{{PLACEHOLDER}}; delete this comment block before publishing. Do NOT set
fact_check.status to "passed" by hand — only the publish-gate workflow may do that.
-->
---
ticker: "{{TICKER}}"
type: preview
event_date: "{{YYYY-MM-DD}}"          # the upcoming print this note previews
published_at: "{{ISO-8601 datetime}}"  # set when the gate passes, not when drafting starts
period: "{{FY20XXQn}}"                 # the fiscal period about to be reported
fiscal_year_end: "{{month}}"
basis: "{{gaap|non_gaap}}"
source_filings:
  - description: "{{e.g. Q_ FY__ earnings 8-K (EX-99.1) — prior-quarter guidance source}}"
    url: "{{EDGAR URL}}"
  - description: "companyfacts XBRL (headline financials/history)"
    url: "{{data.sec.gov companyfacts URL}}"
  # add one entry per additional cited document (10-Q, web source for color, etc.)
fact_check:
  status: pending
  run_at: null
  notes: ""
guidance:
  # One entry per guided metric, pulled from the PRIOR quarter's 8-K press release.
  # Shape = scorecard/guidance/<TICKER>.jsonl (scorecard/SCHEMA.md is authoritative).
  - id: "{{TICKER}}-{{FY20XXQn}}-guid-{{metric}}"
    ticker: "{{TICKER}}"
    timestamp: "{{ISO-8601 datetime}}"
    metric: "{{e.g. revenue}}"
    unit: "{{e.g. USD_M}}"
    basis: "{{gaap|non_gaap}}"
    period: "{{FY20XXQn}}"              # period the guidance is FOR
    guided_at_period: "{{FY20XXQn}}"    # the quarter whose 8-K ISSUED this guidance
    higher_is_better: true    # true for revenue/EPS/ARR/margins; set to false for cost/capex/opex or score.py inverts beat/miss
    guidance:
      kind: range   # or point
      low: 0.0
      high: 0.0
    source_filing: "{{EDGAR 8-K URL the guidance was read from}}"
calls:
  # Our falsifiable calls for THIS print, graded against the guidance/benchmark above.
  # Shape = scorecard/calls/<TICKER>.jsonl.
  - id: "{{TICKER}}-{{FY20XXQn}}-preview-{{metric}}"
    ticker: "{{TICKER}}"
    timestamp: "{{ISO-8601 datetime}}"
    call_type: preview
    period: "{{FY20XXQn}}"
    metric: "{{metric}}"
    unit: "{{unit}}"
    basis: "{{gaap|non_gaap}}"
    source_note: "notes/{{TICKER}}/{{YYYY-MM-DD}}_preview.md"
    higher_is_better: true    # true for revenue/EPS/ARR/margins; set to false for cost/capex/opex or score.py inverts beat/miss
    confidence: 0.0   # optional, 0.0-1.0
    call:
      kind: direction   # direction | range | point | qualitative
      value: "{{beat|met|miss}}"        # only for kind: direction
      benchmark:                        # only for kind: direction — usually == the guidance band above
        kind: range
        low: 0.0
        high: 0.0
    rationale: "{{one or two sentences — why we expect this}}"
    # actual: omitted until the flash/review grades it
---

# {{TICKER}} — Preview: {{Company Name}} {{FY20XXQn}} ({{event_date}}, {{before/after}} market)

## Setup

{{2-4 sentences: what's changed since last quarter, what the market is watching, why this
print matters. Cite `source_filings` inline where a fact is used.}}

## Guidance table (from the {{guided_at_period}} 8-K, filed {{date}})

| Metric | Prior guidance ({{guided_at_period}}) | Basis |
|---|---|---|
| {{metric}} | {{low}}–{{high}} {{unit}} | {{basis}} |

*Source: [{{description}}]({{url}}).*

## Our calls

{{One short paragraph per call in the `calls:` block above, in plain English, each
explicitly tied to its `id` so a reader can find it in the frontmatter. State the
call, the benchmark it's graded against, and the one-line rationale.}}

- **{{metric}} — we call {{beat/met/miss}}** vs. guided {{low}}–{{high}} {{unit}}.
  {{rationale}}

## What matters

{{2-4 bullets: the qualitative things to watch on the print/call that aren't
machine-gradable calls — flag any as `qualitative` calls in frontmatter if falsifiable
enough to track.}}

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
