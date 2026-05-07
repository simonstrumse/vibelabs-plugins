---
name: pre-flight
description: Stakeholder reaction simulation for corporate communications. Pressure-tests a statement, press release, positioning deck, earnings script, M&A announcement, comment letter, or rebrand narrative against a cast of dynamically-researched stakeholders (journalists, activists, scientists, regulators, customers, investors, internal staff, proxy advisors) before you publish. Scopes the run via AskUserQuestion, composes the right mode from a library (crisis pre-flight, tabletop, launch pre-mortem, regulatory response, deal comms, earnings rehearsal, positioning pressure test, counterfactual compare, red-team read, activist-proxy, exec-transition, internal-first), builds a factbase and persona cast from public sources, runs the simulation with quality gates, emits a mode-keyed report plus canonical artifacts (holding statement, Q&A doc, message house, stakeholder heat map, day-1/30/100 plan). Triggers on "simulate reactions", "pressure-test this release", "red team this", "how would X react", "stakeholder simulation", "crisis pre-flight", "tabletop", "messaging review", "statement stress test", "Pre-Flight", "synthetic focus group for comms".
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(python3 *), Write, AskUserQuestion, Agent(scoping-designer, ground-truth-researcher, persona-architect, persona-researcher, persona-worker, critic, social-simulator, memory-keeper, debate-moderator, counterfactual-comparator, synthesizer)
model: claude-opus-4-7
effort: high
---

# Pre-Flight orchestrator — stakeholder reaction simulation

You orchestrate a multi-agent simulation that tells a comms team how a representative cast of real stakeholders would react to a stimulus — before publication. You are industry-agnostic: factbase and persona cast are researched per run from public sources. No content ships with the skill.

`$ARGUMENTS` may contain: a path to the stimulus, inline text, or a short brief ("rebrand narrative for a Norwegian salmon ASA; pressure-test against investors + regulators"). If you receive only a brief with no explicit stimulus, ask for one before proceeding — nearly every mode requires a concrete artifact to test against.

**Plan approval is not optional.** The user reviews the composed run-plan AND the persona cast before any expensive research fires. Do not skip this gate.

---

## Working directory

Create `pre-flight-runs/run-$(date +%Y%m%d-%H%M%S)/` at the user's working dir (not inside the skill). All artifacts land here:

```
pre-flight-runs/<run>/
├── stimulus.md                # the material under test
├── user-answers.yaml          # captured AskUserQuestion answers
├── run-plan.yaml              # emitted by scoping-designer; approved by user
├── factbase.md                # emitted by ground-truth-researcher
├── cast-spec.md               # emitted by persona-architect; approved by user
├── personas/<id>.md           # one per persona, from persona-researcher
├── findings/
│   ├── persona-<id>.md        # first-round reactions
│   ├── critic-<id>.md         # critic verdicts
│   ├── persona-<id>-final.md  # post-critic reactions
│   ├── social-<pair>.md       # optional, social-dynamics phase
│   ├── debate-<pair>.md       # optional, debate phase
│   └── counterfactual-delta.md # optional, counterfactual-compare mode
├── memory/<id>.md             # optional, memory-update phase, within-run scope
├── artifacts/                 # mode-specific (holding-statement, qa-doc, message-house, etc.)
└── report.md                  # final synthesis
```

Cross-run memory, when opted in, writes to `pre-flight-memory/<industry>/` in the user's working dir — never inside the skill.

---

## Phase 0 — Capture the stimulus and scope the run

1. **Load stimulus.** If the user pasted text, write it verbatim to `stimulus.md`. If a path, copy it. If only a brief, ask for the actual artifact (draft, narrative, deck). Stimulus is required.
2. **Flag MNPI.** If the stimulus looks like earnings / deal / regulatory filing content, ask the user once: "This looks like it may contain material non-public information. Running the skill sends content through Anthropic's infrastructure. Continue?" Record their answer in `user-answers.yaml`. Proceed only on explicit yes.
3. **Scoping questions via AskUserQuestion.** Fire 1-3 questions to capture mode intent. The answers feed the scoping-designer.

Example question set — adapt to the stimulus:

- **Q1 (always):** "What kind of pressure test?" — options covering the mode catalog: Crisis pre-flight (quick, one round) · Crisis tabletop (multi-round with memory + social dynamics) · Product launch · Regulatory response · M&A / deal comms · Earnings / IR · Positioning / rebrand · Compare multiple drafts (A/B) · Red-team read · Activist / proxy response · Exec transition · Internal / employee-first · Other (you describe).
- **Q2 (conditional, crisis modes):** "Severity?" — low (operational, one channel) · medium (tactical, multi-channel) · high (strategic, enterprise) · critical (acute, ongoing).
- **Q3 (conditional, multi-run stakeholder tracking):** "Enable cross-run stakeholder memory for this industry?" — records opt-in. Default off. Explain once: "Cross-run memory writes summary-only stakeholder files to `pre-flight-memory/<industry>/` in your working dir. Useful for tracking the same stakeholders across a release cadence. Off by default."

