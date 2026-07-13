---
ticker: "PANW"
type: initiation
event_date: "2026-07-13"
published_at: "2026-07-13T17:15:00Z"
period: "FY2025"
fiscal_year_end: "July"
basis: "non_gaap"
source_filings:
  - description: "FY2025 10-K (fiscal year ended July 31, 2025; filed 2025-08-29) -- business narrative, platform segments, MD&A results of operations, key financial metrics (NGS ARR, RPO), CyberArk pending-acquisition risk"
    url: "https://www.sec.gov/Archives/edgar/data/1327567/000132756725000027/panw-20250731.htm"
  - description: "companyfacts XBRL (headline GAAP financials/history)"
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0001327567.json"
  - description: "Q3 FY2026 earnings 8-K (EX-99.1), filed 2026-06-02 -- Q3 FY2026 actuals and Q4 FY2026 / full-year FY2026 outlook"
    url: "https://www.sec.gov/Archives/edgar/data/1327567/000132756726000012/ex991q326earningsrelease.htm"
fact_check:
  status: passed
  run_at: "2026-07-13T18:10:00Z"
  notes: "17 claims. 14 verified on first pass (both numeric calls -- Q4 FY2026 revenue and FY2026 NGS ARR guides; all FY2026 full-year guidance components; Q3 FY2026 revenue and GAAP/non-GAAP operating income; FY2025 revenue/operating income/net income/EPS/NGS ARR; both qualitative theses). Two numeric prose facts (Q3 FY2026 NGS ARR $8.1B incl $1.6B CyberArk/Chronosphere; Q3 FY2026 GAAP net loss $(177)M and non-GAAP net income $684M) FAILED on first pass as WebFetch wrong-document artifacts -- the verifiers returned FY2025 10-K content for the cited Q3 FY2026 8-K URL (S3/S6-flagged quirk). Both were corroborated by parallel claims on the SAME 8-K URL that passed (prose-q3-revenue confirmed the $388M CyberArk/Chronosphere contribution; prose-q3-op confirmed the Q3 GAAP $(183)M / non-GAAP $814M split) and re-confirmed verbatim by an isolated single-agent re-run. One GENUINE fix applied: the FY2025 RPO prose asserted a prior-year comparative ('from $12.7B, +24%') that is NOT in the cited FY2025 10-K (which carries only current-year RPO $15.8B and ~$7.0B-within-12-months) -- the unsourced comparative was removed. Status passed after that fix and re-verification; nothing else cut."
