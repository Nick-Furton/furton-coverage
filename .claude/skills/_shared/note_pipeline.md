# Shared note-publishing pipeline (used by /preview, /flash, /review)

This is the one procedure all three commands follow, with only the data sources and
template changing per note type (each SKILL.md says what's specific to it). Keeping the
pipeline in one place means a fix to the publish gate or the frontmatter contract only
has to happen once.

## 0. Resolve the ticker

Look it up in `config/universe.json`. If it's one of the frozen 10, you have its `cik`,
`fiscal_year_end`, `basis`, and `key_kpi_concepts` already -- use them; don't re-derive.
If it's not in the file (someone runs a command on an alternate/candidate name), fall
back to `py scripts/edgar.py cik <TICKER>` and proceed without the KPI list -- edgar.py
and build_model.py both work for any resolvable ticker, not only the frozen roster.

## 1. Pull data through `scripts/edgar.py` -- never any other network path

Run it via `py` with `PYTHONUTF8=1` set (Windows console is cp1252). Which calls to make
depend on the note type -- see the type-specific SKILL.md. Two things every note type
must get right:

- **On print day, pass `force=True`** to `earnings_8k()` / `submissions()` (via the CLI's
  behavior or a short inline script) so a just-filed 8-K isn't served stale from cache.
  Off print day (drafting a preview the night before, or a T+2 review days later), the
  cache is exactly what you want -- don't force-refetch and risk hitting a rate limit for
  no reason.
- **Every number that ends up in the note must trace to a specific fetched document.**
  If you can't say which URL a figure came from, you can't cite it in `source_filings`,
  which means it can't survive the publish gate (step 4) -- so don't draft a claim you
  can't source in the first place.

## 2. Draft the note from `notes/_templates/<type>.md`

Follow `notes/_templates/SCHEMA.md` exactly -- it is the frontmatter contract, and it is
deliberately shaped to be byte-for-byte the same as `scorecard/SCHEMA.md`'s record shapes
(Session 4's schema) so that a later extraction step is a mechanical copy, never a
re-interpretation. Every `calls:` / `guidance:` entry needs its `source_note` /
`source_filing` filled honestly, and `id` following the `<TICKER>-<PERIOD>-<type>-<metric>`
convention so it stays traceable and stable if it's ever copied into a scorecard shard.

Write the prose body too -- the fact-check gate's qualitative-refutation pass reads the
note's own qualitative calls, not the whole prose, but a human reading the published note
still needs the narrative.

## 3. Build the `claims` list for the publish gate

Turn every entry in the drafted `calls:` and `guidance:` frontmatter blocks into one
entry of:

```json
{
  "id": "<same id as the frontmatter record>",
  "kind": "numeric",              // "numeric" for direction|range|point calls and any guidance record; "qualitative" for call.kind == "qualitative"
  "metric": "<metric>",
  "unit": "<unit>",
  "claim_summary": "<one plain-English sentence restating the call, e.g. 'we call BEAT vs guided $1,360.0-1,364.0M'>",
  "source_url": "<the SPECIFIC EDGAR document this figure came from>",
  "context": "<the record's rationale, if any>"
}
```

**Where `source_url` comes from differs by record type** -- `guidance:` records carry
`source_filing` directly (an EDGAR URL); `calls:` records only carry `source_note` (a
repo-relative path to the *note*, not a filing URL). For a call's `source_url`, use
whichever entry in the note's top-level `source_filings:` block is the actual document
the call's benchmark/rationale was drawn from (usually the guidance-source 8-K for a
preview call, the just-filed 8-K for a flash/review call) -- don't literally look for a
`source_filing` field on the call record itself, it isn't there.

Do this for **every** numeric and qualitative record in the note -- don't sample a
subset. A note with 6 calls and only 4 checked is not a note that passed the gate.

**Also add one claim for any other material numeric fact stated as fact in the prose**
that isn't already a formal `calls:`/`guidance:` record -- e.g. a review's "what the
10-Q added" section quoting a specific balance-sheet figure, or a flash's aside about a
metric that isn't itself one of the graded calls. The scorecard schema only captures
falsifiable forward-looking calls; it was never meant to be the sole definition of "a
number this note asserts." A hallucinated deferred-revenue figure in the prose is just
as damaging to credibility as a wrong call, so it gets the same check.

## 4. Run the publish gate

Call the Workflow tool with the script contents of
`.claude/skills/_shared/fact_check_workflow.js` (read the file, pass its text as
`script`) and `args: {ticker, note_type, claims}` (from step 3). This fans out one
agent per numeric claim (re-fetches the cited filing and checks the figure) and one
agent per qualitative claim (tries to refute it) -- see that file's header comment for
the full design rationale. It returns `{gate_passed, passed, failed, numeric_results,
qualitative_results, ...}`.

## 5. Apply the verdict -- never publish an unverified number

For every claim in `result.failed`:
- If the `verdict.discrepancy` / `verdict.reasoning` shows the claim was simply wrong
  (bad figure, wrong period, wrong document), **cut it** from the note's frontmatter and
  prose -- don't publish a corrected guess, either omit the line or, if the underlying
  fact matters to the note, redraft it using the verdict's `evidence_quote` /
  `filing_value` as the corrected source of truth (and re-verify that correction before
  trusting it).
- If the claim was directionally right but the gate couldn't confirm it (e.g. the
  fetch failed, or the metric genuinely isn't machine-findable in that document), mark
  it `"verification": "unverified"` in its frontmatter record and say so plainly in the
  prose next to it -- flagged, not silently dropped, not silently trusted either.

Set the note's `fact_check:` block:
```yaml
fact_check:
  status: passed          # only if result.gate_passed is true AND nothing was cut/flagged
  run_at: "<now, ISO-8601>"
  notes: "<one line: N/M claims verified; list anything cut or flagged>"
```
If anything was cut or flagged, `status` is `failed` even though the note still gets
published (with the bad material removed) -- `failed` here means "the gate caught
something," which is the gate doing its job, not a reason to hide the note. Never
hand-set `status: passed` without having actually run the workflow this session.

A flash/review note's "vs. our calls" table computing an informal HIT/MISS/beat-met-miss
label in prose is fine for same-day readability (that's the whole point of a flash), but
it is **not** the scorecard's authoritative grade -- `scripts/score.py` grades
deterministically once the call is extracted into a shard (PLAN §3: "no LLM in the
grading path"). Say so in the note when the classification involves any judgment call
(e.g. an actual disclosed at coarser precision than the guided band), so a reader
doesn't mistake the note's own arithmetic for the public scorecard's final word.

## 6. Write the file

`notes/<TICKER>/<YYYY-MM-DD>_<type>.md`. If a file already exists for that exact date +
type, this is a correction -- do not overwrite it silently; append a dated addendum
note in the body instead (PLAN §7: "never quietly edit a published call").

## 7. Tell the user what happened

Report: how many claims passed/failed the gate, exactly what (if anything) was cut or
flagged and why, and the file path written. If the gate cut something material, say so
plainly rather than quietly shipping a thinner note.

## Not yet wired: scorecard append

These commands draft the note and run the publish gate; they do **not** append the
`calls:`/`guidance:` frontmatter into `scorecard/calls/<TICKER>.jsonl` /
`scorecard/guidance/<TICKER>.jsonl` -- that boundary belongs to Session 6/7 this phase
(their kickoff literally does the extraction step once the scorecard/notes wiring is
confirmed at Merge Gate 2). Once that's settled, extending these commands to also append
matching entries in step 6 is the natural next step for the steady-state cadence
(PLAN §6) -- flagged here so whoever automates that (Session 8) knows where to hook in.

**One extraction gotcha to design around:** a preview call and its later flash/review
grading of that SAME call share one `id` on purpose (the flash literally copies the
preview's call record and adds `actual`) -- that's one call whose lifecycle spans two
notes, not two calls. Whoever wires the append step must extract each `id` into
`scorecard/calls/<TICKER>.jsonl` **exactly once**, from whichever note is the first to
carry a resolved `actual` for it (typically the flash, or the review if the flash left
it pending) -- never from both notes, or `score.py`'s `_assert_unique_ids` guard
(scorecard/SCHEMA.md) raises on the duplicate `id` the moment both get appended.

**Second gotcha (carry originating-note-only fields):** the note that resolves a call
(the flash/review) must copy the call record from the preview *verbatim* and only add
`actual` -- in particular it must preserve `confidence`, which the preview set and which
the flash otherwise silently drops. The extracted-once record is the flash's copy, so if
that copy lacks `confidence`, `score.py`'s calibration curve never sees the call and the
public reliability chart stays empty. Flash/review template blocks carry a `confidence:`
line for this reason; keep it equal to the preview's value.
