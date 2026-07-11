# Note frontmatter schema (Session 3)

Every published note (`notes/<TICKER>/<YYYY-MM-DD>_<type>.md`) carries YAML frontmatter.
The design goal: frontmatter fields are **byte-for-byte the same shape** as
`scorecard/calls/<TICKER>.jsonl` / `scorecard/guidance/<TICKER>.jsonl` records
(schema owned by Session 4, `scorecard/SCHEMA.md`). Extracting a call from a note into
its scorecard shard is then a mechanical copy of the object — never a re-interpretation,
never an LLM re-reading prose to guess at a number. `score.py` grades what is in the
`calls:` / `guidance:` blocks below; it never parses the note body.

**This session (S3) does not write to `scorecard/` — that boundary is owned by
Session 4 this phase, and by Session 6/7 in Phase 3 (their kickoff extracts frontmatter
calls into the real shards). Frontmatter is the audit-ready staging format.**

## Required on every note (all three types)

| field | type | notes |
|---|---|---|
| `ticker` | str | uppercase, matches `config/universe.json` |
| `type` | str | `preview` \| `flash` \| `review` \| `initiation` |
| `event_date` | str (ISO date) | the earnings event this note is about |
| `published_at` | str (ISO-8601 datetime) | when the note passed the fact-check gate and was saved final. **Never backdated** (PLAN §6) — a delayed note keeps its honest late timestamp. **Backtest exception:** a note explicitly reconstructing a historical print (stated as such in its opening prose) sets `published_at` to the SIMULATED historical publish time it would have carried; `fact_check.run_at` always carries the REAL time the gate actually ran, so the two intentionally differ for backtests — that gap is not a backdating violation, it's the whole point of the exercise. |
| `period` | str | fiscal period covered, e.g. `FY2027Q1` (fiscal-year-relative, not calendar) |
| `fiscal_year_end` | str | from `config/universe.json`, for reader context |
| `basis` | str | `gaap` \| `non_gaap` — the basis this company guides/reports on |
| `source_filings` | list | every EDGAR document cited in this note — the fact-check gate iterates this list, one verification pass per entry |
| `fact_check` | obj | `{status: passed\|failed\|pending, run_at: <iso>, notes: <str>}` — set by the publish gate, never hand-set to `passed` |

`source_filings` entries:
```yaml
source_filings:
  - description: "Q4 FY2026 earnings 8-K (EX-99.1) — prior-quarter guidance source"
    url: "https://www.sec.gov/Archives/edgar/data/1535527/000153552726000007/crwd-20260303xex991.htm"
  - description: "companyfacts XBRL (revenue, EPS history)"
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0001535527.json"
```

## `guidance:` block — **preview notes only**

A list of records shaped exactly like `scorecard/guidance/<TICKER>.jsonl` (see that
schema for the authoritative field list: `id, ticker, timestamp, metric, unit, basis,
period, guided_at_period, guidance, source_filing, higher_is_better`). This is the
guidance table built from the **prior quarter's** 8-K press release — the benchmark our
calls are graded against (PLAN §3).

## `calls:` block — **every note type**

A list of records shaped exactly like `scorecard/calls/<TICKER>.jsonl` (`id, ticker,
timestamp, call_type, period, metric, unit, basis, source_note, call, actual,
higher_is_better, confidence, rationale`).
`call.kind` ∈ `direction | range | point | qualitative` — see scorecard/SCHEMA.md for the
exact shape of each. A **preview** note's calls are typically `direction` (graded against
the `guidance:` block above) or `range`/`point`. A **flash** note both grades the
preview's calls (fills their `actual`, in the flash's own copy — the scorecard shard gets
the update when frontmatter is extracted) and can add new forward calls (e.g. reaction to
guidance raised/cut). A **review** note reconciles anything the flash could not (10-Q
detail) and may add thesis-level `qualitative` calls.

**`call_type` marks when a call was ORIGINALLY made, not which note is currently
displaying it.** When a flash/review note re-declares a preview call to fill in its
`actual` (same `id`, same underlying call), `call_type` stays `preview` — it does not
flip to `flash`/`review` just because a later note is the one resolving it. This is what
keeps score.py's "hit rate by call_type" breakdown meaningful (a call made at preview
time is scored as a preview-time call, regardless of which note eventually grades it).

**No number goes into `calls:` or `guidance:` without a `source_filings` entry it can be
traced to.** This is what the adversarial fact-check gate (see below) verifies before a
note is allowed to become final.

## The PUBLISH GATE (non-negotiable, PLAN §5 / CLAUDE.md)

Before a drafted note is saved as final (i.e. before `fact_check.status` may be set to
`passed` and the file written to `notes/<TICKER>/`), it must pass the adversarial
fact-check workflow in `.claude/skills/_shared/fact_check_workflow.js` (fanned out via
the Workflow tool): one pass per numeric claim in `calls:`/`guidance:` re-verifying the
figure against its cited `source_filings` document, and a refutation pass on every
`qualitative` call. Anything that fails or cannot be verified is **cut from the note or
explicitly flagged `unverified`**, never silently published. A note whose gate fails is
not final — it is redrafted or the unverifiable line is removed. See
`.claude/skills/preview/SKILL.md` (and the flash/review equivalents) for exactly how the
three commands invoke the gate.

## Body (prose, below the frontmatter)

Not machine-read — for humans and for the fact-check agents' qualitative-refutation pass
(which reads the prose adjacent to a `qualitative` call as its context). See
`preview.md` / `flash.md` / `review.md` in this directory for the expected section
headers per type.

## Merge Gate 2 addendum (2026-07-11) — resolutions folded in at the gate

Three contract clarifications applied when Session 4 ran Merge Gate 2. They fix cases the
single CRWD backtest did not exercise but Session 6/7 will hit:

1. **`higher_is_better` is not always `true`.** score.py's `_label` maps above-band →
   *beat* only for higher-is-better metrics; for a cost/capex/opex line (e.g. AMZN or META
   capex/expense guidance) coming in *above* the guide is a *miss*, so those records must
   set `higher_is_better: false` or the scorecard silently inverts. The templates now say
   so inline.
2. **Carry `confidence` when a flash/review resolves a preview call.** The resolving note
   copies the preview call and adds `actual`; that copy is the one extracted to the shard
   (see `.claude/skills/_shared/note_pipeline.md`). If it drops `confidence`, score.py's
   calibration curve never sees the call. The flash template now carries a `confidence:`
   line to copy the preview's value.
3. **Initiation notes** (`type: initiation`, Session 6/7) use the **same `calls:` shape**
   as above with `call_type: initiation`, and **no `guidance:` block** (an initiation sets
   a thesis baseline, it is not graded against a prior quarter's guide). Calls are
   typically `qualitative` thesis statements, or `point`/`range` estimates on a stated
   `basis`; `source_note` points at the initiation note. No dedicated `initiation.md`
   template ships yet — reuse `preview.md`'s frontmatter, drop `guidance:`, set
   `call_type: initiation`. Everything else (basis, source_note, fact-check gate) is
   identical.
