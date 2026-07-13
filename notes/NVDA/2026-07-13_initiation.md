---
ticker: "NVDA"
type: initiation
event_date: "2026-07-13"
published_at: "2026-07-13T15:00:00Z"
period: "FY2026"
fiscal_year_end: "January"
basis: "non_gaap"
source_filings:
  - description: "FY2026 10-K (filed 2026-02-25) -- business narrative, reportable segments, MD&A results of operations, China/export-control risk"
    url: "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm"
  - description: "companyfacts XBRL (headline financials/history)"
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json"
  - description: "Q1 FY2027 earnings 8-K (EX-99.1), filed 2026-05-20 -- current-quarter actuals and Q2 FY2027 outlook"
    url: "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000051/q1fy27pr.htm"
fact_check:
  status: passed
  run_at: "2026-07-13T16:15:00Z"
  notes: "13/13 claims verified against their cited EDGAR filings on first pass. All 11 numeric claims (Q2 FY2027 revenue + non-GAAP gross-margin guidance from the Q1 FY2027 8-K, plus 9 FY2026 10-K / Q1 FY2027 8-K facts) matched their sources with verbatim evidence. Both qualitative thesis calls (Data Center demand, China optionality) survived the adversarial refutation pass, each supported by its cited filing. Nothing cut or flagged."
calls:
  - id: "NVDA-FY2027Q2-initiation-revenue"
    ticker: "NVDA"
    timestamp: "2026-07-13T15:00:00Z"
    call_type: initiation
    period: "FY2027Q2"
    metric: "revenue"
    unit: "USD_M"
    basis: "non_gaap"
    source_note: "notes/NVDA/2026-07-13_initiation.md"
    higher_is_better: true
    confidence: 0.55
    call:
      kind: direction
      value: "beat"
      benchmark:
        kind: range
        low: 89180.0
        high: 92820.0
    rationale: "Management guided Q2 FY2027 revenue to $91.0B +/- 2% ($89.18-92.82B) in the Q1 FY2027 8-K, and explicitly stated the outlook assumes NO Data Center compute revenue from China. Q1 FY2027 revenue was already a record $81.6B (+85% Y/Y, +20% Q/Q) with Data Center at $75.2B; with Blackwell/Blackwell Ultra at full ramp, the Rubin platform on a one-year cadence, and Data Center networking up 199% Y/Y, we call the print landing at or above the top of the guided band -- the China exclusion is conservative optionality baked out of the guide, not out of demand."
  - id: "NVDA-FY2027Q2-initiation-non_gaap_gross_margin"
    ticker: "NVDA"
    timestamp: "2026-07-13T15:00:00Z"
    call_type: initiation
    period: "FY2027Q2"
    metric: "non_gaap_gross_margin"
    unit: "pct"
    basis: "non_gaap"
    source_note: "notes/NVDA/2026-07-13_initiation.md"
    higher_is_better: true
    confidence: 0.6
    call:
      kind: point
      value: 75.0
      tolerance: 0.5
    rationale: "Management guided Q2 FY2027 non-GAAP gross margin to 75.0% +/- 50 bps in the Q1 FY2027 8-K. Q1 FY2027 non-GAAP gross margin was 75.0% (GAAP 74.9%), fully recovered from the FY2026 dip to 71.1% that was driven by the Hopper-to-Blackwell system transition and the one-time $4.5B H20 charge. We call the guided level as the base case. NOTE the basis change: beginning Q1 FY2027 NVIDIA's non-GAAP measures NO LONGER exclude stock-based compensation (historical non-GAAP was restated to include it), so this call and any future actual are on the new SBC-inclusive non-GAAP basis -- consistent with each other, but not with pre-FY2027 non-GAAP margins."
  - id: "NVDA-FY2027-initiation-datacenter_thesis"
    ticker: "NVDA"
    timestamp: "2026-07-13T15:00:00Z"
    call_type: initiation
    period: "FY2027"
    metric: "data_center_demand_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/NVDA/2026-07-13_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the FY2026 10-K itself makes: we expect Data Center (compute + networking) to remain the overwhelming growth driver through FY2027 and demand to stay effectively supply/capacity-constrained rather than demand-constrained, on the Blackwell -> Blackwell Ultra (GB300) -> Rubin one-year product cadence and the continued networking ramp (NVLink/Ethernet/InfiniBand). We explicitly flag the 10-K's own gating risk as the thing to watch against this call: the availability of data centers, energy, and capital to build out AI infrastructure -- NVIDIA states any shortage of these could impact its future revenue."
    rationale: "FY2026 10-K: Data Center revenue up 68% Y/Y, with Data Center computing +59% and Data Center networking +142%; Blackwell represented the majority of Data Center revenue; Rubin is on a one-year cadence and Blackwell Ultra/GB300 began shipping in Q2 FY2026. Q1 FY2027 8-K: Data Center revenue a record $75.2B (+92% Y/Y), networking +199% Y/Y. The 10-K's 'Recent Developments' section itself names data-center/energy/capital availability as the crucial constraint on customer buildouts -- our call is that this is a supply-side gate, not a demand shortfall, which is our extrapolation and not a forecast the filing makes."
  - id: "NVDA-FY2027-initiation-china_optionality"
    ticker: "NVDA"
    timestamp: "2026-07-13T15:00:00Z"
    call_type: initiation
    period: "FY2027"
    metric: "china_datacenter_optionality_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/NVDA/2026-07-13_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the FY2026 10-K itself makes: we treat China Data Center compute as a genuine swing factor that is deliberately excluded from NVIDIA's own Q2 FY2027 guide, and we hold it OUT of our base thesis as upside optionality rather than expected revenue. The H20/H200 export-license regime is the key uncertainty -- a re-opening would be upside NVIDIA has not guided, while the licensing/tariff overhang (incl. the 25% U.S. import tariff on H200s shipped under the new program) is the corresponding downside."
    rationale: "Q1 FY2027 8-K: NVIDIA states its Q2 outlook 'is not assuming any Data Center compute revenue from China.' FY2026 10-K: a $4.5B H20 charge was taken in Q1 FY2026 when a USG export license became required; in August 2025 the USG granted licenses allowing certain H20 shipments to China, under which NVIDIA generated ~$60M of revenue; in February 2026 the USG granted a license to ship small amounts of H200 to specific China customers, but NVIDIA had generated no revenue under it as of the filing, the H200s must pass a U.S. inspection, and any so shipped are subject to a 25% U.S. import tariff. Treating China DC compute as excluded optionality is our stance, consistent with -- but not asserted as a forecast by -- these filings."
