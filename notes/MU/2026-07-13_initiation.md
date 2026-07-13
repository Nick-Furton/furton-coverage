---
ticker: "MU"
type: initiation
event_date: "2026-07-13"
published_at: "2026-07-13T17:00:00Z"
period: "FY2025"
fiscal_year_end: "August/September"
basis: "non_gaap"
source_filings:
  - description: "FY2025 10-K (fiscal year ended August 28, 2025; filed 2025) -- business narrative, DRAM/NAND and business-unit revenue, MD&A results of operations, gross-margin and cyclicality risk factors"
    url: "https://www.sec.gov/Archives/edgar/data/723125/000072312525000028/mu-20250828.htm"
  - description: "companyfacts XBRL (headline financials/history)"
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0000723125.json"
  - description: "Q3 FY2026 earnings 8-K (EX-99.1), filed 2026-06-24 -- Q3 FY2026 actuals (ended May 28, 2026) and Q4 FY2026 outlook"
    url: "https://www.sec.gov/Archives/edgar/data/723125/000072312526000013/a2026q3ex991-pressrelease.htm"
fact_check:
  status: passed
  run_at: "2026-07-13T17:40:00Z"
  notes: "14/14 claims verified against their cited EDGAR filings on first pass. All 12 numeric claims (Q4 FY2026 revenue $50.0B +/-1B, non-GAAP gross margin ~86%, and non-GAAP EPS $31.00 +/-1.00 guides; Q3 FY2026 revenue/EPS/gross margin; FY2025 revenue/gross margin/net income; FY2025 DRAM/NAND/CMBU revenue) matched their sources with verbatim evidence. Both qualitative thesis calls (HBM/AI-memory demand, DRAM pricing-cycle) survived the adversarial refutation pass. Nothing cut or flagged."