Record all answers to `user-answers.yaml`.

---

## Phase 1 — Design + factbase in parallel

In a single assistant turn, spawn two agents concurrently:

```
Agent(scoping-designer):
  stimulus_path: pre-flight-runs/<run>/stimulus.md
  user_answers_path: pre-flight-runs/<run>/user-answers.yaml
  modes_dir: ${CLAUDE_SKILL_DIR}/modes
  modes_index_path: ${CLAUDE_SKILL_DIR}/modes/_index.md
  phase_library_path: ${CLAUDE_SKILL_DIR}/reference/phase-library.md
  run_plan_schema_path: ${CLAUDE_SKILL_DIR}/templates/run-plan.schema.yaml
  methodology_sources_path: ${CLAUDE_SKILL_DIR}/reference/methodology-sources.md
  output_path: pre-flight-runs/<run>/run-plan.yaml
  task_template: ${CLAUDE_SKILL_DIR}/templates/scoping-task.md

Agent(ground-truth-researcher):
  stimulus_path: pre-flight-runs/<run>/stimulus.md
  run_plan_path: pre-flight-runs/<run>/run-plan.yaml    # may not exist yet; researcher waits if so — orchestrator re-spawns after run-plan lands if needed
  factbase_schema_path: ${CLAUDE_SKILL_DIR}/templates/factbase.schema.md
  output_path: pre-flight-runs/<run>/factbase.md
  task_template: ${CLAUDE_SKILL_DIR}/templates/ground-truth-task.md
```

If factbase needs the run-plan for industry context and the designer is still running, spawn ground-truth-researcher a moment later — the designer is fast (no WebFetch). In practice: spawn designer first, then ground-truth-researcher when designer returns.

### Validate the run-plan

When `run-plan.yaml` lands, validate against `templates/run-plan.schema.yaml`:
- `mode.name` is in `modes/_index.md`
- Every `phases[].name` is in `reference/phase-library.md`
- Depth parameters within published caps (revise cycles ≤ 2; cast size ≤ 20)
- `memory.cross_run_enabled: true` requires `memory.user_consent_recorded: true`

On validation failure, re-spawn scoping-designer with the specific error. Two retries max; after that, surface to the user.

---

## Phase 2 — Design the cast

Once both `run-plan.yaml` and `factbase.md` exist:

```
Agent(persona-architect):
  run_plan_path: pre-flight-runs/<run>/run-plan.yaml
  factbase_path: pre-flight-runs/<run>/factbase.md
  stimulus_path: pre-flight-runs/<run>/stimulus.md
  cast_spec_schema_path: ${CLAUDE_SKILL_DIR}/templates/cast-spec.schema.md
  persona_bundle_schema_path: ${CLAUDE_SKILL_DIR}/templates/persona-bundle.schema.md
  output_path: pre-flight-runs/<run>/cast-spec.md
  task_template: ${CLAUDE_SKILL_DIR}/templates/persona-architect-task.md
```

Validate the cast-spec: size matches run-plan, cluster distribution matches run-plan, every persona has ≥3 source_candidates, deliberately-excluded list non-empty. On failure, re-spawn architect with the error.

---

## Phase 3 — User approval gate

**Hard stop.** Show the user three things inline:

1. `run-plan.yaml` with `designer_reasoning` at the top — the designer's explanation of mode, cast size, phase composition.
2. `cast-spec.md` with design rationale and deliberately-excluded list.
3. `factbase.md` summary — first 20 lines plus the "Researcher's confidence note."

Accept: "go", "run it", "looks good", or edits. User edits may include:
- Change mode
- Resize cast
- Drop or add a persona
- Change cluster distribution
- Drop or add a phase (only published phases allowed)
- Flip cross-run memory opt-in

Apply edits directly to `run-plan.yaml` and `cast-spec.md`. Re-validate. Do not proceed until the user confirms.

---

## Phase 4 — Deep research in parallel

In a single assistant turn, spawn one `persona-researcher` per persona in `cast-spec.md`:

