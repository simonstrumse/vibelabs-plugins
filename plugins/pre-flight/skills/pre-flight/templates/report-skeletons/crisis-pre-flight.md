# Report skeleton — `crisis-pre-flight`

Extends `_core.md`. All universal sections inherited. Mode-specific additions slot between "Proposed revisions" and "Coverage gaps." Artifacts are emitted as separate files.

## Header line

Use this exact line on the report:

**Run:** <run-id> · **Mode:** crisis-pre-flight · **Severity:** <low | medium | high | critical> · **Personas consulted:** <n> · **Stimulus:** <one-line>

## Mode-specific sections

Insert these between the inherited "Proposed revisions (≤5)" and "Coverage gaps":

### 72-hour risk projection

What is likely to happen in the first 72 hours after this stimulus is published, grounded in the reactions. For each time-bucket, cite the persona(s) whose reaction motivates the projection.

- **Hour 0-6.** Who reacts first? What do they say? (Pull from would_act: yes personas with high-urgency salience.)
- **Hour 6-24.** Who picks up? Which trade press / beat journalists amplify?
- **Hour 24-72.** Which secondary actors (peer companies, regulators, analysts) enter the conversation?

Caveat: this is a projection, not a prediction. It's the best-effort reading of the reactions on hand.

### Highest-leverage edits (Top 3)

The three most impactful edits to the stimulus, ranked. Each edit:

1. **<edit title>** — Before: "<stimulus line>". After: "<suggested line>". Moved: <which personas' posture would shift and how>. Cost: <any downside, e.g. dilutes a key message, annoys another cluster>.
2. ...
3. ...

This section differs from "Proposed revisions" by being ranked and budget-aware. Proposed revisions is the full list (up to 5); Highest-leverage edits is the top-3 with cost-awareness.

### Escalation triggers

If any of these happen post-publication, the team should move from pre-flight mode to live-crisis mode. Pulled from red-line warnings.

- If <trigger event>: <which persona's red_line is crossed> → <their likely action> → <what the team should pre-stage now>
- ...

## Artifacts emitted

The synthesizer writes the following to `artifacts_dir/`:

### `holding-statement.md`

Template at `templates/artifacts/holding-statement.md`. Fill-in-the-blank, deployable in 15 minutes. Grounded in the consensus signals from the reactions.

### `qa-doc.md`

Template at `templates/artifacts/qa-doc.md`. 20-50 anticipated questions. Questions drawn from: red_line warnings (hostile questions), disagreement axes (clarification questions), surprise signals (angle-specific questions). Each with a model answer that doesn't cross any persona's red_line.

### `message-house.md`

Template at `templates/artifacts/message-house.md`. Roof narrative (single sentence aligning all personas' positive framings where any exist) + 3 pillars (drawn from consensus signals) + proof points (drawn from factbase + non-hostile persona reactions).

### `stakeholder-heat-map.md`

Template at `templates/artifacts/stakeholder-heat-map.md`. Power × Legitimacy × Urgency per Mitchell-Agle-Wood 1997. Rendered as a markdown table with one row per persona.

## Length target

Report: ~1600 words (12-persona cast). Artifacts each ~400-800 words.

## Quote verification

Every quoted string in the report traces to a findings file. `scripts/verify_quotes.py` enforces.