calls:
  - id: "MU-FY2026Q4-initiation-revenue"
    ticker: "MU"
    timestamp: "2026-07-13T17:00:00Z"
    call_type: initiation
    period: "FY2026Q4"
    metric: "revenue"
    unit: "USD_M"
    basis: "non_gaap"
    source_note: "notes/MU/2026-07-13_initiation.md"
    higher_is_better: true
    confidence: 0.6
    call:
      kind: direction
      value: "beat"
      benchmark:
        kind: range
        low: 49000.0
        high: 51000.0
    rationale: "Management guided Q4 FY2026 revenue to $50.0B +/- $1.0B in the Q3 FY2026 8-K (the guide is identical on a GAAP and non-GAAP basis -- there is no revenue adjustment). Q3 FY2026 revenue was already a record $41.46B (up from $23.86B the prior quarter and $9.30B a year earlier), and CEO Sanjay Mehrotra framed Q4 as an 'even stronger outlook,' pointing to multi-year Strategic Customer Agreements meant to make revenue more durable and predictable. With HBM4 in high-volume shipments for the lead customer's platform, DRAM pricing still rising into an AI-driven demand environment the 10-K describes as outpacing industry supply, and Micron shifting DRAM supply toward higher-value data-center markets, we call the print landing at or above the top of the guided band."
  - id: "MU-FY2026Q4-initiation-non_gaap_gross_margin"
    ticker: "MU"
    timestamp: "2026-07-13T17:00:00Z"
    call_type: initiation
    period: "FY2026Q4"
    metric: "non_gaap_gross_margin"
    unit: "pct"
    basis: "non_gaap"
    source_note: "notes/MU/2026-07-13_initiation.md"
    higher_is_better: true
    confidence: 0.55
    call:
      kind: point
      value: 86.0
      tolerance: 1.0
    rationale: "Management guided Q4 FY2026 non-GAAP gross margin to approximately 86% in the Q3 FY2026 8-K. Non-GAAP gross margin was already 84.9% in Q3 FY2026 (GAAP 84.6%), up sharply from 74.9% the prior quarter and 39.0% a year earlier, on rising DRAM average selling prices and a richer HBM/data-center mix. We take the guided ~86% as the base case rather than betting on a large miss or beat: the sequential step-up implied is modest relative to the moves already delivered, and per-gigabit cost reductions plus continued mix shift support it. The 10-K's own risk factors -- shifts in product mix and the possibility that ASP declines outpace cost reductions -- are the offsets to a further leg up."
  - id: "MU-FY2026-initiation-hbm_ai_memory_thesis"
    ticker: "MU"
    timestamp: "2026-07-13T17:00:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "hbm_ai_memory_demand_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/MU/2026-07-13_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the filing itself makes: we expect HBM and AI-driven data-center memory demand to remain the dominant growth driver for Micron through FY2026, with the Cloud Memory business unit (which houses HBM) staying the fastest-growing unit as HBM4 moves through high-volume ramp on the lead customer's platform. We explicitly flag the filing-disclosed risk that cuts against this: the 10-K describes memory as a deeply cyclical industry where AI-driven demand is currently outpacing supply, but where a swing to oversupply, or ASP declines that outpace per-gigabit cost reductions, could reverse pricing and margins quickly (the FY2023 downturn, with $1.831B of inventory write-downs and a negative-9% consolidated gross margin, is the filing's own recent proof of how fast that can happen)."
    rationale: "FY2025 10-K: Cloud Memory Business Unit (CMBU) revenue was $13,524M (36% of total, up 257% Y/Y), driven by HBM, high-capacity DIMMs, and low-power server DRAM for AI cloud-server demand; the MD&A states AI-driven demand is accelerating and outpacing industry supply, and that Micron shifted DRAM supply toward higher-value data-center markets. Q3 FY2026 8-K product highlights: HBM4 (on 1-beta DRAM) is in high-volume shipments for the lead customer's platform and HBM4E (1-gamma) is targeted for volume production in calendar 2027. The 10-K's Risk Factors themselves warn that gross margins can be hurt by ASP declines, product-mix shifts, and the memory cycle -- so our sustained-demand call is our extrapolation, not a forecast the filing makes, and the cyclicality/oversupply risk is the disclosed counterweight."
  - id: "MU-FY2026-initiation-dram_pricing_cycle_thesis"
    ticker: "MU"
    timestamp: "2026-07-13T17:00:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "dram_pricing_cycle_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/MU/2026-07-13_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the filing itself makes: we expect DRAM to stay the primary earnings engine and DRAM pricing/margins to hold up better than NAND through FY2026, given Micron's stated strategy of shifting DRAM supply toward higher-value data-center segments and managing NAND supply/technology cadence more conservatively. The filing-disclosed risk that cuts against this is memory-market cyclicality: the 10-K attributes FY2025's gains to constrained supply and rising ASPs (DRAM ASPs up a low-40% range in FY2025), conditions that are demand- and supply-balance dependent and have historically reversed -- a return to oversupply or an ASP downturn would compress the very DRAM margins this thesis leans on."
    rationale: "FY2025 10-K: total revenue was $37,378M (+49% Y/Y); reported DRAM revenue was $28.58B (up 62%, on a low-40%-range ASP increase and mid-teen bit-shipment growth) versus NAND revenue of $8.50B (up 18%, on high-teen bit-shipment growth). The MD&A says Micron shifted DRAM supply to data-center/hyperscale markets and 'prudently manages' NAND to align supply growth with demand. Consolidated gross margin improved to 40% in FY2025 from 22% in FY2024, led by DRAM. The 10-K frames these as cycle-driven (supply/demand balance, ASPs) and its Risk Factors flag that the cycle can turn -- so our DRAM-leadership call is our own forward view, with cyclicality as the explicit disclosed risk, not a projection the filing itself asserts."
---

# MU -- Initiation: Micron Technology, Inc.

*Initiation note: sets our baseline thesis on Micron from the FY2025 10-K (fiscal year
ended August 28, 2025) and the Q3 FY2026 earnings 8-K (filed 2026-06-24). Micron is the
memory/HBM leg of the AI-compute supply chain -- the NVDA -> AMD -> AVGO -> MU cross-read
-- and an off-calendar reporter (fiscal year ending late August/September, quarters
reported Mar/Jun/Sep/Dec) that fills gaps the December-FY names miss. Unlike a preview
note, this is not graded against a prior quarter's guidance -- it establishes the calls
above as the tracked baseline for future flashes/reviews.*

## Business

Micron designs and manufactures memory and storage products built on its DRAM, NAND, and
NOR semiconductor technologies. It reports four business units: **Cloud Memory (CMBU)**
-- memory for large hyperscale cloud customers plus **HBM (high-bandwidth memory)** for
all data-center customers; **Core Data Center (CDBU)** -- memory/storage for mid-tier
cloud, enterprise and OEM data-center customers, including data-center SSDs; **Mobile and
Client (MCBU)** -- smartphone and PC memory/storage plus Crucial-branded consumer
products; and **Automotive and Embedded (AEBU)**.

