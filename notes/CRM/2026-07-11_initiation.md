---
ticker: "CRM"
type: initiation
event_date: "2026-07-11"
published_at: "2026-07-11T19:00:00Z"
period: "FY2026"
fiscal_year_end: "January"
basis: "non_gaap"
source_filings:
  - description: "FY2026 10-K (filed 2026-03-02) -- business narrative, MD&A"
    url: "https://www.sec.gov/Archives/edgar/data/1108524/000110852426000060/crm-20260131.htm"
  - description: "companyfacts XBRL (headline financials/history)"
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0001108524.json"
  - description: "Q1 FY2027 earnings 8-K (EX-99.1), filed 2026-05-27 -- current-quarter actuals and Q2/full-year FY2027 outlook"
    url: "https://www.sec.gov/Archives/edgar/data/1108524/000110852426000125/crm-q1fy27xexhibit991.htm"
fact_check:
  status: failed
  run_at: "2026-07-11T21:15:00Z"
  notes: "6/7 claims verified clean; 1 published flagged unverified. 6 numeric claims (Q2 FY2027 revenue guide, FY2027 full-year GAAP/non-GAAP margin guide, FY2026 revenue/op-income/EPS, RPO, cash/buybacks/dividends, Informatica acquisition, attrition rate) all passed, though two initially came back as false mismatches from a wrong-document/fetch-failure infra quirk (see Session 3's handoff) and were confirmed genuine on isolated re-check. The agentforce/cRPO thesis went through 3 correction rounds: round 1 overreached by implying the 10-K itself causally attributes cRPO's outpacing of revenue to Agentforce; round 2 mistakenly REMOVED a real, verified $2.2B Informatica-current-RPO figure after a false-negative fact-check pass claimed it didn't exist -- restored after direct re-reading of the cached filing text confirmed the figure is present verbatim; round 3 (final) nets out both the FX and Informatica-RPO components and surfaces the 10-K's own caution that RPO 'is not necessarily indicative of future revenue growth' as a genuine headwind, and passed. The attrition-rate thesis was refuted twice on the same structural grounds (a forward-looking bet a backward-looking filing can neither confirm nor deny, made explicitly against the filing's own risk-factor hedging) -- rather than loop indefinitely on an inherently unconfirmable forward call, it is published flagged `verification: unverified` per the note pipeline's handling of directionally-reasonable claims the gate cannot settle; see its prose disclosure in 'What we're tracking'."
