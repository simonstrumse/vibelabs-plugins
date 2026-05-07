# Phase library

Catalog of all phases the scoping-designer may compose into a run-plan. The orchestrator rejects any phase name not listed here. Each phase has a stable I/O contract; the runtime implementation is in `templates/phases/<name>.md`.

Phases are listed in their natural execution order. Not every mode uses every phase — the mode files in `modes/` compose their own phase subset.

---

## `factbase`

**Purpose.** Build the shared ground-truth file all personas read. Prevents factual drift.

**Agent.** `ground-truth-researcher` (Sonnet 4.6)
**Inputs.** `stimulus_path`, `run_plan_path`, `factbase_schema_path`
**Output.** `pre-flight-runs/<run>/factbase.md`
**Params.**
- `freshness_window_days`: int (default 30; critical mode: 7; high: 14; low/medium: 30)
- `web_fetch_budget`: int (default 8)

**Exit gate.** Minimum 10 sources, at least one ≤`freshness_window_days` old, "What personas should NOT do" section non-empty.

---

## `cast-design`

**Purpose.** Pick the specific personas to simulate. Salience-score every candidate. Emit a cast-spec the user can approve or edit.

**Agent.** `persona-architect` (Opus 4.7)
**Inputs.** `run_plan_path`, `factbase_path`, `stimulus_path`, `cast_spec_schema_path`, `persona_bundle_schema_path`
**Output.** `pre-flight-runs/<run>/cast-spec.md`
**Params.**
- `use_salience_scoring`: bool (default true)

**Exit gate.** Cast size matches run-plan; cluster distribution matches run-plan; every persona has ≥3 source_candidates; deliberately excluded list non-empty; at least one Tier-1 salience present (or explicit flag if not).

**User approval gate.** The orchestrator pauses here. User reviews cast-spec, can edit freely, confirms before `deep-research` fires.

---

## `deep-research`

**Purpose.** Build one persona bundle per entry in the cast-spec. Parallel subagent execution.

**Agent.** `persona-researcher` (Sonnet 4.6), spawned N times in parallel.
**Inputs per spawn.** `cast_entry_path` (one entry from cast-spec), `factbase_path`, `schema_path` (persona-bundle.schema.md), `output_path` (persona-specific)
**Output.** N files at `pre-flight-runs/<run>/personas/<id>.md`
**Params.**
- `parallelism`: int (default = cast size; max 20)
- `per_persona_timeout_s`: int (default 120)

**Exit gate.** Every bundle meets schema minima (≥3 signature quotes for named; ≥4 concerns; ≥4 forbidden_phrases; ≥3 rhetorical_constraints; ≥3 red_lines; provenance complete). Failures downgrade to archetype or are flagged in coverage gaps.

---

## `initial-reactions`

**Purpose.** Each persona reacts to the stimulus independently. No cross-contamination — workers never see each other's output.

**Agent.** `persona-worker` (Sonnet 4.6), spawned N times in parallel.
**Inputs per spawn.** `persona_file`, `stimulus_path`, `factbase_path`, `schema_path` (reaction-schema.md), `output_path`
**Output.** N files at `pre-flight-runs/<run>/findings/persona-<id>.md`
**Params.**
- `parallelism`: int
- `prepend_signature_opener`: bool (default true)

**Exit gate.** Every worker returns a well-formed reaction file or a structured error. Orchestrator moves forward even if 1-2 workers fail (documented in coverage gaps).

---

## `critic`

**Purpose.** Quality-gate each reaction against the rubric. Revise or kill.

**Agent.** `critic` (Sonnet 4.6), spawned N times in parallel.
**Inputs per spawn.** `persona_file`, `reaction_path`, `stimulus_path`, `factbase_path`, `rubric_path` (critic-rubric.md), `output_path`
**Output.** N files at `findings/critic-<id>.md` (PASS/REVISE/KILL verdict). On REVISE, re-spawn `persona-worker` with the critic's revision note, producing `findings/persona-<id>-final.md`.
**Params.**
- `parallelism`: int
- `max_revise_cycles`: int (hardcoded cap: 2)

**Exit gate.** Every persona either has a PASS or a KILL verdict. If >30% of cast KILL, orchestrator surfaces to user — the stimulus or persona cast is mismatched.

