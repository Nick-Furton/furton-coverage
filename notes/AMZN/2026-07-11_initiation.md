---
ticker: "AMZN"
type: initiation
event_date: "2026-07-11"
published_at: "2026-07-11T17:00:00Z"
period: "FY2025"
fiscal_year_end: "December"
basis: "gaap"
source_filings:
  - description: "FY2025 10-K (filed 2026-02-06) -- business narrative, segments, MD&A"
    url: "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm"
  - description: "companyfacts XBRL (headline financials/history)"
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0001018724.json"
  - description: "Q1 FY2026 earnings 8-K (EX-99.1), filed 2026-04-29 -- current-quarter actuals and Q2 2026 outlook"
    url: "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000012/amzn-20260331xex991.htm"
fact_check:
  status: passed
  run_at: "2026-07-11T20:30:00Z"
  notes: "9/9 claims verified. 6 numeric claims (Q2 2026 net-sales/op-income guidance + 4 FY2025 10-K facts) passed; one (FY2025 net income $77.670B) initially came back as a mismatch because the verifier agent's WebFetch returned a different rendering of the same accession (a TTM-through-Q1-2026 view) than the actual FY2025 10-K -- a known infra quirk (see Session 3's handoff); re-verified in isolation and confirmed genuinely present in the filing. Both qualitative theses initially failed: the AWS-margin call wrongly framed FY2025 as margin EXPANSION when the filing's own segment table shows AWS margin actually contracted (37.0% to 35.4%); the cost-discipline call ignored that the 10-K's own Q1 2026 guidance implies margin compression from new cost items, not the absence of FY2025's one-time charges. Both corrected to the opposite (compression) thesis and passed on re-verification."
calls:
  - id: "AMZN-FY2026Q2-initiation-net_sales"
    ticker: "AMZN"
    timestamp: "2026-07-11T17:00:00Z"
    call_type: initiation
    period: "FY2026Q2"
    metric: "net_sales"
    unit: "USD_M"
    basis: "gaap"
    source_note: "notes/AMZN/2026-07-11_initiation.md"
    higher_is_better: true
    confidence: 0.55
    call:
      kind: direction
      value: "beat"
      benchmark:
        kind: range
        low: 194000.0
        high: 199000.0
    rationale: "Amazon guided Q2 2026 net sales to $194.0-199.0B (16-19% YoY growth) in the Q1 FY2026 8-K, assuming Prime Day falls in Q2. AWS grew 20% in FY2025 and accelerated through the year on capacity additions; combined with a now-routine pattern of the top end of guidance proving conservative in strong demand quarters, we lean toward a print at or above the top of the range."
  - id: "AMZN-FY2026Q2-initiation-operating_income"
    ticker: "AMZN"
    timestamp: "2026-07-11T17:00:00Z"
    call_type: initiation
    period: "FY2026Q2"
    metric: "operating_income"
    unit: "USD_M"
    basis: "gaap"
    source_note: "notes/AMZN/2026-07-11_initiation.md"
    higher_is_better: true
    confidence: 0.5
    call:
      kind: direction
      value: "met"
      benchmark:
        kind: range
        low: 20000.0
        high: 24000.0
      # cost/capex-adjacent items (severance, litigation settlements, AI infra depreciation) create real
      # downside risk to this band even as revenue upside exists -- we call the middle of the range, not
      # an operating-income beat, unlike the net-sales call above.
    rationale: "Amazon guided Q2 2026 operating income to $20.0-24.0B, versus $19.2B in Q2 2025. FY2025 already absorbed $2.5B (FTC settlement), $2.7B (severance) and $1.3B (asset impairments) of one-time-ish charges against a $1.4B step-up in depreciation from the shortened server useful-life change -- we see the guided band as achievable but not obviously conservative given AI-infrastructure depreciation and continued severance/litigation charge risk, so we call 'met' (within band) rather than a beat."
  - id: "AMZN-FY2026-initiation-aws_margin_thesis"
    ticker: "AMZN"
    timestamp: "2026-07-11T17:00:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "aws_operating_margin_qualitative"
    unit: "n/a"
    basis: "gaap"
    source_note: "notes/AMZN/2026-07-11_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the FY2025 10-K itself makes: AWS operating margin stays under pressure through FY2026 -- continuing, not reversing, the FY2025 pattern -- as AI-infrastructure depreciation (including the shortened server/networking useful life) keeps growing faster than AWS revenue."
    rationale: "FY2025 10-K: AWS net sales grew 20% to $128.7B and AWS operating income grew in dollars to $45.6B from $39.8B, but AWS operating MARGIN actually contracted -- 37.0% in FY2024 ($39.8B/$107.6B) to 35.4% in FY2025 ($45.6B/$128.7B) -- because AWS technology/infrastructure costs, which absorbed the bulk of the $1.4B useful-life-driven depreciation step-up, grew faster than revenue. We initially misread the dollar growth as margin expansion; corrected here. Our forward call is that this compression continues in FY2026 as AI-capex depreciation keeps scaling, not that it reverses."
  - id: "AMZN-FY2026-initiation-cost_discipline_thesis"
    ticker: "AMZN"
    timestamp: "2026-07-11T17:00:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "opex_discipline_qualitative"
    unit: "n/a"
    basis: "gaap"
    source_note: "notes/AMZN/2026-07-11_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view: consolidated operating margin expansion stalls or reverses in Q1 FY2026 (the only FY2026 quarter management has guided as of this note), not because FY2025's one-time charges recur, but because Amazon's own guidance points to new FY2026 cost items -- higher Amazon Leo satellite costs, quick-commerce investment, and sharper international pricing -- that the 10-K does not attribute to the absence of FY2025's severance/legal charges."
    rationale: "FY2025 10-K MD&A: operating income rose to $80.0B (11.2% of $716.9B net sales) from $68.6B (10.8% of $637.9B) in FY2024, despite absorbing the FTC settlement, severance, and asset-impairment charges detailed in Note 1. We initially framed FY2026 as a further margin-expansion story on those charges rolling off; the 10-K's own Q1 2026 guidance (operating income $16.5-21.5B on higher net sales) implies a margin band whose low end is below Q1 2025's ~11.5-12%, and management explicitly attributes that risk to NEW FY2026 investments (Leo, quick commerce, international pricing) rather than to any repeat of FY2025's charges. Corrected here to reflect what the filing's own forward-looking guidance actually implies, rather than our original (unsupported) extrapolation."
