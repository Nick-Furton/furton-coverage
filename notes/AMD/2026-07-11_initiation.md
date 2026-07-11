---
ticker: "AMD"
type: initiation
event_date: "2026-07-11"
published_at: "2026-07-11T16:00:00Z"
period: "FY2025"
fiscal_year_end: "December"
basis: "non_gaap"
source_filings:
  - description: "FY2025 10-K (filed 2026-02-04) -- business narrative, segments, MD&A"
    url: "https://www.sec.gov/Archives/edgar/data/2488/000000248826000018/amd-20251227.htm"
  - description: "companyfacts XBRL (headline financials/history)"
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0000002488.json"
  - description: "Q1 FY2026 earnings 8-K (EX-99.1), filed 2026-05-05 -- current-quarter actuals and Q2 FY2026 outlook"
    url: "https://www.sec.gov/Archives/edgar/data/2488/000000248826000072/q12026991.htm"
fact_check:
  status: passed
  run_at: "2026-07-11T18:30:00Z"
  notes: "12/12 claims verified. All 10 numeric claims (Q2 FY2026 revenue/margin guidance + 8 FY2025 10-K facts) matched their cited filings on first pass. Both qualitative thesis calls initially failed the refutation pass: the drafted datacenter_thesis claim mis-stated the FY2025 relationship (Client & Gaming actually outgrew Data Center, 51% vs 32%) and cited a nonexistent 'MI400' product; the margin_recovery claim was phrased as if the 10-K itself projected FY2026 margin. Both calls were corrected -- reframed explicitly as our own forward view (not the filing's), the segment-growth error fixed, and the fictional product name removed -- and passed on re-verification."
calls:
  - id: "AMD-FY2026Q2-initiation-revenue"
    ticker: "AMD"
    timestamp: "2026-07-11T16:00:00Z"
    call_type: initiation
    period: "FY2026Q2"
    metric: "revenue"
    unit: "USD_M"
    basis: "non_gaap"
    source_note: "notes/AMD/2026-07-11_initiation.md"
    higher_is_better: true
    confidence: 0.6
    call:
      kind: direction
      value: "beat"
      benchmark:
        kind: range
        low: 10900.0
        high: 11500.0
    rationale: "Management guided Q2 FY2026 revenue to ~$11.2B +/- $300M in the Q1 FY2026 8-K. Data Center demand for Instinct MI350-series GPUs was already described as strong entering the quarter, and the October 2025 OpenAI product-purchase agreement (6 GW of AMD GPUs, first tranche on MI450) is an incremental demand signal not yet reflected in the base guide, so we call the print landing at or above the top of the guided band."
  - id: "AMD-FY2026Q2-initiation-non_gaap_gross_margin"
    ticker: "AMD"
    timestamp: "2026-07-11T16:00:00Z"
    call_type: initiation
    period: "FY2026Q2"
    metric: "non_gaap_gross_margin"
    unit: "pct"
    basis: "non_gaap"
    source_note: "notes/AMD/2026-07-11_initiation.md"
    higher_is_better: true
    confidence: 0.55
    call:
      kind: point
      value: 56.0
      tolerance: 0.5
    rationale: "Management guided non-GAAP gross margin to ~56% for Q2 FY2026. FY2025 GAAP gross margin already recovered to 50% (from 49% in FY2024) despite ~$440M of net MI308 export-control inventory charges; with the bulk of that charge reversed in Q4 FY2025 and Data Center mix continuing to richen, we see the guided level as achievable without further one-time drag."
  - id: "AMD-FY2026-initiation-datacenter_thesis"
    ticker: "AMD"
    timestamp: "2026-07-11T16:00:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "data_center_revenue_growth_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/AMD/2026-07-11_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the FY2025 10-K itself makes: we expect AMD's Data Center segment to reaccelerate and outgrow Client & Gaming in FY2026, reversing the FY2025 pattern (Client & Gaming's 51% revenue growth actually outpaced Data Center's 32% that year), on the Instinct MI350/MI450 GPU ramp, the 5th Gen EPYC ramp, and the October 2025 OpenAI multiyear GPU-deployment agreement (6 GW, first gigawatt on MI450)."
    rationale: "FY2025 10-K: Data Center net revenue grew 32% to $16.6B versus 51% for Client & Gaming and -3% for Embedded -- Client & Gaming was actually the faster grower in FY2025, which our call explicitly expects to reverse. The OpenAI agreement (signed October 2025, so largely outside the FY2025 P&L) and the Helios rack-scale platform preview are the disclosed catalysts we're leaning on for that reversal; the filing does not itself forecast FY2026 segment growth."
  - id: "AMD-FY2026-initiation-margin_recovery"
    ticker: "AMD"
    timestamp: "2026-07-11T16:00:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "gross_margin_trajectory_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/AMD/2026-07-11_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the FY2025 10-K itself makes: we expect AMD's gross margin to continue trending upward in FY2026 as the FY2025 MI308 export-control inventory charges (net ~$440M) roll off further and Data Center mix richens, though we note two filing-disclosed risks that could cut against this -- continued uncertainty over China export licensing for MI308 (including a possible 15%-of-revenue government levy not yet formalized as of the filing) and new competitive pressure flagged from the September 2025 Nvidia-Intel partnership/investment."
    rationale: "FY2025 10-K MD&A: gross margin improved to 50% in FY2025 (from 49% in FY2024) even while absorbing the net MI308 charge, and $360M of the ~$800M Q2 FY2025 charge was already reversed in Q4 FY2025 after the government granted export licenses for certain China shipments. The 10-K itself gives no FY2026 margin guidance and separately flags ongoing inventory-writedown and competitive-pricing risk in its Risk Factors -- our upward call is an extrapolation of the FY2025 trend, not something the filing asserts, and we note the offsetting risks explicitly rather than ignoring them."
