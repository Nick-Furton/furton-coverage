---
ticker: "DE"
type: initiation
event_date: "2026-07-13"
published_at: "2026-07-13T16:30:00Z"
period: "FY2025"
fiscal_year_end: "October"
basis: "gaap"
source_filings:
  - description: "FY2025 10-K (fiscal year ended 2025-11-02, filed 2025-12-18) -- business, segment structure, MD&A, trade-policy and ag-cycle risk"
    url: "https://www.sec.gov/Archives/edgar/data/315189/000110465925122321/de-20251102x10k.htm"
  - description: "companyfacts XBRL (headline financials/history)"
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0000315189.json"
  - description: "Q2 FY2026 earnings 8-K (EX-99.1), filed 2026-05-21 -- current-quarter actuals, segment detail, and the FY2026 net-income outlook"
    url: "https://www.sec.gov/Archives/edgar/data/315189/000110465926064747/de-20260521xex99d1.htm"
fact_check:
  status: passed
  run_at: "2026-07-13T16:55:00Z"
  notes: "13/13 claims verified. All 11 numeric claims (FY2026 net-income guide, C&F net-sales outlook, FY2025 revenue/net-income/EPS, Q2 FY2026 actuals/segments, ~$600M FY2025 tariff cost, $272M IEEPA recovery, FY2026 segment outlook, H1 capital return) matched their cited 10-K/8-K on first pass. Qualitative trade/ag-risk call passed first pass. The qualitative ag-cycle-cushion call was REFUTED on first pass, but on wrong-document evidence: the refuter quoted 10-K industry-outlook phrasing ('flat to up slightly', 'flat to slightly higher') that does NOT appear in the cited Q2 FY2026 8-K -- the known WebFetch wrong-document artifact flagged by S3/S6. It was corroborated as correct by (a) the parallel numeric verifier on the identical 8-K URL (prose-fy26-segment-outlook, matches=true) and (b) an isolated single-agent re-run that fetched the exact 8-K and returned refuted=false, confirming the segment outlook (PPA down 5-10%, SAT up ~15%, CF up ~20%), Large Ag industry down 15-20%, and the $4.5-5.0B net-income guide verbatim. Nothing cut or flagged."
calls:
  - id: "DE-FY2026-initiation-net_income"
    ticker: "DE"
    timestamp: "2026-07-13T16:30:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "net_income"
    unit: "USD_M"
    basis: "gaap"
    source_note: "notes/DE/2026-07-13_initiation.md"
    higher_is_better: true
    confidence: 0.62
    call:
      kind: direction
      value: "met"
      benchmark:
        kind: range
        low: 4500.0
        high: 5000.0
    rationale: "In the Q2 FY2026 8-K Deere maintained its FY2026 outlook for net income attributable to Deere & Company of $4.5-5.0 billion (a plain GAAP dollar range -- the least basis-ambiguous guide on our board). First-half FY2026 net income was $2.429B (down 9% YoY); reaching the ~$4.75B midpoint needs ~$2.32B in the second half versus ~$2.35B in H2 FY2025, which we view as achievable given Construction & Forestry and Small Ag & Turf strength offsetting the Large Ag downcycle. We call the full year landing INSIDE the reaffirmed band rather than above or below it."
  - id: "DE-FY2026-initiation-cf_net_sales_growth"
    ticker: "DE"
    timestamp: "2026-07-13T16:30:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "construction_forestry_net_sales_growth"
    unit: "pct"
    basis: "gaap"
    source_note: "notes/DE/2026-07-13_initiation.md"
    higher_is_better: true
    confidence: 0.5
    call:
      kind: direction
      value: "beat"
      benchmark:
        kind: point
        value: 20.0
        tolerance: 0.0
    rationale: "Deere's FY2026 segment outlook (Q2 FY2026 8-K) guides Construction & Forestry net sales up ~20%. Q2 FY2026 C&F net sales were already +29% YoY (H1 +31%) and C&F operating profit +48%, with management citing infrastructure spending, rental-fleet investment, and data-center construction starts as tailwinds. We call full-year C&F net-sales growth landing ABOVE the ~20% guide. (Segment net sales are press-release-sourced; companyfacts carries headline financials only.)"
  - id: "DE-FY2026-initiation-ag_cycle_thesis"
    ticker: "DE"
    timestamp: "2026-07-13T16:30:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "ag_cycle_trough_qualitative"
    unit: "n/a"
    basis: "gaap"
    source_note: "notes/DE/2026-07-13_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the filings themselves make: we expect Deere's diversified portfolio to cushion the large-agriculture downcycle in FY2026 -- Production & Precision Ag (Large Ag) net sales are guided DOWN 5-10% against a U.S./Canada large-ag industry guided down 15-20%, but Small Ag & Turf (up ~15%) and Construction & Forestry (up ~20%) are guided up enough that we expect consolidated net income to hold roughly near FY2025's ~$5.0B rather than falling materially further, i.e. an approaching cyclical trough rather than an accelerating decline."
    rationale: "Q2 FY2026 8-K segment outlook: PPA net sales down 5-10%, SAT up ~15%, C&F up ~20%; industry outlook has U.S./Canada Large Ag down 15-20% while C&F categories are flat-to-up. FY2025 10-K: net income attributable to Deere fell to $5,027M from $7,100M on the ag downcycle. Our 'near-trough, portfolio-cushioned' read is an extrapolation of that segment mix, not a forecast the filings assert -- Deere's own guide is the $4.5-5.0B net-income range, which is modestly below FY2025."
  - id: "DE-FY2026-initiation-trade_ag_risk"
    ticker: "DE"
    timestamp: "2026-07-13T16:30:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "trade_and_ag_cycle_risk_qualitative"
    unit: "n/a"
    basis: "gaap"
    source_note: "notes/DE/2026-07-13_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the filings themselves make: we see the two dominant swing factors to Deere's FY2026 net-income guide as (1) the evolving global tariff/trade regime -- Deere booked roughly $600M of direct incremental tariff cost in FY2025 and is a net U.S. exporter of ag/turf equipment exposed to retaliatory tariffs -- and (2) the depth and duration of the Large Ag downcycle driven by weak row-crop farm income. Either could move the print within or outside the guided band."
    rationale: "FY2025 10-K 'Global Trade Policies': ~$600M direct incremental tariff impact in 2025 (excluding supplier/demand effects), ~80% of domestic sales assembled in the U.S., retaliatory-tariff exposure as a net exporter; 'Agricultural Market Business Cycle': lower volumes, greater sales-incentive reliance, elevated receivable write-offs in 2025. These are the filing-disclosed risks our call names as the swing factors; the direction/magnitude bet is ours, not the filing's."