calls:
  - id: "CRM-FY2027Q2-initiation-revenue"
    ticker: "CRM"
    timestamp: "2026-07-11T19:00:00Z"
    call_type: initiation
    period: "FY2027Q2"
    metric: "revenue"
    unit: "USD_M"
    basis: "non_gaap"
    source_note: "notes/CRM/2026-07-11_initiation.md"
    higher_is_better: true
    confidence: 0.6
    call:
      kind: direction
      value: "beat"
      benchmark:
        kind: range
        low: 11270.0
        high: 11350.0
      # note: guided range already reflects the FY27 midpoint raise; historically Salesforce's
      # actuals have landed at or slightly above the top of the initial Q-guide.
    rationale: "Salesforce guided Q2 FY2027 revenue to $11.27-11.35B (+10-11% YoY, including slightly above 4pts of Informatica contribution) in the Q1 FY2027 8-K, and simultaneously raised the FY2027 full-year revenue midpoint. Given management raised guidance the same quarter it set this range (rather than just reiterating), and cRPO grew 16% in FY2026 (faster than revenue), we lean toward a print at or above the top of the guided band."
  - id: "CRM-FY2027-initiation-gaap_operating_margin"
    ticker: "CRM"
    timestamp: "2026-07-11T19:00:00Z"
    call_type: initiation
    period: "FY2027"
    metric: "gaap_operating_margin"
    unit: "pct"
    basis: "non_gaap"
    source_note: "notes/CRM/2026-07-11_initiation.md"
    higher_is_better: true
    confidence: 0.5
    call:
      kind: point
      value: 20.6
      tolerance: 0.3
    rationale: "Salesforce's full-year FY2027 GAAP operating margin guidance is 20.6% (raised/updated in the Q1 FY2027 8-K), continuing the FY2026 pattern where GAAP operating margin expanded to ~20% (from ~19%) on restructuring-driven cost discipline (workforce reduction, data-center exits, office-space reductions). We call the guided figure achievable given that trend, but flag that continued Informatica integration costs are the main swing factor against it."
  - id: "CRM-FY2027-initiation-agentforce_thesis"
    ticker: "CRM"
    timestamp: "2026-07-11T19:00:00Z"
    call_type: initiation
    period: "FY2027"
    metric: "agentforce_adoption_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/CRM/2026-07-11_initiation.md"
    call:
      kind: qualitative
      value: "Our own forward view, not a projection the FY2026 10-K itself makes and not a causal link the filing draws: we expect cRPO growth to keep outpacing total revenue growth into FY2027, with Agentforce/Data 360 momentum and a full year of Informatica as drivers -- net of the 3-point FX tailwind and the approximately $2.2 billion of current RPO directly attributable to the Informatica acquisition (both disclosed in the 10-K), which inflated FY2026's 16%-vs-10% cRPO/revenue gap and may not repeat at the same scale. We note explicitly that the 10-K itself cautions that RPO 'is not necessarily indicative of future revenue growth' and is 'impacted by acquisitions' -- i.e., the filing flags exactly the risk that some of FY2026's cRPO outperformance is acquisition-driven backlog rather than organic demand, which is a real headwind to this call, not just a rounding caveat."
    rationale: "FY2026 10-K: management's 'strong momentum' language names Agentforce, Slack and Data 360 'bolstered by the acquisition of Informatica,' but the filing does NOT itself causally attribute cRPO's 16%-vs-10% outpacing of revenue to those products -- that link is our own inference. The filing discloses that FX added 3 points to FY2026 cRPO growth, and separately (in a current-RPO footnote) that current RPO 'includes approximately $2.2 billion of remaining performance obligation related to Informatica' -- both facts we net out rather than treating the full gap as organic momentum. (An earlier draft of this call incorrectly stated the $2.2B figure 'does not appear in the filing' after a fact-check pass returned a false negative; direct re-reading of the cited 10-K confirms the figure is present verbatim, and it has been restored here.) The 10-K's own RPO-methodology language ('not necessarily indicative of future revenue growth,' 'impacted by acquisitions') is a genuine disclosed caveat against this call, which we surface plainly rather than only in our favor. The 10-K contains no FY2027 outlook language at all; this call is entirely our own forward extrapolation."
  - id: "CRM-FY2027-initiation-attrition_thesis"
    ticker: "CRM"
    timestamp: "2026-07-11T19:00:00Z"
    call_type: initiation
    period: "FY2027"
    metric: "attrition_rate_qualitative"
    unit: "n/a"
    basis: "non_gaap"
    source_note: "notes/CRM/2026-07-11_initiation.md"
    verification: "unverified"
    call:
      kind: qualitative
      value: "UNVERIFIED (see fact_check notes) -- our own speculative forward view, made explicitly against the filing's own risk-factor hedging, not with its support: Salesforce's attrition rate (approximately 8% as of January 31, 2026, excluding Slack self-service and current-year acquisitions) holds roughly flat or improves through FY2027, rather than deteriorating as AI/Agentforce pricing and packaging changes are rolled out to the existing customer base."
    rationale: "FY2026 10-K states attrition 'has helped keep our attrition rate consistent as compared to the prior year' via customer programs -- a backward-looking fact only. The filing's own Risk Factors separately and explicitly hedge the other way: attrition rates are 'difficult to predict,' may 'increase or fluctuate' from pricing/packaging changes, and Agentforce/Data 360 pricing-and-packaging strategies 'may not be widely accepted by new or existing customers' and 'may harm our business.' The publish-gate refuter twice found this unconfirmable, on the same grounds each time: the filing contains no forward FY2027 language either way, and its own risk factors lean cautionary rather than supportive. Since the underlying backward-looking facts are verified and the gate's objection is inherent to any forward speculative call made against a backward-looking document's hedging language (not a factual error in our drafting), we are publishing this flagged as unverified rather than cutting a genuinely two-sided, disclosed thesis -- per the publish-gate procedure for claims that are directionally reasonable but that the gate cannot confirm."
