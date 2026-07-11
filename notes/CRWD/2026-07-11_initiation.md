---
ticker: "CRWD"
type: initiation
event_date: "2026-07-11"
published_at: "2026-07-11T20:00:00Z"
period: "FY2026"
fiscal_year_end: "January"
basis: "non_gaap"
source_filings:
  - description: "FY2026 10-K (filed 2026-03-05) -- business narrative, key metrics, MD&A"
    url: "https://www.sec.gov/Archives/edgar/data/1535527/000153552726000010/crwd-20260131.htm"
  - description: "companyfacts XBRL (headline financials/history)"
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0001535527.json"
  - description: "Q1 FY2027 earnings 8-K (EX-99.1), filed 2026-06-03 -- current-quarter actuals and Q2/full-year FY2027 outlook"
    url: "https://www.sec.gov/Archives/edgar/data/1535527/000153552726000022/crwd-20260603xex991.htm"
  - description: "prior CRWD notes (backtest series covering the same Q1 FY2027 print in more granular detail)"
    url: "notes/CRWD/2026-06-05_review.md"
fact_check:
  status: passed
  run_at: "2026-07-11T21:00:00Z"
  notes: "9/9 claims verified across three rounds. 7 numeric claims (Q2/FY2027 guidance + FY2026 10-K facts) passed on the first pass. Both qualitative theses initially failed: the retention thesis originally implied the July 19 Incident's commitment-package headwind was 'rolling off' when the 10-K discloses it as open-ended with no expiration -- reframed as a speculative bet made explicitly against that disclosed, continuing risk, and passed. The GAAP-profitability thesis originally claimed the loss was 'continuing to narrow toward breakeven' based only on a Q1-over-Q1 comparison; checking the 10-K's annual figures revealed the full-year loss actually WIDENED every year through FY2026 ($19.1M to $116.4M to $293.3M) -- reframed as a genuine inflection call (reversing that widening) rather than a continuation of a trend that didn't exist, and re-sourced so the Q1 FY2027 figure cites the 8-K (the 10-K predates FY2027 and cannot contain that data) while the annual trend cites the 10-K. Both passed on final re-verification."
