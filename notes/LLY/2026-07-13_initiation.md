---
ticker: "LLY"
type: initiation
event_date: "2026-07-13"
published_at: "2026-07-13T16:45:00Z"
period: "FY2025"
fiscal_year_end: "December"
basis: "non_gaap"
source_filings:
  - description: "FY2025 10-K (fiscal year ended December 31, 2025) -- business narrative, product revenue, MD&A results of operations, IRA/pricing and competition risk"
    url: "https://www.sec.gov/Archives/edgar/data/59478/000005947826000013/lly-20251231.htm"
  - description: "companyfacts XBRL (headline financials/history)"
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0000059478.json"
  - description: "Q1 2026 earnings 8-K (EX-99), filed 2026-04-30 -- current-quarter actuals and updated full-year 2026 guidance (revenue, non-GAAP EPS, performance margin)"
    url: "https://www.sec.gov/Archives/edgar/data/59478/000005947826000043/q126lillysalesandearningsp.htm"
fact_check:
  status: passed
  run_at: "2026-07-13T17:20:00Z"
  notes: "15/15 claims verified against their cited EDGAR filings on first pass. All 13 numeric claims (raised FY2026 revenue $82-85B and non-GAAP EPS $35.50-37.00 guides, Q1 2026 revenue/Mounjaro/Zepbound/non-GAAP EPS, Foundayo FDA approval, FY2025 revenue/net income/EPS/Mounjaro/Zepbound, incretin 56%-of-revenue) matched their sources with verbatim evidence. Both qualitative thesis calls (incretin-franchise growth, oral-incretin/Foundayo catalyst) survived the adversarial refutation pass. Nothing cut or flagged."