---

# AMD -- Initiation: Advanced Micro Devices, Inc.

*Initiation note: sets our baseline thesis on AMD from the FY2025 10-K (filed 2026-02-04)
and the Q1 FY2026 earnings 8-K (filed 2026-05-05). Unlike a preview note, this is not
graded against a prior quarter's guidance -- it establishes the calls above as the
tracked baseline for future flashes/reviews.*

## Business

AMD reports three segments: **Data Center** (server CPUs, Instinct-series AI
accelerator GPUs, DPUs, AI NICs, FPGAs), **Client and Gaming** (Ryzen desktop/notebook
CPUs and APUs, Radeon discrete GPUs, semi-custom game-console SoCs -- combined into one
reportable segment starting FY2025), and **Embedded** (embedded CPUs/APUs/FPGAs/SoCs).
FY2025 net revenue was $34.6B, up 34% year over year: Data Center $16.6B (+32%), Client
and Gaming $14.6B (+51%), Embedded $3.5B (-3%). GAAP gross margin was 50% (vs. 49% in
FY2024); GAAP diluted EPS was $2.65 for FY2025.

Two 2025 corporate actions matter to the thesis: the March 2025 acquisition of ZT
Systems (retaining design/IP and talent, with the manufacturing business subsequently
sold to Sanmina in October 2025) accelerates AMD's ability to deliver full
rack-scale AI systems rather than just chips; and the October 2025 OpenAI product
purchase agreement -- 6 gigawatts of AMD GPU deployment, with the first gigawatt on
the upcoming MI450 series, paired with a warrant for up to 160M AMD shares vesting on
purchase/stock-price milestones -- is a demand commitment from one of the largest AI
compute buyers, not yet reflected in prior guidance cycles.

## What we're tracking

- **Q2 FY2026 revenue and non-GAAP gross margin vs. AMD's own guide** (~$11.2B +/-
  $300M revenue, ~56% non-GAAP gross margin, per the Q1 FY2026 8-K) -- our baseline
  calls above lean toward a beat, on the view that Instinct MI350 demand and the
  OpenAI agreement are incremental to a guide set before the deal's full scope was
  public.
- **Segment mix**: whether Data Center reverses FY2025's pattern and outgrows Client &
  Gaming in FY2026 -- notably, Client & Gaming was the faster-growing segment in FY2025
  (+51% vs. Data Center's +32%), so this is a forward call of ours, not an extrapolation
  of the prior year's trend.
- **Gross margin trajectory**: whether the FY2025 MI308 export-control inventory drag
  (net ~$440M, ~$800M booked in Q2 FY2025 with ~$360M reversed in Q4 after licenses
  were granted) is fully behind AMD, or whether further export-policy shifts reopen
  that risk -- the China licensing regime is explicitly called out in the 10-K as
  still evolving (no final regulation on the reported 15%-of-China-revenue
  expectation as of the filing date).
- **Repurchase pace**: $9.4B remained available under the $14B buyback authorization
  as of December 27, 2025, after $1.3B returned to shareholders in FY2025 -- a
  capital-allocation signal to watch alongside the OpenAI-warrant dilution overhang.

## Model

`models/AMD/AMD_model_2026-07-11.xlsx` -- built via `scripts/build_model.py AMD`
against companyfacts XBRL (trailing 8 quarters, headline financials + our-estimates
tab). Segment-level detail (Data Center / Client & Gaming / Embedded revenue) is not
in companyfacts (headline-only, per the Session 2 structural finding) -- the model
carries consolidated revenue/margin/EPS history only; segment figures above are cited
directly to the 10-K.

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