---

## `social-dynamics` *(optional)*

**Purpose.** Model how stakeholders respond to each other's public positions. Inter-persona reply round.

**Agent.** `social-simulator` (Sonnet 4.6)
**Inputs.** Pairs of (persona_A, reaction_A, persona_B, reaction_B) + factbase
**Output.** `findings/social-<pair-id>.md` per pairing
**Params.**
- `pairings`: enum (natural-antagonist | cross-cluster | explicit)
- `rounds`: int (default 2)

**Exit gate.** Every pairing produces two second-round reactions (one per persona responding to the other). Synthesizer gets a "Coalition dynamics" section in the report.

**Milestone.** M3.

---

## `memory-update` *(optional)*

**Purpose.** Distill prior-round reactions into memory stubs that the next round's persona-worker reads.

**Agent.** `memory-keeper` (Haiku 4.5)
**Inputs.** All `persona-<id>-final.md` files from round N
**Output.** `memory/<persona-id>.md` per persona (summary-only; no full reactions)
**Params.**
- `scope`: enum (within-run | cross-run)
- `style`: summary-only (always; no full reactions persisted)

**Cross-run gate.** `cross-run` scope requires explicit `user_consent_recorded: true` in the run-plan. Memory writes to `pre-flight-memory/<industry>/<persona-id>.md` in the user's working dir, never in the skill dir.

**Milestone.** M3.

---

## `debate` *(optional)*

**Purpose.** Adversarial exchange between natural antagonists or mode-specific pairings (e.g. analyst Q&A for earnings, activist-vs-regulator for policy).

**Agent.** `debate-moderator` (Opus 4.7)
**Inputs.** Pair of personas + their first-round reactions + factbase
**Output.** `findings/debate-<pair-id>.md` (3-exchange transcript)
**Params.**
- `exchanges`: int (default 3)
- `pairings`: list of (persona_a, persona_b) tuples

**Milestone.** M3.

---

## `counterfactual` *(optional, counterfactual-compare mode only)*

**Purpose.** Same cast reacts to N drafts. Produces a delta report.

**Agent.** `counterfactual-comparator` (Opus 4.7)
**Inputs.** N drafts + full reaction sets for each draft + factbase
**Output.** `findings/counterfactual-delta.md`
**Params.**
- `drafts`: list of paths (2-4 drafts)

**Milestone.** M3.

---

## `synthesis`

**Purpose.** Assemble the final report per the mode-keyed skeleton. Emit mode-specific artifacts.

**Agent.** `synthesizer` (Opus 4.7)
**Inputs.** All `persona-<id>-final.md` files, optionally social/debate/counterfactual findings, stimulus, plan, factbase, skeleton_path, artifacts_dir.
**Output.** `report.md` + artifact files under `artifacts/`
**Params.**
- `skeleton_path`: string (mode-specific)
- `artifacts`: list of artifact names (mode-specific: holding-statement, qa-doc, message-house, stakeholder-heat-map, day-1-30-100-plan, mock-analyst-qa, cascade-pack, comment-letter, reputation-scorecard, counterfactual-delta)

**Exit gate.** `scripts/verify_quotes.py` returns 0. Every quoted string in `report.md` appears verbatim in a findings file or in the stimulus. On failure, orchestrator passes a CORRECTIONS block back to the synthesizer for one retry.

---

## Phase composition rules

- `factbase` → `cast-design` → `deep-research` → `initial-reactions` → `critic` — **mandatory pipeline head.** Every mode uses these five phases in this order.
- `synthesis` — **mandatory pipeline tail.** Always last.
- Optional phases (`social-dynamics`, `memory-update`, `debate`, `counterfactual`) go between `critic` and `synthesis`, in that order when multiple are present.
- `memory-update` with scope `cross-run` requires `memory.user_consent_recorded: true` at the run-plan level.
- `counterfactual` is only valid in `counterfactual-compare` mode. Unique per-phase mode coupling.

## Unknown phases

The orchestrator validates the run-plan against this phase list on load. An unknown phase name triggers immediate rejection and re-prompts the scoping-designer with the error. No silent fallthrough.