calls:
  - id: "LLY-FY2026-initiation-revenue"
    ticker: "LLY"
    timestamp: "2026-07-13T16:45:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "revenue"
    unit: "USD_M"
    basis: "non_gaap"
    source_note: "notes/LLY/2026-07-13_initiation.md"
    higher_is_better: true
    confidence: 0.6
    call:
      kind: direction
      value: "beat"
      benchmark:
        kind: range
        low: 82000.0
        high: 85000.0
    rationale: "In the Q1 2026 8-K, Lilly RAISED full-year 2026 revenue guidance to $82.0B-$85.0B (from $80.0B-$83.0B), after Q1 2026 revenue grew 56% to $19.8B on 65% volume growth. The incretin franchise is the driver: Q1 2026 Mounjaro revenue was $8.66B (+125%) and Zepbound $4.16B (+80%), and FY2025 Mounjaro+Zepbound were already 56% of total revenue. With the June-2026 launch of Foundayo (orforglipron), the first oral GLP-1 pill, incremental to the base guide and ex-U.S. Mounjaro still early in its rollout, we call full-year revenue landing at or above the top of the raised band. Risk to the call: the guide bakes in continued lower realized prices (Q1 price was -13%) and July-2026 Medicare obesity-access discounts, so a sharper price step-down could offset volume."
  - id: "LLY-FY2026-initiation-eps_adj"
    ticker: "LLY"
    timestamp: "2026-07-13T16:45:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "eps_adj"
    unit: "eps_usd"
    basis: "non_gaap"
    source_note: "notes/LLY/2026-07-13_initiation.md"
    higher_is_better: true
    confidence: 0.55
    call:
      kind: direction
      value: "beat"
      benchmark:
        kind: range
        low: 35.50
        high: 37.00
    rationale: "Lilly RAISED full-year 2026 non-GAAP EPS guidance to $35.50-$37.00 (from $33.50-$35.00) in the Q1 2026 8-K, alongside a performance-margin guide raised to 47.0%-48.5%. Q1 2026 non-GAAP EPS was already $8.55 (+156%), with non-GAAP gross margin at 82.6% of revenue. Operating leverage on the incretin volume ramp plus the ~895M assumed share count support the top of the band. NOTE the guidance explicitly EXCLUDES acquired IPR&D incurred after March 31, 2026 -- Lilly signed four acquisitions (Orna, Centessa, Kelonia, Ajax) around the print, so future IPR&D charges do not count against this non-GAAP guide but do hit reported EPS. Risk to the call: reported (GAAP) EPS could diverge materially from the non-GAAP figure this call is graded on if late-year IPR&D or special charges are large."
  - id: "LLY-FY2026-initiation-incretin_thesis"
    ticker: "LLY"
    timestamp: "2026-07-13T16:45:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "incretin_franchise_growth_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/LLY/2026-07-13_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the filing itself makes: we expect Lilly's incretin franchise (Mounjaro + Zepbound, tirzepatide) to remain the dominant growth engine through FY2026, with volume growth continuing to outrun the realized-price decline. We explicitly flag the filing-disclosed risks that cut against this: the FY2025 10-K states worldwide realized prices fell (U.S. price -10% in 2025) and that continued pricing pressure, the company's preliminary U.S. government drug-pricing agreements, July-2026 Medicare obesity discounts, and intense competition could reduce revenue -- so this is a volume-over-price thesis, not a filing forecast."
    rationale: "FY2025 10-K: Mounjaro revenue was $22,965M (+99%) and Zepbound $13,542M (+175%); the two together were 56% of total revenue, and Lilly states it expects cardiometabolic products to remain a significant and growing portion of the business. Q1 2026 8-K: Mounjaro $8,662M (+125%), Zepbound $4,160M (+80%), with consolidated volume +65% versus price -13%. The 10-K itself does NOT forecast FY2026 franchise growth and separately warns of lower realized prices, government-set prices under the IRA (Trulicity and Verzenio selected for 2028), manufacturing-capacity dependence, and intense competition -- our volume-led growth call is an extrapolation, and we name those offsetting risks rather than ignore them."
  - id: "LLY-FY2026-initiation-oral_incretin_pipeline"
    ticker: "LLY"
    timestamp: "2026-07-13T16:45:00Z"
    call_type: initiation
    period: "FY2026"
    metric: "oral_incretin_pipeline_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/LLY/2026-07-13_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the filing itself makes: we treat orforglipron (branded Foundayo), Lilly's oral GLP-1 pill, as the key FY2026 pipeline catalyst -- an oral incretin sidesteps the injectable manufacturing-capacity constraint and can materially widen the treatable population, and we hold it as upside to the incretin thesis. We explicitly flag the filing-disclosed uncertainty against it: pharmaceutical R&D carries significant timing and approval risk, uptake pace in new channels is uncertain, and Lilly ties near-term performance to the timing of orforglipron approvals and Medicare access -- so this is our catalyst call, not a filing projection."
    rationale: "Q1 2026 8-K: the U.S. FDA approved Foundayo (orforglipron) for adults with obesity/overweight with weight-related conditions, with positive Phase 3 results in type 2 diabetes; Lilly calls it 'the only approved GLP-1 pill that can be taken any time of day, without food and water restrictions.' FY2025 10-K: orforglipron was submitted in the U.S./EU/Japan and granted a Commissioner's National Priority Voucher, and Lilly states near-term performance will be impacted by the timing of orforglipron regulatory approvals and Medicare access, and that it has undertaken significant manufacturing-expansion initiatives to meet demand. The filings disclose the approval and the risk; the call that oral dosing is the FY2026 population-expanding catalyst is our forward view, not a forecast the filings make."
---

# LLY -- Initiation: Eli Lilly and Company

*Initiation note: sets our baseline thesis on Eli Lilly from the FY2025 10-K (fiscal
year ended December 31, 2025) and the Q1 2026 earnings 8-K (filed 2026-04-30). Lilly is
the desk's deliberate pharma decorrelator -- a name whose thesis rides incretin
(GLP-1/GIP) demand and pipeline, not AI capex, so its calls are meant to keep the
scorecard from being one correlated infrastructure bet. Unlike a preview note, this is
not graded against a prior quarter's guidance -- it establishes the calls above as the
tracked baseline for future flashes/reviews.*

## Business