calls:
  - id: "PANW-FY2026Q4-initiation-revenue"
    ticker: "PANW"
    timestamp: "2026-07-13T17:15:00Z"
    call_type: initiation
    period: "FY2026Q4"
    metric: "revenue"
    unit: "USD_M"
    basis: "non_gaap"
    source_note: "notes/PANW/2026-07-13_initiation.md"
    higher_is_better: true
    confidence: 0.58
    call:
      kind: direction
      value: "beat"
      benchmark:
        kind: range
        low: 3345.0
        high: 3355.0
    rationale: "Management guided Q4 FY2026 total revenue to $3.345-3.355B (+32% Y/Y) in the Q3 FY2026 8-K. Q3 FY2026 revenue already grew 31% to $3.0B (including $388M from the newly consolidated CyberArk and Chronosphere acquisitions), and CEO Nikesh Arora characterized the quarter as one with 'accelerating organic bookings growth.' With a full quarter of CyberArk consolidation in Q4 versus a partial contribution in Q3, plus AI-security demand pull, we call the print landing at or above the top of the very narrow guided band."
  - id: "PANW-FY2026Q4-initiation-ngs_arr"
    ticker: "PANW"
    timestamp: "2026-07-13T17:15:00Z"
    call_type: initiation
    period: "FY2026Q4"
    metric: "ngs_arr"
    unit: "USD_M"
    basis: "non_gaap"
    source_note: "notes/PANW/2026-07-13_initiation.md"
    higher_is_better: true
    confidence: 0.55
    call:
      kind: direction
      value: "beat"
      benchmark:
        kind: range
        low: 8900.0
        high: 8950.0
    rationale: "Management guided Next-Generation Security ARR to $8.90-8.95B (+59-60% Y/Y) at the end of Q4/FY2026 in the Q3 FY2026 8-K. NGS ARR exited Q3 FY2026 at $8.1B (+60% Y/Y, of which $1.6B came from CyberArk and Chronosphere), and NGS ARR is the KPI PANW's platformization strategy is explicitly built to drive. With CyberArk fully consolidated and platform deals landing, we call NGS ARR finishing FY2026 at or above the top of the guided band. NOTE this metric is partly inorganic in FY2026 -- roughly $1.6B of the Q3 balance is acquired -- so the reported growth rate overstates the organic run-rate."
  - id: "PANW-FY2026-initiation-platformization"
    ticker: "PANW"
    timestamp: "2026-07-13T17:15:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "platformization_ngs_arr_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/PANW/2026-07-13_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the filing itself makes: we expect PANW's platformization strategy -- consolidating Network Security, Cortex security operations/cloud, and now CyberArk identity onto integrated platforms -- to keep NGS ARR compounding as the primary growth engine through FY2026, structurally outgrowing total revenue (NGS ARR grew ~33% in FY2025, from $4.2B to $5.6B, versus 14.9% total revenue growth). We explicitly flag the filing-disclosed risk that cuts against this: the Q3 FY2026 8-K's own forward-looking-statements section names 'failure of our platformization product offerings' and the risk that expected CyberArk integration benefits and synergies 'may not be fully achieved in a timely manner, or at all' -- and a large part of the headline 60% NGS ARR growth is currently inorganic (CyberArk/Chronosphere), so the organic platformization thesis is what we are actually calling."
    rationale: "FY2025 10-K: platformization is described as the core strategy (combining products/services into tightly integrated Network Security, Cortex, and Cloud platforms); NGS ARR grew to $5.6B at July 31, 2025 from $4.2B a year earlier (~+33%) while total revenue grew 14.9% to $9.2B -- NGS ARR is the disproportionate growth driver the company says it optimizes for. Q3 FY2026 8-K: NGS ARR reached $8.1B (+60% Y/Y, incl. $1.6B from CyberArk/Chronosphere) and RPO $18.4B (+36%). Our call that platformization keeps NGS ARR the lead growth engine organically through FY2026 is an extrapolation, not a forecast the filings make; the 8-K itself lists platformization failure and unrealized CyberArk synergies among its enumerated risks."
  - id: "PANW-FY2026-initiation-gaap_nongaap_gap"
    ticker: "PANW"
    timestamp: "2026-07-13T17:15:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "gaap_to_nongaap_profitability_gap_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/PANW/2026-07-13_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the filing itself makes: we expect PANW to stay solidly non-GAAP profitable while its GAAP operating result stays pressured (potentially a GAAP operating loss in some quarters) through FY2026, and we flag the size of the GAAP-to-non-GAAP gap as the key earnings-quality watch item. In Q3 FY2026 PANW reported a GAAP operating LOSS of $183M against non-GAAP operating income of $814M -- a >$990M wedge driven mostly by $517M of share-based-compensation-related charges plus $198M of CyberArk acquisition-related costs and $280M of acquired-intangible amortization. The filing-disclosed risk that cuts against a benign read: those SBC and acquisition/contingent-consideration and convertible-note fair-value items are recurring and explicitly excluded from the non-GAAP guidance (op margin 28.9-29.2%, EPS $3.77-3.79 for FY2026), and SBC-driven share issuance is a real dilution/ownership cost the non-GAAP numbers do not capture."
    rationale: "Q3 FY2026 8-K reconciliation: GAAP operating loss $(183)M vs non-GAAP operating income $814M; bridge items are SBC-related charges $517M, acquisition-related costs $198M, amortization of acquired intangibles $280M, litigation $2M. GAAP net loss was $(177)M / $(0.22) diluted vs non-GAAP net income $684M / $0.85 diluted. FY2025 10-K: full-year FY2025 was GAAP-profitable (operating income $1,242.9M, 13.5% margin; net income $1,133.9M, $1.60 diluted) with $1,300.1M of total SBC -- the GAAP operating loss is a post-CyberArk-close phenomenon, not the FY2025 baseline. PANW's FY2026 guidance is non-GAAP only (it explicitly does not reconcile to GAAP because SBC and fair-value items 'cannot be reasonably predicted'). Our call that the gap persists and is the watch item is our framing, not a forecast the filings assert."
---

# PANW -- Initiation: Palo Alto Networks, Inc.

*Initiation note: sets our baseline thesis on Palo Alto Networks from the FY2025 10-K
(fiscal year ended July 31, 2025) and the Q3 FY2026 earnings 8-K (filed 2026-06-02).
PANW is the platform-security leg of the software complex, and its July fiscal-year-end
staggers it off the crowded calendar-quarter reporting cluster. Unlike a preview note,
this is not graded against a prior quarter's guidance -- it establishes the calls above
as the tracked baseline for future flashes/reviews. PANW guides and reports its outlook
on a non-GAAP basis; every guidance figure below is stated exactly as management gave it.*

## Business

Palo Alto Networks is a global cybersecurity provider whose strategy centers on
**platformization** -- consolidating customers' disparate point products onto a small
number of tightly integrated platforms. It organizes its portfolio into three platform
areas: **Network Security** (ML-Powered Next-Generation Firewalls, Prisma SASE/Access,
Cloud-Delivered Security Services, Strata Cloud Manager, Prisma AIRS for AI security),
**Cortex security operations and cloud security** (Cortex XSIAM/XDR/XSOAR/Xpanse and
Cortex Cloud CNAPP), and **Unit 42** threat intelligence and advisory services. As of
the FY2025 10-K it served end-customers in over 180 countries, including almost all of
the Fortune 100; the Q3 FY2026 release cites 70,000+ customers.