---

# NVDA -- Initiation: NVIDIA Corporation

*Initiation note: sets our baseline thesis on NVIDIA from the FY2026 10-K (fiscal year
ended January 25, 2026; filed 2026-02-25) and the Q1 FY2027 earnings 8-K (filed
2026-05-20). Unlike a preview note, this is not graded against a prior quarter's
guidance -- it establishes the calls above as the tracked baseline for future
flashes/reviews.*

## Business

NVIDIA is, in its own FY2026 10-K framing, "a data center scale AI infrastructure
company reshaping all industries." It reports two operating segments: **Compute &
Networking** (Data Center accelerated computing and networking platforms, AI software,
and Automotive/autonomous-vehicle platforms) and **Graphics** (Gaming GPUs,
Professional Visualization, and related). FY2026 (ended January 25, 2026) revenue was
**$215.9B, up 65%** year over year, split Compute & Networking **$193.5B (+67%)** and
Graphics **$22.5B (+57%)**. GAAP gross margin was **71.1%** (down 3.9 pts from 75.0% in
FY2025), GAAP operating income **$130.4B**, GAAP net income **$120.1B**, and GAAP
diluted EPS **$4.90** (up 67%).

Within the business, Data Center revenue grew **68%** in FY2026 (Data Center computing
+59% on Blackwell demand, Data Center networking +142% on NVLink fabric for GB200/GB300
plus Ethernet/InfiniBand), with Blackwell representing the majority of Data Center
revenue; Gaming was +41%, Professional Visualization +70%, and Automotive +39%. Revenue
is highly concentrated: in FY2026 one direct customer was **22%** of total revenue and
another **14%**, both primarily Compute & Networking.

Two structural items frame the forward story. First, **the FY2026 gross-margin dip to
71.1%** was driven by the Hopper-HGX-to-Blackwell-full-system transition plus a one-time
**$4.5B H20 charge** (excess inventory / purchase obligations after an April-2025 U.S.
export-license requirement); non-GAAP gross margin was already back to **75.0%** by Q1
FY2027. Second, **China**: after the H20 charge, the USG granted limited H20 licenses in
August 2025 (~$60M realized) and a small H200 license in February 2026 (none realized as
of the 10-K, subject to U.S. inspection and a 25% import tariff) -- and NVIDIA's own Q2
FY2027 guide assumes *no* China Data Center compute revenue at all.

## What we're tracking

- **Q2 FY2027 revenue and non-GAAP gross margin vs. NVIDIA's own guide** ($91.0B +/- 2%
  revenue, 75.0% +/- 50 bps non-GAAP gross margin, per the Q1 FY2027 8-K) -- our
  baseline calls above lean to a revenue beat (the guide excludes China DC compute) and
  take the guided margin as base case.
- **The two framework transitions announced with Q1 FY2027.** NVIDIA is (a) moving to a
  new market-platform reporting structure -- **Data Center** (Hyperscale + ACIE) and
  **Edge Computing** -- replacing the Compute & Networking / Graphics segment view used
  in the FY2026 10-K, and (b) as of Q1 FY2027, **no longer excluding stock-based
  compensation from its non-GAAP measures** (historical non-GAAP restated to match). The
  second change matters for grading: our non-GAAP margin call is on the new SBC-inclusive
  basis, not comparable to pre-FY2027 non-GAAP.
- **Data Center supply/capacity gate.** The 10-K names data-center, energy, and capital
  availability as the crucial constraint on customer buildouts -- the risk our
  "supply-constrained, not demand-constrained" thesis is measured against.
- **China optionality.** Any re-opening of China Data Center compute is upside NVIDIA has
  not guided; the H20/H200 license-and-tariff regime is the swing factor we hold out of
  the base case.
- **Capital return.** NVIDIA returned ~$20.0B to shareholders in Q1 FY2027, had $38.5B
  remaining under its buyback authorization, then added **$80.0B** more (approved May 18,
  2026) and raised the quarterly dividend from $0.01 to $0.25/share -- a
  capital-allocation signal to watch alongside the ~$120B FY2026 net-income base.

## Model

`models/NVDA/NVDA_model_2026-07-13.xlsx` -- built via `scripts/build_model.py NVDA`
against companyfacts XBRL (trailing 8 quarters of headline financials + margin/growth
formulas + our-estimates tab). Two model notes: (1) segment/market-platform detail (Data
Center, Compute & Networking, Graphics, Gaming, etc.) is **not** in companyfacts
(headline-only, per the Session 2 structural finding) -- the segment and Data Center
figures above are cited directly to the FY2026 10-K and the Q1 FY2027 8-K, not the model;
(2) the model retains **as-originally-reported (earliest-filed)** figures, so the two
pre-split quarters that predate NVIDIA's June-2024 10-for-1 stock split show pre-split
diluted EPS (the build logged this as a filing-to-filing disagreement, resolved to
earliest-filed by design) -- a labeling artifact of the split, not a data error.

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
