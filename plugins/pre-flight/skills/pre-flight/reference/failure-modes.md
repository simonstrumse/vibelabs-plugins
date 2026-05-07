# Failure modes and their signatures

Read this when a simulation output feels off. Each failure has a signature the orchestrator can detect and a corrective action. Updated for V2 (mode-routed, agent-architected skill).

---

## V1 failure modes (still apply)

### Sycophantic collapse

**Signature.** All personas land in "skeptical" or "neutral" sentiment regardless of stimulus. Reactions open with "I appreciate…", "Overall…", "While there are some concerns…". Hostile personas sound reasonable. Transactional personas sound enthusiastic.

**Root cause.** Claude's helpful-assistant attractor pulls personas toward politeness. Most common with hostile personas on first-pass.

**Fix.**
- Critic catches this with "non-sycophantic" criterion.
- Persona bundle must carry a `signature_opener` the worker prepends, and a `forbidden_phrases` list the critic hard-blocks on. If the bundle lacks these, the persona-researcher produced a weak bundle — regenerate with that persona marked for redo.
- If >30% of a run trips non-sycophantic, surface to user: the cast may be miscast for the stimulus.

---

### Factual drift

**Signature.** Personas reference facts that don't appear in the stimulus or factbase. Invented statistics. Wrong acquisition or leadership history.

**Root cause.** Factbase wasn't read, or the stimulus ambiguity forced speculation. More common when Claude's training data has a stale fact about the company that the factbase didn't explicitly counter.

**Fix.**
- Confirm `factbase_path` is in the spawn message.
- Add the specific drifted fact to the factbase's "What personas should NOT do" section with an explicit correction.
- If the factbase is ≥90 days old, regenerate it (ground-truth-researcher).

---

### Cross-contamination

**Signature.** Personas quote each other. Reactions converge on identical phrasings. The cast reaches consensus too cleanly.

**Root cause.** Workers reading each other's files. Usually a path bug.

**Fix.** Confirm each worker's system message includes only `persona_file`, `stimulus_path`, `factbase_path`, `schema_path`, and (optionally) `prior_memory_path` + `revision_note_path`. Never sibling findings.

---

### Persona bleed

**Signature.** Same-cluster personas (e.g. two activists) produce indistinguishable reactions. Shuffling names wouldn't change the report.

**Root cause.** Persona bundles too thin or too similar. Signature_quotes collection is weak. Rhetorical_constraints not differentiated.

**Fix.** Enrich the bundles. Each persona needs ≥3 signature quotes the others don't have, ≥4 forbidden_phrases specific to their voice, and a distinct signature_opener. If two bundles share openers, re-fire persona-researcher on the weaker one.

---

### Invented quotes in the report

**Signature.** A quote attributed to a persona in `report.md` doesn't match any text in `findings/persona-<id>-final.md`.

**Root cause.** Synthesizer paraphrasing and presenting as quotation.

**Fix.** `scripts/verify_quotes.py` catches this. Synthesizer reruns with a CORRECTIONS block. If it happens twice on a single run, surface to user — the synthesizer prompt needs tightening at the skill level.

---

### Coverage-gap silence

**Signature.** Report reads as complete. No "Coverage gaps" section, or it's empty.

**Root cause.** Synthesizer over-confident. The plan consciously skipped personas or the critic KILLed some, and the synthesizer didn't carry that forward.