FY2025 (year ended July 31, 2025) total revenue was **$9,221.5M, up 14.9%** year over
year, split Product **$1,801.9M** (19.5% of revenue, +12.4%) and Subscription & support
**$7,419.6M** (80.5%, +15.5%). GAAP gross margin was **73.4%** (down from 74.3% in
FY2024), GAAP operating income **$1,242.9M** (13.5% margin, up from 8.5%), GAAP net
income **$1,133.9M**, and GAAP diluted EPS **$1.60**. Total share-based compensation was
**$1,300.1M**. The two press-release KPIs the company steers by both grew faster than
revenue: **NGS ARR** reached **$5.6B** at July 31, 2025 (from $4.2B a year earlier,
roughly +33%) and **remaining performance obligation (RPO)** reached **$15.8B** as of
July 31, 2025 (of which ~$7.0B is expected to be recognized within 12 months).

The story then inflects on M&A. During FY2025 PANW acquired certain IBM QRadar assets
(Aug 2024) and Protect AI (July 2025), and entered a definitive agreement to acquire
**CyberArk** (identity security), which the 10-K expected to close in the second half of
FY2026. By the Q3 FY2026 print CyberArk had closed and consolidated: Q3 FY2026 total
revenue grew **31% to $3.0B** (including **$388M** from CyberArk and Chronosphere), NGS
ARR grew **60% to $8.1B** (including **$1.6B** from CyberArk/Chronosphere), and RPO grew
**36% to $18.4B** (including $1.8B). Critically, the acquisition charges flipped GAAP
operating income negative even as non-GAAP stayed strongly positive (see below).

## What we're tracking

- **Q4 FY2026 revenue and NGS ARR vs. PANW's own guide** ($3.345-3.355B revenue at +32%;
  NGS ARR $8.90-8.95B at +59-60%, per the Q3 FY2026 8-K) -- our baseline calls above lean
  to a beat on both, on a full quarter of CyberArk consolidation and platform-deal
  momentum. Note the narrowness of the revenue band ($10M wide) and that much of the NGS
  ARR growth rate is currently inorganic.
- **The GAAP-to-non-GAAP profitability gap.** Q3 FY2026 was a **GAAP operating loss of
  $183M** against **non-GAAP operating income of $814M** -- a wedge driven by $517M SBC,
  $198M CyberArk acquisition costs, and $280M acquired-intangible amortization. FY2026
  guidance is non-GAAP only (operating margin **28.9-29.2%**, diluted non-GAAP EPS
  **$3.77-3.79**), and management explicitly declines to reconcile it to GAAP. The size
  and persistence of this gap -- especially the recurring SBC and the dilution it implies
  -- is our earnings-quality watch item.
- **Full-year FY2026 guide.** Total revenue **$11.415-11.425B** (+24%), NGS ARR
  **$8.90-8.95B**, RPO **$20.9-21.0B** (+32-33%), non-GAAP operating margin
  **28.9-29.2%**, diluted non-GAAP EPS **$3.77-3.79** (763-766M shares), and adjusted
  free-cash-flow margin **37.5%** -- with management reiterating a target of 40% adjusted
  FCF margin in FY2028.
- **CyberArk integration.** The 8-K lists platformization failure and unrealized CyberArk
  synergies among its named risks; the share count jump (diluted shares 707M in Q3 FY2025
  to 801M GAAP-weighted in Q3 FY2026, reflecting stock issued for CyberArk) is the
  dilution to watch against the non-GAAP EPS line.

## Model

`models/PANW/PANW_model_2026-07-13.xlsx` -- built via `scripts/build_model.py PANW`
against companyfacts XBRL (trailing quarters of headline GAAP financials + margin/growth
formulas + our-estimates tab). Three model notes:

1. **The KPIs are press-release-sourced, not in companyfacts.** NGS ARR, billings, and
   RPO (the metrics PANW guides and that our calls above are graded on) are **not** in
   companyfacts' non-dimensional facts -- consistent with the Session 2 structural
   finding -- so those figures are cited directly to the FY2025 10-K and the Q3 FY2026
   8-K, not carried in the model.
2. **The GAAP operating-income row can look negative/odd in recent quarters, and that is
   real, not a data error.** After the CyberArk close, GAAP operating income swung to a
   **loss ($183M in Q3 FY2026)** because GAAP absorbs the full SBC ($517M), acquisition
   costs ($198M), and intangible amortization ($280M) that PANW's non-GAAP measures
   exclude; on a non-GAAP basis the same quarter was **$814M** of operating income. The
   model carries GAAP (companyfacts) history; the non-GAAP profitability the company
   guides to is a separate, higher line.
3. **A pre-split EPS labeling artifact.** The build logged filing-to-filing
   disagreements on diluted EPS for several pre-December-2024 quarters (e.g. a Jan-2024
   quarter shown at $4.89 as originally filed vs. $2.44 as later restated); this reflects
   PANW's December 2024 two-for-one stock split, and the model retains
   as-originally-reported (earliest-filed) figures by design -- a split labeling artifact,
   not a data error. Remaining warnings were sub-$1M rounding differences between the
   original and comparative-period refilings, resolved to earliest-filed.

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