```
Agent(persona-researcher):   # one invocation per persona entry
  cast_entry_path: pre-flight-runs/<run>/cast-spec.md    # architect's entry for this persona
  factbase_path: pre-flight-runs/<run>/factbase.md
  schema_path: ${CLAUDE_SKILL_DIR}/templates/persona-bundle.schema.md
  output_path: pre-flight-runs/<run>/personas/<id>.md
  task_template: ${CLAUDE_SKILL_DIR}/templates/persona-researcher-task.md
```

Fire all N in one turn — they run concurrently. Budget ~90s per researcher. 12-persona cast ≈ 90s wall-clock for the phase.

Post-phase check: any researcher that couldn't hit the named-floor (≥3 signature quotes) will have downgraded `persona_type: archetype`. Note this in the final coverage gaps; do not retry — the downgrade is honest.

---

## Phase 5 — Initial reactions in parallel

```
Agent(persona-worker):   # one per persona
  persona_file: pre-flight-runs/<run>/personas/<id>.md
  stimulus_path: pre-flight-runs/<run>/stimulus.md
  factbase_path: pre-flight-runs/<run>/factbase.md
  output_path: pre-flight-runs/<run>/findings/persona-<id>.md
  schema_path: ${CLAUDE_SKILL_DIR}/templates/reaction-schema.md
  task_template: ${CLAUDE_SKILL_DIR}/templates/persona-task.md
```

All N in one turn, parallel. Workers never see each other's output.

---

## Phase 6 — Critic loop (max 2 revise cycles)

For each reaction, spawn a critic in parallel:

```
Agent(critic):
  persona_file: ...
  reaction_path: findings/persona-<id>.md
  stimulus_path: ...
  factbase_path: ...
  output_path: findings/critic-<id>.md
  rubric_path: ${CLAUDE_SKILL_DIR}/templates/critic-rubric.md
```

For each REVISE verdict:
1. Read `findings/critic-<id>.md` for the specific fixes.
2. Re-spawn the same persona-worker with `revision_note_path: findings/critic-<id>.md` set in the task template variables.
3. Worker writes `findings/persona-<id>.md` again (revision_round: 1).
4. Re-run the critic on the revised reaction (revision_round: 2 trip).
5. On second REVISE fail → KILL → exclude persona from synthesis, note in coverage gaps.

On PASS (or after cycle 2), rename to `findings/persona-<id>-final.md`.

**Escalation check:** if >30% of cast KILL, stop. The stimulus or cast is mismatched; surface to user before synthesizing.

---

## Phase 7 — Optional phases (per run-plan)

Execute in this order if present in the run-plan's `phases` list:

### 7a. `social-dynamics` (crisis-tabletop, deal-comms, M3)

For each pairing in the run-plan's `social-dynamics.pairings`:

```
Agent(social-simulator):
  persona_a_file: ...
  persona_b_file: ...
  reaction_a_path: findings/persona-<a>-final.md
  reaction_b_path: findings/persona-<b>-final.md
  factbase_path: ...
  output_path: findings/social-<pair-id>.md
  task_template: ${CLAUDE_SKILL_DIR}/templates/social-dynamics-task.md
```

All pairings in one turn, parallel.

### 7b. `memory-update` (multi-round modes, M3)

After each round, distill all `persona-<id>-final.md` into memory stubs:

```
Agent(memory-keeper):
  findings_dir: pre-flight-runs/<run>/findings/
  scope: within-run | cross-run   # from run-plan
  industry_key: <string>          # from run-plan (if cross-run)
  output_dir: pre-flight-runs/<run>/memory/   # or pre-flight-memory/<industry>/ for cross-run
  task_template: ${CLAUDE_SKILL_DIR}/templates/memory-update-task.md
```

Cross-run memory is never default. `user_consent_recorded: true` is checked again here; if false, refuse to write cross-run files.

### 7c. `debate` (regulatory-response, earnings-rehearsal, activist-proxy, red-team-read, M3)

For each pairing in the run-plan's `debate.pairings`:

```
Agent(debate-moderator):
  persona_a_file: ...
  persona_b_file: ...
  reaction_a_path: ...
  reaction_b_path: ...
  factbase_path: ...
  exchanges: 3
  output_path: findings/debate-<pair-id>.md
  task_template: ${CLAUDE_SKILL_DIR}/templates/debate-task.md
```

### 7d. `counterfactual` (counterfactual-compare mode only, M3)

For a counterfactual-compare run, Phases 5 and 6 ran N times (one per draft). Now:

```
Agent(counterfactual-comparator):
  drafts: <list>
  reaction_sets: <list of dirs>
  factbase_path: ...
  output_path: findings/counterfactual-delta.md
  task_template: ${CLAUDE_SKILL_DIR}/templates/counterfactual-task.md
```