---

# AMZN -- Initiation: Amazon.com, Inc.

*Initiation note: sets our baseline thesis on AMZN from the FY2025 10-K (filed
2026-02-06) and the Q1 FY2026 earnings 8-K (filed 2026-04-29). Unlike a preview note,
this is not graded against a prior quarter's guidance -- it establishes the calls above
as the tracked baseline for future flashes/reviews. AMZN is one of the two GAAP-basis
names in the roster (with DE) -- its guidance and grading actuals are GAAP by
convention, no non-GAAP reconciliation trap to watch here.*

## Business

Amazon organizes operations into three segments: **North America** (retail + advertising
+ subscriptions in North America), **International** (same, internationally), and
**AWS** (compute/storage/database/AI services for enterprises, startups, governments).
FY2025 consolidated net sales were $716.9B, up 12% year over year: North America
$426.3B (+10%), International $161.9B (+13%), AWS $128.7B (+20%, the fastest-growing
segment). Segment operating income: North America $29.6B (from $25.0B), International
$4.75B (from $3.79B), AWS $45.6B (from $39.8B) -- AWS alone contributed more operating
income than the other two segments combined. Consolidated operating income was $80.0B
(11.2% margin) versus $68.6B (10.8% margin) in FY2024; net income was $77.67B.

Three FY2025 items matter to the forward thesis: (1) a change in estimated useful life
for a subset of servers/networking equipment (six years to five) added $1.4B of
depreciation and cut net income by $1.0B, mostly hitting AWS -- a direct, disclosed
readthrough of AI-infrastructure capital intensity; (2) one-time-ish charges totaling
roughly $6.5B pretax (FTC settlement $2.5B in Q3, ~$2.4B of Italy tax/legal/severance/
impairment charges in Q4, plus ~$2.7B of severance company-wide) that management frames
as non-recurring; and (3) AWS's growth reaccelerated to 20% in FY2025 (from a comparable
19% in FY2024), the highest of the three segments and the number AI-capex trades are
watching hardest.

## What we're tracking

- **Q2 2026 net sales and operating income vs. Amazon's own guide** ($194.0-199.0B net
  sales at 16-19% YoY growth; $20.0-24.0B operating income vs. $19.2B in Q2 2025, per
  the Q1 FY2026 8-K, assuming Prime Day falls in Q2) -- our baseline calls lean toward a
  net-sales beat but only a mid-band operating-income call given rising AI-infra
  depreciation and litigation/severance charge risk.
- **AWS operating margin trajectory**: it already contracted in FY2025 (37.0% to
  35.4%) as technology/infrastructure costs -- including the useful-life-driven
  depreciation step-up -- grew faster than AWS's 20% revenue growth. We track whether
  that compression continues into FY2026 as AI capex keeps scaling, not whether it
  reverses.
- **Whether FY2025's ~$6.5B of settlement/severance/impairment charges recur** -- a
  repeat would be a fresh headwind, but their absence would not by itself guarantee
  margin expansion, since Amazon's own Q1 2026 guidance already points to new cost
  items (Leo satellite costs, quick-commerce investment, sharper international
  pricing) as a separate compression risk.
- **Capital expenditure trend**, since AWS capacity investment is the read-through to
  the NVDA/AVGO/AMD names elsewhere in this coverage book -- Amazon does not itemize
  AI-specific capex separately from total capex in the 10-K, so this is tracked
  qualitatively pending 10-Q/8-K disclosure.

## Model

`models/AMZN/AMZN_model_2026-07-11.xlsx` -- built via `scripts/build_model.py AMZN`
against companyfacts XBRL. **Known data gap:** AMZN's `GrossProfit` XBRL tag has no
data in the trailing-8-quarter window (last tagged period is 2009-09-30) -- Amazon
does not report a standalone gross-profit line under that concept post-2009, so the
model's Gross Profit row is intentionally left blank per the anchoring design (a
build-time warning documents this; see the model's Income Statement tab notes) rather
than showing a stale or fabricated figure. Segment-level revenue/operating income
(North America/International/AWS) is not in companyfacts either (headline-only, per
the Session 2 structural finding) -- those figures above are cited directly to the
10-K.

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