Eli Lilly is a global pharmaceutical company whose results are now dominated by its
**incretin (tirzepatide) franchise** -- **Mounjaro** (type 2 diabetes) and **Zepbound**
(obesity), the same molecule marketed under two brands. FY2025 revenue was **$65,179M,
up 45%** year over year (U.S. $43,481M, outside U.S. $21,698M), driven by a 50% volume
increase partially offset by a 6% price decline. GAAP net income was **$20,640M (+95%)**
and reported diluted EPS **$22.95 (+96%)**. Lilly guides and reports on both a reported
(GAAP) and non-GAAP basis; the coverage basis here is **non-GAAP**, the basis Lilly uses
for its EPS and margin guidance.

Product concentration is the defining feature: **Mounjaro** FY2025 revenue was
**$22,965M (+99%)**, **Zepbound $13,542M (+175%)**, and **Verzenio** (oncology) $5,723M
(+8%). Mounjaro and Zepbound together were **56% of total revenue** in 2025, and Lilly
states it expects cardiometabolic-health products to remain a significant and growing
share of the business. The quarterly dividend was raised to $1.73/share effective Q1
2026 (an indicated annual rate of $6.92 for 2026).

Two forward items frame the thesis. First, **orforglipron (branded Foundayo)** -- an
oral GLP-1 pill approved by the U.S. FDA (announced with the Q1 2026 print) for obesity,
with positive Phase 3 diabetes data -- opens the incretin market to oral dosing and, by
Lilly's framing, "meaningfully expand[s] the number of people who can benefit from
GLP-1s." Second, **pricing and access**: FY2025 realized prices fell (U.S. -10%), Lilly
reached preliminary U.S. government drug-pricing agreements (Medicare obesity-medicine
discounts by July 1, 2026), and the IRA has selected Trulicity and Verzenio for
government-set prices effective 2028 -- a structural offset to volume the filings flag
directly.

## What we're tracking

- **Full-year 2026 revenue and non-GAAP EPS vs. Lilly's own raised guide** (revenue
  $82.0B-$85.0B, non-GAAP EPS $35.50-$37.00, performance margin 47.0%-48.5%, tax rate
  18%-19%, per the Q1 2026 8-K) -- our baseline calls above lean to a beat on both, on
  the view that the incretin volume ramp and the Foundayo launch are incremental to a
  guide Lilly already raised once at Q1.
- **Incretin volume vs. price.** Q1 2026 was +65% volume, -13% price; whether volume
  keeps outrunning the realized-price decline as Medicare obesity discounts (July 1,
  2026) and NRDL pricing in China take hold is the core swing factor.
- **Orforglipron / Foundayo uptake.** The oral GLP-1 launch is the FY2026 catalyst we're
  watching -- pace of uptake, Medicare access timing, and manufacturing capacity for a
  pill versus injectables.
- **The non-GAAP vs. reported gap.** FY2026 non-GAAP EPS guidance excludes acquired IPR&D
  after March 31, 2026; Lilly signed four acquisitions (Orna, Centessa, Kelonia, Ajax)
  around the print, so reported (GAAP) EPS can diverge materially from the non-GAAP figure
  our EPS call is graded on -- a basis watch-item for future flashes.
- **Pricing/policy and competition risk.** IRA government-set prices (Trulicity, Verzenio
  from 2028), the preliminary U.S. government pricing agreements, biosimilar/generic
  competition, and intense incretin competition are the disclosed downside our thesis is
  measured against.

## Model

`models/LLY/LLY_model_2026-07-13.xlsx` -- built via `scripts/build_model.py LLY` against
companyfacts XBRL (trailing headline financials + our-estimates tab). Two model notes:
(1) **product-level revenue** (Mounjaro / Zepbound / Verzenio) is **not** in companyfacts
(headline-only, per the Session 2 structural finding) -- the product figures above are
cited directly to the FY2025 10-K and the Q1 2026 8-K press release, not the model; and
(2) **Lilly does not tag standalone GrossProfit or OperatingIncome** in companyfacts, so
the model carries consolidated revenue / net income / diluted EPS history from XBRL, and
gross/performance margin is press-release-sourced (Q1 2026 non-GAAP gross margin 82.6%;
FY2026 performance-margin guide 47.0%-48.5%).

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