calls:
  - id: "CRWD-FY2027Q2-initiation-revenue"
    ticker: "CRWD"
    timestamp: "2026-07-11T20:00:00Z"
    call_type: initiation
    period: "FY2027Q2"
    metric: "revenue"
    unit: "USD_M"
    basis: "non_gaap"
    source_note: "notes/CRWD/2026-07-11_initiation.md"
    higher_is_better: true
    confidence: 0.6
    call:
      kind: direction
      value: "beat"
      benchmark:
        kind: range
        low: 1436.0
        high: 1442.0
    rationale: "CrowdStrike guided Q2 FY2027 total revenue to $1,436.0-1,442.0M in the Q1 FY2027 8-K, alongside management explicitly 'increasing' its full-year FY2027 guidance the same quarter. FY2026 net new ARR of $1.0B (vs. $806.7M in FY2025) and a dollar-based net retention rate that improved to 115% (from 112%) support the view that the July 19 Incident's drag on new bookings is fading, so we lean toward a top-of-band or better print."
  - id: "CRWD-FY2027Q2-initiation-non_gaap_eps"
    ticker: "CRWD"
    timestamp: "2026-07-11T20:00:00Z"
    call_type: initiation
    period: "FY2027Q2"
    metric: "eps_adj"
    unit: "eps_usd"
    basis: "non_gaap"
    source_note: "notes/CRWD/2026-07-11_initiation.md"
    higher_is_better: true
    confidence: 0.55
    call:
      kind: point
      value: 1.165
      tolerance: 0.05
    rationale: "CrowdStrike guided Q2 FY2027 non-GAAP EPS to $1.16-1.17. Non-GAAP income from operations already grew to $325.7M in Q1 FY2027 (from $201.1M a year earlier) while GAAP loss from operations narrowed sharply ($30.6M loss vs. $118.7M loss) -- we call the midpoint of the guided EPS range as achievable given that operating-leverage trend, without assuming further acceleration beyond what's already guided."
  - id: "CRWD-FY2027-initiation-retention_thesis"
    ticker: "CRWD"
    timestamp: "2026-07-11T20:00:00Z"
    call_type: initiation
    period: "FY2027"
    metric: "net_retention_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/CRWD/2026-07-11_initiation.md"
    call:
      kind: qualitative
      value: "Our own speculative forward view, made explicitly against the filing's own disclosed headwind rather than with its support: CrowdStrike's dollar-based net retention rate continues to improve (or at minimum holds at 115%) through FY2027. The 10-K does NOT describe the July 19 Incident's customer-commitment-package effects as rolling off -- it describes them as an open-ended, continuing risk with no stated expiration -- so this call bets the FY2026 retention improvement keeps outweighing that disclosed, ongoing headwind, not that the headwind itself is fading."
    rationale: "FY2026 10-K: dollar-based net retention improved to 115% (from 112% a year earlier), a fact the filing supports. But the filing's own language on customer commitment packages is open-ended and continuing -- 'have resulted, and are expected to continue to result, in increased contraction... and decreased upsell dollar values' -- with no roll-off or expiration language anywhere in the document. We are not claiming the filing supports fading headwinds; we are betting that FY2026's demonstrated retention improvement continues to outrun a headwind the 10-K itself frames as ongoing, which is a genuinely two-sided, speculative call."
  - id: "CRWD-FY2027-initiation-gaap_profitability_thesis"
    ticker: "CRWD"
    timestamp: "2026-07-11T20:00:00Z"
    call_type: initiation
    period: "FY2027"
    metric: "gaap_operating_income_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/CRWD/2026-07-11_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, corrected after checking the FY2026 10-K's annual trend rather than just the Q1-over-Q1 comparison: FY2027 marks an inflection where CrowdStrike's FULL-YEAR GAAP operating loss narrows for the first time since FY2024, reversing three straight years of widening (FY2024 loss $19.1M -> FY2025 loss $116.4M -> FY2026 loss $293.3M). We initially framed this as a simple continuation of 'narrowing' based only on the Q1 FY2027-vs-Q1 FY2026 comparison, which mischaracterized the trend -- full-year losses actually widened every year through FY2026. The Q1 FY2027 improvement ($30.6M loss vs. $118.7M a year earlier) is real, but it is better understood as the sharpest data point yet in a within-FY2026 sequential narrowing (loss of $118.7M in Q1 FY2026 down to $6.9M in Q4 FY2026) than as an extension of an annual trend that didn't previously exist."
    rationale: "FY2026 10-K income statement: full-year loss from operations was $293.3M (FY2026), $116.4M (FY2025), and $19.1M (FY2024) -- widening each year, not narrowing, largely because July 19 Incident-related costs appear to have hit hardest in FY2026 (the incident occurred July 19, 2024, roughly nine months before FY2026 began). Within FY2026 itself, the quarterly loss narrowed sequentially from $118.7M (Q1) to $6.9M (Q4), and Q1 FY2027's $30.6M loss (vs. $118.7M a year earlier) extends that sequential improvement. Non-GAAP income from operations grew to $325.7M from $201.1M over the same year-over-year window. The FY2026 10-K separately states legal/professional costs tied to the July 19 Incident are expected to continue, an open-ended cost the filing does not quantify or forecast rolling off -- our call is that revenue growth's operating leverage now outpaces that continuing cost drag on a full-year basis, which would be a new pattern, not a continuation of one already established in the filing."
---

# CRWD -- Initiation: CrowdStrike Holdings, Inc.

*Initiation note: sets our baseline thesis on CRWD from the FY2026 10-K (filed
2026-03-05, fiscal year ended January 31, 2026) and the Q1 FY2027 earnings 8-K (filed
2026-06-03). This is not graded against a prior quarter's guidance -- it establishes
the calls above as the tracked baseline for future flashes/reviews. Note: a separate
backtest note series (`notes/CRWD/2026-06-02_preview.md` through `2026-06-05_review.md`,
Session 3) already covers this same Q1 FY2027 print in more granular, quarter-specific
detail; this initiation note is deliberately broader and forward-looking (FY2027 full
year, not just Q1) and its call ids do not overlap with that series.*

