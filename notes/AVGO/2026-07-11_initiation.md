---
ticker: "AVGO"
type: initiation
event_date: "2026-07-11"
published_at: "2026-07-11T18:00:00Z"
period: "FY2025"
fiscal_year_end: "November"
basis: "non_gaap"
source_filings:
  - description: "FY2025 10-K (filed 2025-12-18) -- business narrative, segments, MD&A"
    url: "https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm"
  - description: "companyfacts XBRL (headline financials/history)"
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0001730168.json"
  - description: "Q2 FY2026 earnings 8-K (EX-99), filed 2026-06-03 -- current-quarter actuals and Q3 FY2026 outlook"
    url: "https://www.sec.gov/Archives/edgar/data/1730168/000173016826000051/avgo-05032026x8kxex99.htm"
fact_check:
  status: passed
  run_at: "2026-07-11T19:30:00Z"
  notes: "8/8 claims verified. 6 numeric claims (Q3 FY2026 revenue/margin guidance + 4 FY2025 10-K facts) matched on first pass. The custom-silicon-thesis qualitative call passed on first pass. The VCF-software-margin thesis initially failed: it cited ongoing labor-cost synergies as a forward driver, but the 10-K discloses VMware-integration restructuring is 'substantially completed' -- most of that labor-cost tailwind is already realized, not still running off. Corrected to rest the forward call on the VCF subscription-mix shift only, and passed on re-verification."
calls:
  - id: "AVGO-FY2026Q3-initiation-revenue"
    ticker: "AVGO"
    timestamp: "2026-07-11T18:00:00Z"
    call_type: initiation
    period: "FY2026Q3"
    metric: "revenue"
    unit: "USD_M"
    basis: "non_gaap"
    source_note: "notes/AVGO/2026-07-11_initiation.md"
    higher_is_better: true
    confidence: 0.55
    call:
      kind: point
      value: 29400.0
      tolerance: 300.0
    rationale: "Management guided Q3 FY2026 revenue to approximately $29.4B (+84% YoY) in the Q2 FY2026 8-K, citing custom AI accelerator and AI networking demand as the driver. Given how much of Broadcom's AI backlog is now multi-year custom-silicon (XPU) programs with a small number of hyperscale customers, we treat the point guide itself -- not a wide band -- as the right benchmark and call it landing within a tight ~1% tolerance of the guided figure."
  - id: "AVGO-FY2026Q3-initiation-non_gaap_op_margin"
    ticker: "AVGO"
    timestamp: "2026-07-11T18:00:00Z"
    call_type: initiation
    period: "FY2026Q3"
    metric: "non_gaap_operating_margin"
    unit: "pct"
    basis: "non_gaap"
    source_note: "notes/AVGO/2026-07-11_initiation.md"
    higher_is_better: true
    confidence: 0.55
    call:
      kind: point
      value: 67.0
      tolerance: 1.0
    rationale: "Management guided Q3 FY2026 non-GAAP operating margin to approximately 67% of revenue, explicitly citing 'strong operating leverage.' FY2025 GAAP operating margin already expanded to 40% (from 26% in FY2024) on higher infrastructure-software gross margin and AI-driven semiconductor demand; the non-GAAP guide (which excludes acquisition-related amortization and stock-based comp) is consistent with that trend continuing."
  - id: "AVGO-FY2026-initiation-custom-silicon-thesis"
    ticker: "AVGO"
    timestamp: "2026-07-11T18:00:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "semiconductor_ai_revenue_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/AVGO/2026-07-11_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the FY2025 10-K itself makes: Broadcom's Semiconductor Solutions segment growth in FY2026 continues to be driven primarily by custom AI accelerators (XPUs) and AI networking products rather than the broader non-AI semiconductor business, sustaining the segment's outsized growth versus FY2024's more diversified base."
    rationale: "FY2025 10-K: Semiconductor Solutions net revenue grew 22% to $36.9B, explicitly attributed to 'strong demand for our networking solutions, primarily custom AI accelerators and AI networking products,' and one customer (a distributor within Semiconductor Solutions) accounted for 32% of net revenue in FY2025 versus 28% in FY2024 -- rising customer concentration consistent with a small number of hyperscale AI-XPU programs driving the growth. The 10-K itself gives no FY2026 revenue-driver guidance; this is our extrapolation of the FY2025 pattern."
  - id: "AVGO-FY2026-initiation-vcf-software-thesis"
    ticker: "AVGO"
    timestamp: "2026-07-11T18:00:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "infrastructure_software_margin_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/AVGO/2026-07-11_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the FY2025 10-K itself makes: Infrastructure Software segment operating income keeps growing faster than its revenue through FY2026 as the VCF subscription-license transition continues to shift the revenue mix toward higher-margin license recognition -- though we no longer lean on labor-cost synergies as a forward driver, since the 10-K discloses that VMware-integration restructuring is 'substantially completed,' meaning most of that one-time labor-cost tailwind is already realized in the FY2025 base rather than still running off."
    rationale: "FY2025 10-K: Infrastructure Software revenue grew 26% to $27.0B while segment operating income grew 49% to $20.8B (from $14.0B), driven by VCF subscription license revenue recognition and lower post-VMware-integration labor costs. Note 15 (Restructuring) states VMware-integration restructuring activities are 'substantially completed' -- so our forward call rests on the subscription-mix shift continuing, not on further labor-cost reduction, and we flag the FY2025 comparison base (VMware only a partial-year addition in FY2023) as a reason the 49% growth rate itself may not repeat even if the margin-expansion direction does."