---

# CRM -- Initiation: Salesforce, Inc.

*Initiation note: sets our baseline thesis on CRM from the FY2026 10-K (filed
2026-03-02, fiscal year ended January 31, 2026) and the Q1 FY2027 earnings 8-K (filed
2026-05-27). Unlike a preview note, this is not graded against a prior quarter's
guidance -- it establishes the calls above as the tracked baseline for future
flashes/reviews.*

## Business

Salesforce operates as one reportable segment, deriving ~95% of revenue from
subscription and support (Cloud Services, term software licenses) and the remainder
from professional services. FY2026 (ended January 31, 2026) revenue was $41.5B, up 10%
year over year; GAAP income from operations was $8.3B (20% margin, up from 19%);
diluted EPS was $7.80 (up from $6.36). Operating cash flow was $15.0B (+15%), and cash/
marketable securities stood at $9.6B. Total remaining performance obligation was
$72.4B (+14%) and current RPO (the next-12-months forward-revenue indicator) was
$35.1B (+16%) -- growing faster than reported revenue, the standard "leading
indicator" framing for a subscription business.

Two capital-allocation and M&A items stand out: Salesforce repurchased ~50 million
shares for ~$12.7B in FY2026 (up from 30 million shares / $7.8B in FY2025) and paid
~$1.6B in dividends; and it closed the ~$9.6B acquisition of Informatica (AI-powered
enterprise data management) in November 2025, plus a smaller October 2025 acquisition
of Regrello, both explicitly framed as accelerating the "agentic roadmap." Informatica
contributed only ~$0.4B of FY2026 revenue (a partial year, closed with about 2.5
months left in the fiscal year) -- the Q1 FY2027 8-K guides roughly 4 points of FY2027
revenue growth to Informatica, its first full year in the numbers.

## What we're tracking

- **Q2 FY2027 revenue vs. Salesforce's own guide** ($11.27-11.35B, +10-11% YoY,
  including >4pts from Informatica) and the **FY2027 full-year guide** ($45.9-46.2B
  revenue, 20.6% GAAP / 34.3% non-GAAP operating margin) -- our baseline calls lean
  toward a Q2 beat and an on-guide full-year GAAP margin.
- **cRPO growth versus revenue growth**: FY2026's 16%-vs-10% gap is the number that
  matters most for whether Agentforce/Data Cloud momentum is real bookings growth
  ahead of recognized revenue, or noise from the Informatica deal timing.
- **Attrition**: ~8% as of January 31, 2026 (ex-Slack self-service, ex-current-year
  acquisitions) -- the 10-K itself flags pricing/packaging risk for newer AI products
  as a genuine, unresolved risk to this holding steady. Our forward call that it holds
  or improves (`CRM-FY2027-initiation-attrition_thesis`) is marked **unverified**: the
  publish gate could not confirm it because the 10-K contains no FY2027 outlook either
  way and its own risk-factor language leans cautionary -- we're publishing the call
  flagged rather than cutting a genuinely two-sided thesis, per the note pipeline's
  handling of directionally-reasonable claims a backward-looking filing can't settle.
- **Margin trajectory net of Informatica integration costs** -- FY2026's margin
  expansion came from restructuring (workforce, data-center, office-space reductions);
  whether that continues once Informatica's own cost structure is folded in for a full
  year is an open question the 10-K does not resolve.

## Model

`models/CRM/CRM_model_2026-07-11.xlsx` -- built via `scripts/build_model.py CRM`
against companyfacts XBRL (trailing 8 quarters, headline financials + our-estimates
tab). cRPO, RPO, and Agentforce/Data-Cloud-specific detail are not in companyfacts
(headline-only, per the Session 2 structural finding); those figures above are cited
directly to the 10-K and 8-K.

---

*Educational research generated from public SEC EDGAR filings. Not investment advice.*