---

# DE -- Initiation: Deere & Company

*Initiation note: sets our baseline thesis on Deere from the FY2025 10-K (fiscal year
ended November 2, 2025; filed 2025-12-18) and the Q2 FY2026 earnings 8-K (filed
2026-05-21). Unlike a preview note, this is not graded against a prior quarter's
guidance -- it establishes the calls above as the tracked baseline for future
flashes/reviews. Deere is one of the desk's two deliberate decorrelators (industrials /
agriculture), uncorrelated with the AI-capex cycle that drives most of the book.*

## Business

Deere is a global leader in agricultural, turf, construction, and forestry equipment,
managed through four operating segments: **Production & Precision Agriculture (PPA)** --
large ag (high-horsepower tractors, combines, precision-ag technology); **Small
Agriculture & Turf (SAT)**; **Construction & Forestry (CF)**; and **Financial Services
(FS)**, which finances John Deere equipment. Deere guides FY2026 net income
attributable to Deere & Company as a plain **GAAP dollar range** -- the cleanest,
least-basis-ambiguous call on the coverage board.

FY2025 (ended November 2, 2025) was a down year in the agricultural cycle: total net
sales and revenues fell to **$45,684M** (from $51,716M in FY2024), net income
attributable to Deere fell to **$5,027M** (from $7,100M), and diluted EPS fell to
**$18.50** (from $25.62). Management attributes the decline to lower shipment volumes
amid weak row-crop farm fundamentals, greater reliance on sales incentives, and elevated
receivable write-offs, plus roughly **$600M** of direct incremental tariff cost.

The most recent print (Q2 FY2026, quarter ended May 3, 2026) shows the portfolio split
clearly: **net income $1,773M, EPS $6.55** (vs. $1,804M / $6.64 a year ago), with
first-half net income of **$2,429M**. By segment for the quarter, PPA net sales were
**$4,503M (-14%)** with operating profit down 39%, while SAT net sales were **$3,485M
(+16%)** and CF net sales **$3,790M (+29%)** with CF operating profit up 48% -- the
smaller-equipment and construction lines are offsetting Large Ag weakness. The quarter
also included a **$272M** recovery of IEEPA-related tariffs following a February 20, 2026
U.S. Supreme Court decision invalidating those tariffs.

## What we're tracking

- **FY2026 net income vs. Deere's own $4.5-5.0B GAAP guide** (maintained in the Q2 FY2026
  8-K) -- our baseline call is that the year lands inside the reaffirmed band.
- **Segment mix / the ag trough.** FY2026 segment outlook: PPA net sales down 5-10%, SAT
  up ~15%, CF up ~20%; the U.S./Canada Large Ag industry is guided down 15-20%. Whether
  SAT + CF strength continues to cushion the Large Ag downcycle is our core decorrelator
  thesis, and our C&F-net-sales call leans above the ~20% guide.
- **Trade / tariff regime.** ~$600M of direct FY2025 tariff cost, net-exporter exposure
  to retaliation, and the still-evolving IEEPA situation (a $272M recovery already booked
  in Q2) -- a swing factor to the net-income guide in either direction.
- **Right-to-repair litigation.** The FTC + state-AG antitrust suit (filed January 2025)
  is an open legal/regulatory overhang; Deere reports preliminary resolution discussions.
- **Capital allocation.** Deere repurchased $500M of stock and paid $878M of dividends in
  H1 FY2026 -- through-cycle capital return to watch against the earnings trough.

## Model

`models/DE/DE_model_2026-07-13.xlsx` -- built via `scripts/build_model.py DE` against
companyfacts XBRL (trailing 8 quarters + our-estimates tab). Two important model caveats
specific to DE: (1) Deere stopped tagging a standalone `GrossProfit` (last ~2020) and
`OperatingIncomeLoss` (last ~2023) under those us-gaap concepts, so those Income
Statement rows are intentionally **blank** (the builder anchors to Revenue's period set
and leaves a stale/renamed tag empty rather than mislabeling old data) -- and a known
open build_model defect (`notes/_inbox/gate2_build_model_followups.md` item 1) means the
Gross/Operating **margin %** rows compute `0.0%` off those blank cells rather than
showing blank, so **ignore the 0.0% margin rows for DE**; the real segment operating
profits are in the 8-K and cited above. (2) Deere's segment net sales / operating profit
(PPA, SAT, CF, FS) are not in companyfacts (headline-only) and are cited directly to the
8-K. The model carries consolidated net-sales-and-revenues, net income, and EPS history.

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
