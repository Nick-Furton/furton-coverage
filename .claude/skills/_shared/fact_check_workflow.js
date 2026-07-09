// Shared adversarial fact-check PUBLISH GATE for Furton Coverage.
//
// Used by /preview, /flash, and /review (see their SKILL.md files) as the last step
// before a drafted note may be saved final. Every numeric claim in the note's
// `calls:`/`guidance:` frontmatter gets an independent agent that re-fetches the CITED
// EDGAR document and checks the number against the filing itself (not against what the
// drafting session believes it read). Every qualitative call gets an agent whose job is
// to try to REFUTE it from the same cited document. Nothing here trusts the drafting
// session's own reading twice -- that would just be Claude grading its own homework.
//
// Notes are public; one hallucinated number kills the desk's credibility (PLAN §5/§7),
// so a claim that fails or can't be verified is cut or flagged by the calling skill --
// never silently published. This script only produces verdicts; it does not edit the
// note (the calling session does that, using these results).
//
// args shape (passed by the calling skill):
//   {
//     ticker: "CRWD",
//     note_type: "preview" | "flash" | "review",
//     claims: [
//       {
//         id: "CRWD-FY2027Q1-preview-revenue",
//         kind: "numeric" | "qualitative",
//         metric: "revenue",
//         unit: "USD_M",
//         claim_summary: "we call BEAT vs guided $1,360.0-1,364.0M" | the qualitative text,
//         source_url: "https://www.sec.gov/Archives/edgar/data/.../ex991.htm",
//         context: "one sentence of surrounding rationale, for the qualitative refuter"
//       }, ...
//     ]
//   }

export const meta = {
  name: 'fact_check_note',
  description: 'Publish-gate: adversarially re-verify every numeric claim against its cited EDGAR filing and try to refute every qualitative call',
  phases: [
    { title: 'Verify numeric claims' },
    { title: 'Refute qualitative claims' },
  ],
}

const NUMERIC_VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    matches: {
      type: 'boolean',
      description: 'true only if the cited filing itself contains a figure that supports the claimed value/band within reasonable rounding tolerance',
    },
    filing_value: {
      type: ['string', 'null'],
      description: 'the actual figure(s) found in the filing for this metric, quoted as text (e.g. "$1,386 million"), or null if the metric could not be located at all',
    },
    evidence_quote: {
      type: 'string',
      description: 'a short VERBATIM quote from the fetched filing that the verdict is based on; empty string only if nothing relevant was found',
    },
    discrepancy: {
      type: 'string',
      description: 'if matches is false: explain exactly what differs (wrong number, wrong period, metric not present, wrong document, etc.); empty string if matches is true',
    },
  },
  required: ['matches', 'evidence_quote', 'discrepancy'],
}

const REFUTE_VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    refuted: {
      type: 'boolean',
      description: 'true if you found evidence IN THE CITED FILING that contradicts, undercuts, or is not supported by the claim -- default to true (refuted) if you cannot confirm support, do not give the claim the benefit of the doubt',
    },
    evidence_quote: {
      type: 'string',
      description: 'verbatim quote from the filing that either supports or contradicts the claim',
    },
    reasoning: {
      type: 'string',
      description: 'one or two sentences on why the claim holds up or does not, referencing the quote',
    },
  },
  required: ['refuted', 'evidence_quote', 'reasoning'],
}

function numericPrompt(c) {
  return `You are an adversarial fact-checker for a public research note. Your ONLY job is to determine whether a specific numeric claim is actually supported by its cited SEC EDGAR filing -- you do not get to trust the claim, you must verify it from the source.

Ticker: ${A.ticker}
Metric: ${c.metric} (unit: ${c.unit})
Claim as drafted: ${c.claim_summary}
Cited source: ${c.source_url}

Steps:
1. Fetch ${c.source_url} (use WebFetch; if it is a data.sec.gov JSON API URL, fetch and read the JSON directly).
2. Locate the figure(s) for "${c.metric}" in that exact document.
3. Compare what the filing actually says to the claim as drafted above.
4. If the filing does not contain this metric at all, or you fetch the wrong document, that is matches=false with an explanation -- do not guess or extrapolate a number that is not there.

Call the verdict tool with your finding. Be skeptical: a plausible-sounding number that you cannot actually find quoted in the fetched document is NOT a match.`
}

function refutePrompt(c) {
  return `You are an adversarial reviewer for a public research note. Your job is to try to REFUTE the following qualitative claim using ONLY the cited SEC EDGAR filing -- actively look for reasons it is wrong, overstated, or unsupported. Do not just confirm it.

Ticker: ${A.ticker}
Claim: "${c.claim_summary}"
Context/rationale given: ${c.context || '(none given)'}
Cited source: ${c.source_url}

Steps:
1. Fetch ${c.source_url} (WebFetch).
2. Search for language that CONTRADICTS or fails to support the claim (e.g. the filing says the opposite, is silent on the topic, or gives numbers that undercut the claim).
3. If you cannot find anything in the filing that actually supports the claim either, that also counts as refuted=true (an unsupported claim is not publishable as fact) -- do not default to trusting it.
4. Only set refuted=false if the filing itself clearly backs the claim.

Call the verdict tool with your finding.`
}

// Defensive: some environments deliver `args` as a JSON string rather than the parsed
// object the Workflow tool documents -- handle both rather than assuming.
const A = typeof args === 'string' ? JSON.parse(args) : args

const claims = A.claims || []
const numeric = claims.filter((c) => c.kind !== 'qualitative')
const qualitative = claims.filter((c) => c.kind === 'qualitative')

log(`Fact-check gate for ${A.ticker} ${A.note_type}: ${numeric.length} numeric claim(s), ${qualitative.length} qualitative claim(s)`)

phase('Verify numeric claims')
const numericResults = await parallel(
  numeric.map((c) => () =>
    agent(numericPrompt(c), {
      label: `verify:${c.id}`,
      phase: 'Verify numeric claims',
      schema: NUMERIC_VERDICT_SCHEMA,
    }).then((v) => ({ ...c, verdict: v }))
  )
)

phase('Refute qualitative claims')
const qualitativeResults = await parallel(
  qualitative.map((c) => () =>
    agent(refutePrompt(c), {
      label: `refute:${c.id}`,
      phase: 'Refute qualitative claims',
      schema: REFUTE_VERDICT_SCHEMA,
    }).then((v) => ({ ...c, verdict: v }))
  )
)

const numericFiltered = numericResults.filter(Boolean)
const qualitativeFiltered = qualitativeResults.filter(Boolean)

const passedNumeric = numericFiltered.filter((r) => r.verdict?.matches === true)
const failedNumeric = numericFiltered.filter((r) => r.verdict?.matches !== true)
const passedQualitative = qualitativeFiltered.filter((r) => r.verdict?.refuted === false)
const failedQualitative = qualitativeFiltered.filter((r) => r.verdict?.refuted !== false)

if (failedNumeric.length) {
  log(`${failedNumeric.length} numeric claim(s) FAILED verification: ${failedNumeric.map((r) => r.id).join(', ')}`)
}
if (failedQualitative.length) {
  log(`${failedQualitative.length} qualitative claim(s) could not be confirmed / were refuted: ${failedQualitative.map((r) => r.id).join(', ')}`)
}

return {
  ticker: A.ticker,
  note_type: A.note_type,
  gate_passed: failedNumeric.length === 0 && failedQualitative.length === 0,
  total_claims: claims.length,
  passed: [...passedNumeric, ...passedQualitative],
  failed: [...failedNumeric, ...failedQualitative],
  numeric_results: numericFiltered,
  qualitative_results: qualitativeFiltered,
}