FY2025 (ended August 28, 2025) revenue was **$37,378M, up 49%** year over year. By
product, reported **DRAM revenue was $28.58B** (up 62%, on a low-40%-range increase in
average selling prices and a mid-teen bit-shipment increase) and reported **NAND revenue
was $8.50B** (up 18%, on high-teen bit-shipment growth). By business unit: **CMBU
$13,524M (36% of revenue, +257%)**, **CDBU $7,229M (19%, +45%)**, **MCBU $11,859M (32%,
+2%)**, and **AEBU $4,753M (13%, +3%)** -- the AI/HBM-driven CMBU was by far the fastest
grower. GAAP consolidated **gross margin was 40%** ($14,873M, up from 22% in FY2024),
GAAP **operating income $9,770M (26%)**, and GAAP **net income $8,539M**. The 10-K's own
framing: "AI-driven demand is accelerating and is outpacing industry supply," with Micron
shifting DRAM supply toward higher-value data-center markets, emphasizing HBM.

The forward story is the AI-memory upcycle. In Q3 FY2026 (ended May 28, 2026), reported
in the June-24 8-K, revenue was a record **$41.46B** (versus $23.86B the prior quarter and
$9.30B a year earlier), non-GAAP diluted **EPS $25.11** (GAAP $24.67), and non-GAAP
**gross margin 84.9%** (GAAP 84.6%). CEO Sanjay Mehrotra tied the results and the "even
stronger" Q4 outlook to "the strategic value of memory in the AI era" and to multi-year
**Strategic Customer Agreements** intended to make revenue more durable and predictable.
On product, **HBM4** (built on 1-beta DRAM) is in high-volume shipments for the lead
customer's platform, and **HBM4E** (1-gamma) is targeted for volume production in
calendar 2027. Micron declared a $0.15/share quarterly dividend and ended Q3 FY2026 with
$30.2B of cash, marketable investments and restricted cash.

## What we're tracking

- **Q4 FY2026 revenue and non-GAAP gross margin vs. Micron's own guide** ($50.0B +/-
  $1.0B revenue -- identical GAAP and non-GAAP -- and approximately 86% non-GAAP gross
  margin, per the Q3 FY2026 8-K). Our baseline calls above lean to a revenue beat (record
  Q3, "even stronger" Q4 language, HBM4 ramp, Strategic Customer Agreements) and take the
  guided ~86% margin as base case. Micron also guided Q4 FY2026 non-GAAP **EPS of $31.00
  +/- $1.00** (GAAP $30.73 +/- $1.00) on ~1.15B diluted shares.
- **HBM / AI-memory demand.** Whether CMBU (which houses HBM) stays the dominant growth
  driver as HBM4 ramps and HBM4E approaches -- against the 10-K's disclosed memory-cycle
  risk that oversupply or ASP declines could reverse pricing and margins.
- **DRAM vs. NAND.** Whether DRAM (up 62% in FY2025 on a low-40%-range ASP increase)
  remains the earnings engine and holds margin better than NAND, given Micron's stated
  supply-shift-to-data-center strategy and more conservative NAND supply management.
- **Cyclicality.** The 10-K's own recent proof that the cycle turns fast: the FY2023
  downturn carried $1.831B of inventory NRV write-downs and a negative-9% consolidated
  gross margin. AI demand "outpacing supply" today is a supply/demand-balance condition,
  not a permanent state.

## Model

`models/MU/MU_model_2026-07-13.xlsx` -- built via `scripts/build_model.py MU` against
companyfacts XBRL (trailing quarters of headline financials + margin/growth formulas +
our-estimates tab). Model note: DRAM/NAND product mix and business-unit revenue (CMBU /
CDBU / MCBU / AEBU) and HBM detail are **not** in companyfacts (headline-only, per the
Session 2 structural finding) -- those figures above are press-release / 10-K-sourced
(the FY2025 splits from the 10-K MD&A, the Q3 FY2026 actuals and Q4 FY2026 guidance from
the 8-K EX-99.1), not from the model, which carries consolidated revenue/margin/EPS
history only.

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