**Fix.** Synthesizer reads `plan_path` (cast-spec's deliberately-excluded list) and `findings/critic-*.md` (for KILL verdicts). Both streams feed Coverage gaps. Non-negotiable.

---

### Scope mismatch

**Signature.** Report is longer and deeper than the stimulus warrants. 2,500-word report on a 150-word statement.

**Root cause.** Default cast was too large for the stimulus.

**Fix.** Scoping-designer should right-size the cast. The orchestrator surfaces the run-plan to the user who can reduce size at the approval gate.

---

### Red-line silence

**Signature.** The stimulus crosses a persona's stated red_line but the reaction glosses over it.

**Root cause.** Sycophantic collapse variant. Or the persona bundle's red_lines field is too abstract.

**Fix.** Critic's "within red_lines" criterion catches this. If it doesn't, the bundle's red_lines are probably vague — rewrite them with concrete trigger phrases grounded in the factbase.

---

### Confidence inflation

**Signature.** All personas report `confidence: 0.8+`. No thin-read reactions.

**Root cause.** Prompt framing pushes personas toward strong takes even when the real person wouldn't have one.

**Fix.** The persona-worker template explicitly allows low confidence. If every run is high-confidence across many runs, revisit the `reaction-schema.md` field guidance.

---

## V2 failure modes (new in this architecture)

### Persona-research shallowness

**Signature.** A persona-researcher writes a bundle with <3 verbatim signature quotes, placeholder text in one or more sections, or sources dated >90 days.

**Root cause.** The public record for this person is thinner than the architect estimated.

**Fix.** The bundle is automatically downgraded to `persona_type: archetype`. Named-person attribution is stripped. The synthesizer quotes the persona as an archetype ("a trade-press reporter said..."). Surface the downgrade in Coverage gaps. Do not retry — the downgrade is honest.

---

### Factbase staleness

**Signature.** Factbase's newest source is >90 days old. The stimulus references events not captured in the factbase's recent-events section.

**Root cause.** Ground-truth-researcher's freshness window was too wide, or the stimulus is post-factbase.

**Fix.** Regenerate the factbase with `freshness_window_days: 30` (or 7 for critical severity). If the stimulus references events even fresher than that, surface to user — the researcher needs a targeted WebFetch pass.

---

### Mode misfit

**Signature.** Scoping-designer picked `earnings-rehearsal` but the stimulus is actually a crisis statement. Or picked `crisis-pre-flight` for an M&A announcement. Report reads as structurally wrong.

**Root cause.** Designer over-weighted stimulus type (press release format) over situation (acute crisis in progress).

**Fix.** User catches at the approval gate. Scoping-designer emits `designer_reasoning` that the user reads first — mode override happens there. Orchestrator re-runs scoping-designer with the user's mode override.

---

### Plan grammar violation

**Signature.** Scoping-designer emits a run-plan with an unknown mode name, an unknown phase name, or depth parameters out of published caps.

**Root cause.** Designer drifted or hallucinated a new phase.

**Fix.** Orchestrator validates against `reference/phase-library.md` + `modes/_index.md` + `templates/run-plan.schema.yaml` on load. Rejects + re-spawns designer with the specific error. Two retries max; on third failure, surface to user.

---

### Cast-spec violation

**Signature.** Persona-architect emits a cast-spec with size off, cluster distribution off, empty deliberately-excluded list, or personas missing source_candidates.

**Fix.** Orchestrator validates against `templates/cast-spec.schema.md`. Rejects + re-spawns architect with the error. Two retries max.

---

### Social-dynamics collapse

**Signature.** `social-dynamics` phase pairings converge to agreement. Second-round reactions reconcile differences rather than sharpening them.

**Root cause.** Personas are modeling a dialogue rather than simulating their real-world response to the other's position. Helpful-assistant attractor re-enters via the social-simulator.

**Fix.** Use `debate-moderator` phase instead (adversarial framing) for pairings where convergence is unrealistic. The designer should flag high-antagonism pairings for debate rather than social-dynamics.

---

### Memory drift (cross-run)

**Signature.** Cross-run memory from a prior run injects facts into this run's personas that don't belong — e.g. a persona's posture is anchored in a previous stimulus rather than the current one.

**Root cause.** Memory should be summary-only (posture, sentiment delta, standout framing) — never full reactions. If the memory-keeper wrote too much, it contaminates.

**Fix.** Memory-keeper `style: summary-only` is hard-enforced; it must not emit reactions verbatim. If contamination is suspected, flush `pre-flight-memory/<industry>/<persona-id>.md` and re-run with `cross_run_enabled: false`.

---

### Revise-loop exhaustion

**Signature.** A persona's reaction REVISEs twice then gets KILLed. Persona excluded from synthesis.

**Root cause.** Persona bundle is malformed (weak signature_opener, vague red_lines, missing forbidden_phrases) or the stimulus genuinely doesn't activate this persona's voice.

**Fix.**
- If one-off: accept the KILL, note in Coverage gaps. Single persona failing out of 12 is normal.
- If a pattern: regenerate the persona bundle (re-fire persona-researcher). Or drop the persona from the cast if the stimulus doesn't concern them.
- Revise cycles are capped at 2 per Park/Roleplay-doh — more cycles drift further, not less.

---

### Architect-researcher signal mismatch

**Signature.** Architect marked persona as `named`; researcher couldn't find ≥3 quotes and downgraded to `archetype`. Many downgrades = architect over-confident.

**Root cause.** Architect used stakeholder ecosystem map too optimistically; didn't re-check recent public record.

**Fix.** Downgrades are automatic and safe. If ≥30% of a cast downgrades, surface to user — the industry may not have enough named public-record personae for this mode. Consider switching to a more archetype-friendly cluster distribution.

---

### Use-constraint leakage

**Signature.** A named persona's `use_constraint` is "internal rehearsal only, not for public-facing output" but the synthesizer attributed quotes to the named person in a public-facing artifact.

**Root cause.** Synthesizer didn't check the `use_constraint` field on bundle load.

**Fix.** Synthesizer reads every bundle's frontmatter before writing. If `use_constraint` blocks public-facing attribution and the mode's output class is public-facing, strip to archetype quotation and note in the appendix. The orchestrator should validate this on report emission.

---

## Detection patterns

Most of these surface through one of three gates:
1. **Critic verdict patterns** — >30% REVISE or KILL signals a bundle or cast problem.
2. **`verify_quotes.py` failures** — invented quotes or `use_constraint` leakage.
3. **User reading the report** — some failures (sycophantic collapse, persona bleed, mode misfit) are perceptual. The user's first-read reaction at the approval gate catches these cheaply.

If any failure mode isn't caught by any of these gates within two runs, that's the next diagnostic priority — add detection, don't paper over.