---

## Phase 8 — Synthesize

```
Agent(synthesizer):
  findings_dir: pre-flight-runs/<run>/findings/
  stimulus_path: ...
  plan_path: pre-flight-runs/<run>/run-plan.yaml
  factbase_path: ...
  output_path: pre-flight-runs/<run>/report.md
  skeleton_path: ${CLAUDE_SKILL_DIR}/templates/report-skeletons/<mode>.md
  artifacts_dir: pre-flight-runs/<run>/artifacts/
  social_findings_dir: pre-flight-runs/<run>/findings/   # optional, present if social-dynamics ran
  debate_findings_dir: pre-flight-runs/<run>/findings/   # optional, present if debate ran
```

Synthesizer produces `report.md` + the mode's artifacts under `artifacts/`.

---

## Phase 9 — Verify quotes

```
!python3 ${CLAUDE_SKILL_DIR}/scripts/verify_quotes.py pre-flight-runs/<run>/
```

If the script flags unverified quotes, re-spawn synthesizer with a `CORRECTIONS:` block listing the flagged quotes. Max one retry.

---

## Phase 10 — Present

1. Present `report.md` inline. Truncate cleanly at ~1500 words with a pointer to the full file.
2. List the artifacts emitted (holding-statement, qa-doc, etc.) with paths.
3. Offer follow-ups:
   - Add a specific missing persona (runs a single persona-researcher + worker + critic)
   - Deep-dive on a disagreement axis (runs `debate` phase between the two named personas)
   - Revise the stimulus based on the report and re-run (new run, factbase + personas reusable)
   - Compare this stimulus with an alternative draft (re-run in `counterfactual-compare` mode)

---

## Hard rules

- **Plan approval is not optional.** If the user says "just run it," still show the plan and accept a one-word confirmation — the plan step catches miscast personas and mode mismatches cheaply.
- **Validate against schemas.** The run-plan, cast-spec, persona bundle, and reaction are all schema-gated. Reject and re-prompt on violations. Do not silently fix.
- **Personas never see each other's reactions** before submitting their own. Parallel isolation.
- **Never invent a quote.** Only text personas actually wrote. `verify_quotes.py` enforces.
- **Never break the fourth wall inside persona prompts.** Personas live in their world. You (the orchestrator) may break frame when talking to the user; workers and critics never do.
- **Respect `use_constraint`.** The synthesizer handles named-person attribution per bundle constraints. Default: internal rehearsal only.
- **Match report depth to input depth.** A 150-word statement doesn't need a 2500-word report.
- **Empty findings dir is a bug.** Never produce a report with zero worker outputs. Surface to user.
- **Named people only with ≥3 verbatim signature quotes.** Otherwise archetype — no named attribution to a real individual.
- **If MNPI**, warn once and continue only on explicit confirmation.
- **Cross-run memory is opt-in.** Never default-enable. Writes summary-only, never full reactions.

---

## Implementation references

Architecture follows the [orchestrator-worker pattern](https://www.anthropic.com/engineering/built-multi-agent-research-system) (Opus lead + Sonnet workers + Opus synth = 90% uplift over single-agent). Persona-fidelity approach is grounded in [Park et al. 2024 "Generative Agent Simulations of 1,000 People"](https://arxiv.org/abs/2411.10109) (multi-lens expert reflection, interview-grounded bundles). Drift mitigation (signature_opener, forbidden_phrases, rhetorical_constraints) is grounded in [Li et al. 2024 on persona drift](https://arxiv.org/abs/2402.10962). Critic loop is Constitutional AI ([Bai et al.](https://arxiv.org/abs/2212.08073)). Stakeholder salience framework is [Mitchell-Agle-Wood 1997](https://www.ronaldmitchell.org/publications/mitchell%20and%20agle%201997.pdf). Stakeholder taxonomy is [Freeman 1984](https://en.wikipedia.org/wiki/Stakeholder_theory). Red_lines grounded in Fisher/Ury BATNA.

Real-world workflow anchors: H+K FlightSchool+, Polpeo, Weber Shandwick FireBell, Edelman Social-Issue Crisis Simulation, Brunswick 360°, FGS Global, APCO, NIRI, RepTrak, Interbrand, Lippincott, IABC Handbook cascade, Siegel+Gale, Brunswick/FGS/Joele Frank/Sard Verbinnen/Kekst CNC deal-comms playbooks. See `reference/methodology-sources.md` for citations. Original inspiration: [Pre-Flight / CAMEL-AI OASIS](https://github.com/camel-ai/oasis).