## Business

CrowdStrike sells cloud-delivered endpoint/cloud/identity security (the Falcon
platform) via per-endpoint, per-module subscriptions (95% of FY2026 revenue) plus
incident-response and professional services (5%). FY2026 (ended January 31, 2026)
total revenue was $4.812B, up 22% year over year; subscription gross margin was flat
at 78%. Annual Recurring Revenue (ARR) grew 24% to $5.253B, with $1.0B of net new ARR
added during FY2026 (versus $806.7M in FY2025) -- an acceleration in new-business
momentum. Dollar-based net retention improved to 115% (from 112%). GAAP operating loss
narrowed sharply into Q1 FY2027: $30.6M (versus $118.7M a year earlier), while
non-GAAP income from operations grew to $325.7M (from $201.1M).

The **July 19 Incident** -- the July 19, 2024 Falcon sensor content-update defect that
caused widespread Windows system crashes -- remains a live, disclosed overhang. The
10-K states the company continues to incur "significant legal and professional
services and other general and administrative expenses" tied to the incident and its
related lawsuits/claims, and that customer commitment packages introduced afterward
(discounting, extra modules, flexible terms, subscription extensions) have caused, and
are expected to continue causing, "increased contraction" and "decreased upsell dollar
values" as those packages' terms play out. That the net retention rate nonetheless
improved to 115% in FY2026 is the central tension in our thesis: bookings and renewal
economics are recovering faster than the disclosed headwind would suggest, but the
filing itself does not forecast whether that continues.

## What we're tracking

- **Q2 FY2027 revenue and non-GAAP EPS vs. CrowdStrike's own guide** ($1,436.0-1,442.0M
  revenue; $1.16-1.17 non-GAAP EPS, from the Q1 FY2027 8-K, issued alongside a raise to
  full-year FY2027 guidance) -- our baseline calls lean toward a revenue beat and an
  on-guide EPS print.
  Full-year FY2027 guidance for reference: ARR $6,531.7-6,555.5M, revenue
  $5,914.7-5,958.7M, non-GAAP EPS $4.88-4.96.
- **Net retention and net-new-ARR trend** as the July 19 Incident's customer-commitment
  packages continue to work through multi-year contracts -- whether FY2026's
  improvement (115% retention, $1.0B net new ARR) continues or the disclosed
  contraction/reduced-upsell risk catches up with it.
- **Full-year GAAP operating loss trend**: it widened every year from FY2024 ($19.1M)
  through FY2026 ($293.3M), largely on July 19 Incident-related costs that appear to
  have hit hardest in FY2026 -- whether the sharp Q1 FY2027 year-over-year improvement
  ($30.6M loss vs. $118.7M) marks a genuine full-year inflection or is just the latest
  point on an intra-FY2026 sequential recovery ($118.7M to $6.9M loss, Q1 to Q4) that
  doesn't yet tell us about FY2027 as a whole.

## Model

`models/CRWD/CRWD_model_2026-07-11.xlsx` -- built via `scripts/build_model.py CRWD`
against companyfacts XBRL. **Known data quirk:** the model logs warnings that
GrossProfit, OperatingIncomeLoss, EarningsPerShareDiluted, and NetIncomeLoss for the
quarter ended 2025-04-30 disagree slightly between as-filed values across two
different later filings (e.g. diluted EPS -$0.44 vs. -$0.42) -- likely a small
restatement or reclassification between the original 10-Q and a later filing that
re-presents the comparative period. Per the anchoring design, the model keeps the
earliest-filed value. ARR, net new ARR, and dollar-based net retention are not in
companyfacts (headline-only, per the Session 2 structural finding); those figures
above are cited directly to the 10-K and 8-K.

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