---

# AVGO -- Initiation: Broadcom Inc.

*Initiation note: sets our baseline thesis on AVGO from the FY2025 10-K (filed
2025-12-18) and the Q2 FY2026 earnings 8-K (filed 2026-06-03). Unlike a preview note,
this is not graded against a prior quarter's guidance -- it establishes the calls above
as the tracked baseline for future flashes/reviews. AVGO's November fiscal year-end
staggers its calendar off the crowded Dec-FYE cluster elsewhere in this coverage book.*

## Business

Broadcom reports two segments: **Semiconductor Solutions** (all semiconductor product
lines and IP licensing -- including custom AI accelerators/XPUs, AI networking, and
broadband/wireless/storage silicon) and **Infrastructure Software** (private cloud via
VMware Cloud Foundation/VCF, mainframe software, cybersecurity, and Fibre Channel SAN).
FY2025 total net revenue was $63.9B, up 24% from $51.6B in FY2024: Semiconductor
Solutions $36.9B (+22%), Infrastructure Software $27.0B (+26%). GAAP gross margin
expanded to 68% (from 63%), and GAAP operating income nearly doubled to $25.5B (40%
margin, from $13.5B / 26% margin) -- Infrastructure Software operating income grew
faster (+49% to $20.8B) than its revenue, while Semiconductor Solutions operating
income grew 27% to $21.2B.

Customer concentration is notable and rising: one semiconductor-solutions distributor
customer accounted for 32% of FY2025 net revenue (up from 28% in FY2024), and the top
five end customers represented roughly 40% of net revenue in both years -- consistent
with a small number of hyperscale customers driving most of the custom-AI-accelerator
growth the 10-K credits for the semiconductor segment's expansion. Stock-based
compensation rose sharply ($7.57B vs. $5.67B in FY2024) after a two-year equity award
structure replaced the normal annual grant cycle in Q2 FY2025 -- a one-time timing
shift, not an ongoing step-change, worth remembering when comparing GAAP opex
year-over-year.

## What we're tracking

- **Q3 FY2026 revenue and non-GAAP operating margin vs. AVGO's own guide**
  (~$29.4B revenue, +84% YoY; ~67% non-GAAP operating margin; ~68% adjusted EBITDA
  margin -- all from the Q2 FY2026 8-K) -- our baseline calls treat the point guide as
  the benchmark given how few large custom-silicon programs drive the number.
- **Whether AI-related Semiconductor Solutions growth broadens beyond the current
  customer concentration** or remains dependent on a small number of hyperscale
  programs -- the 32%-from-one-distributor figure is the number to watch for
  concentration risk.
- **Infrastructure Software margin expansion** as the VMware VCF subscription
  transition and integration synergies continue -- whether operating income keeps
  outgrowing revenue in that segment as it did in FY2025 (+49% vs. +26%).
- **Stock-based compensation normalization** after the FY2025 two-year-award timing
  shift, to avoid misreading FY2026 opex trends as a margin change when it's really a
  grant-cycle artifact.

## Model

`models/AVGO/AVGO_model_2026-07-11.xlsx` -- built via `scripts/build_model.py AVGO`
against companyfacts XBRL. **Known data quirk:** the model logs a warning that diluted
EPS for two 2024 period-ends disagrees between as-filed values (e.g. $2.84 vs. $0.28
for the quarter ended 2024-02-04) -- this is Broadcom's 10-for-1 stock split completed
in July 2024, which caused later filings to restate prior-period EPS on a post-split
basis while the original as-filed value was pre-split. Per the anchoring design, the
model keeps the earliest-filed (as-originally-reported, pre-split) value rather than
silently mixing bases -- readers comparing to post-split market data should adjust.
Segment-level revenue/operating income (Semiconductor Solutions / Infrastructure
Software, AI revenue) is not in companyfacts (headline-only, per the Session 2
structural finding); those figures above are cited directly to the 10-K.

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
