# Pre-Flight — stakeholder reaction simulation skill

A Claude Code skill that pressure-tests any corporate communication by spawning a dynamically-researched cast of stakeholder persona subagents in parallel, critic-passing each reaction, and synthesizing a mode-keyed report with canonical PR artifacts.

Industry-agnostic. Nothing ships with the skill — the factbase and persona cast are built per run from public sources. Grounded in real PR practice (H+K FlightSchool+, Polpeo, Edelman, Brunswick, FGS, NIRI, APCO, IABC) and multi-agent research (Park et al. 2024, Li et al. 2024, Constitutional AI).

---

## What it does

You paste a stimulus — a press release draft, statement, positioning deck, earnings script, comment letter, rebrand narrative, M&A announcement. The skill:

1. **Scopes the run.** Asks 1-3 questions via AskUserQuestion to classify the work: crisis pre-flight, tabletop, launch, earnings, deal comms, regulatory response, positioning test, counterfactual compare, red-team read, activist-proxy, exec-transition, or internal-first.
2. **Designs the run.** A scoping-designer agent composes a validated run-plan (mode, phases, cast, depth, artifacts) from the published phase library. No invented phases.
3. **Builds the factbase.** A ground-truth-researcher agent pulls corporate structure, recent events, regulatory baseline, controversies, standard framings, stakeholder ecosystem map, and drift-prevention list from 10+ public sources.
4. **Architects the cast.** A persona-architect agent emits a cast-spec with salience scoring (Mitchell-Agle-Wood 1997 Power × Legitimacy × Urgency), named-vs-archetype decisions, and source candidates per persona.
5. **Pauses for approval.** You review the run-plan AND the cast before any expensive research fires.
6. **Researches personas in parallel.** One persona-researcher per cast entry, building an interview-grade bundle (≥3 verbatim signature quotes with source URLs, voice, signature_opener, forbidden_phrases, rhetorical_constraints, red_lines, multi-lens expert reflections per Park et al. 2024).
7. **Spawns reactions in parallel.** Every persona reacts to the stimulus independently. No cross-contamination.
8. **Critic loop.** Each reaction graded against a six-criterion rubric (in-character, forbidden-phrase check, grounded, non-sycophantic, within red_lines, schema-compliant). REVISE cycles capped at 2 per Park/Roleplay-doh literature.
9. **Optional phases.** Social-dynamics (paired replies), memory-update (multi-round + cross-run opt-in), debate (adversarial pairings), counterfactual (A/B drafts) — composed per the run-plan.
10. **Synthesizes.** Mode-keyed report skeleton + canonical artifacts (holding statement, Q&A doc, message house, stakeholder heat map, Day 1/30/100 plan, mock analyst Q&A, cascade pack, comment letter, reputation scorecard, counterfactual delta).
11. **Verifies.** Every quoted line traces to a findings file via `verify_quotes.py`.

Total wall-clock for a 12-persona `crisis-pre-flight` run: ~4-6 minutes. Cost: ~$2.

---

## Install

### From the Vibe Labs marketplace

```bash
claude plugin marketplace add simonstrumse/vibelabs-plugins
claude plugin install pre-flight@vibelabs-plugins
```

Or load directly for a session from a local checkout:

```bash
claude --plugin-dir ./plugins/pre-flight
```

### Invoke

Inside Claude Code, paste the stimulus or ask naturally:

```
Pressure-test this press release against investors, regulators, and trade press — ./releases/q4-2026.md
```

```
Run a crisis pre-flight on this statement. Severity: high.
```

```
Compare these two drafts against the same stakeholder cast — ./draft-A.md and ./draft-B.md
```

The skill triggers on: simulate reactions, pressure-test, red team, how would X react, stakeholder simulation, crisis pre-flight, tabletop, messaging review, statement stress test, Pre-Flight.

---

## Folder layout

```
skill/
├── .claude-plugin/plugin.json
├── skills/pre-flight/
│   ├── SKILL.md                        # mode-routed orchestrator (Opus 4.7)
│   ├── modes/                          # one file per mode + _index.md
│   │   ├── _index.md
│   │   ├── crisis-pre-flight.md        # ✅ M1
│   │   └── (others shipped in M2, M3)
│   ├── reference/
│   │   ├── phase-library.md            # I/O contract per phase
│   │   ├── methodology-sources.md      # evidence trail per mode
│   │   └── failure-modes.md            # debugging guide (V1 + V2)
│   ├── templates/
│   │   ├── run-plan.schema.yaml        # scoping-designer output contract
│   │   ├── factbase.schema.md          # ground-truth-researcher output contract
│   │   ├── cast-spec.schema.md         # persona-architect output contract
│   │   ├── persona-bundle.schema.md    # persona-researcher output contract (v2)
│   │   ├── reaction-schema.md          # persona-worker output contract
│   │   ├── critic-rubric.md            # six-criterion rubric
│   │   ├── persona-task.md             # worker spawn prompt
│   │   ├── scoping-task.md             # designer spawn prompt
│   │   ├── ground-truth-task.md        # researcher spawn prompt
│   │   ├── persona-architect-task.md   # architect spawn prompt
│   │   ├── persona-researcher-task.md  # per-persona researcher spawn prompt
│   │   ├── report-skeletons/
│   │   │   ├── _core.md                # universal sections, all modes inherit
│   │   │   └── crisis-pre-flight.md    # ✅ M1
│   │   └── artifacts/                  # per-artifact templates
│   │       ├── holding-statement.md
│   │       ├── qa-doc.md
│   │       ├── message-house.md
│   │       └── stakeholder-heat-map.md
│   └── scripts/
│       └── verify_quotes.py            # post-synthesis quote verification
└── agents/
    ├── scoping-designer.md             # Opus 4.7 — run-plan designer
    ├── ground-truth-researcher.md      # Sonnet 4.6 — factbase builder
    ├── persona-architect.md            # Opus 4.7 — cast designer + salience scorer
    ├── persona-researcher.md           # Sonnet 4.6 — per-persona bundle builder
    ├── persona-worker.md               # Sonnet 4.6 — roleplay
    ├── critic.md                       # Sonnet 4.6 — rubric grader
    └── synthesizer.md                  # Opus 4.7 — report + artifacts writer
```

Runtime files land in the user's working dir at `pre-flight-runs/<run>/`. Nothing is persisted in the skill dir. Cross-run memory (opt-in) lands at `pre-flight-memory/<industry>/` in the user's working dir.

---

## Architecture

```
Phase 0: Scoping (AskUserQuestion)
         │
         ▼
Phase 1: scoping-designer + ground-truth-researcher (parallel)
         │                 │
         ▼                 ▼
   run-plan.yaml      factbase.md
         └────────┬────────┘
                  ▼
Phase 2: persona-architect
                  │
                  ▼
            cast-spec.md
                  │
                  ▼
Phase 3: USER APPROVAL GATE
                  │
                  ▼
Phase 4: persona-researcher × N (parallel) → personas/<id>.md × N
                  │
                  ▼
Phase 5: persona-worker × N (parallel) → findings/persona-<id>.md
                  │
                  ▼
Phase 6: critic × N (parallel) → REVISE loop (max 2) → findings/persona-<id>-final.md
                  │
                  ▼
Phase 7: optional phases per run-plan
         (social-simulator, memory-keeper, debate-moderator, counterfactual-comparator)
                  │
                  ▼
Phase 8: synthesizer → report.md + artifacts/
                  │
                  ▼
Phase 9: verify_quotes.py
                  │
                  ▼
Phase 10: present to user
```

**Model strategy.** Opus 4.7 for orchestrator, scoping-designer, persona-architect, synthesizer, counterfactual-comparator, debate-moderator (hard reasoning). Sonnet 4.6 for ground-truth-researcher, persona-researcher, persona-worker, critic, social-simulator (parallel scale, good-enough voice). Haiku 4.5 for memory-keeper (summarization).

**Parallelism.** Every subagent call that can go in parallel does — Phases 4, 5, 6, and 7 all spawn N agents in a single turn. A 12-persona run in `crisis-pre-flight` mode completes in ~4-6 min.

**Anti-drift.** Three defenses against the helpful-assistant attractor:
- Persona bundles carry signature_opener (prepended to reactions), forbidden_phrases (critic hard-fails on match), and rhetorical_constraints (hard style rules). Li et al. 2024 shows these are the highest-leverage drift mitigations.
- Critic rubric checks for forbidden phrases explicitly. Revise cycles capped at 2.
- Synthesizer preserves disagreement rather than collapsing to consensus.

---

## When to use

| You want to | Use this skill | Don't use this skill |
|---|---|---|
| Pre-flight a press release, statement, Q&A doc | ✅ | |
| Run a tabletop crisis simulation multi-round | ✅ | |
| Pressure-test a positioning or rebrand narrative | ✅ | |
| Rehearse mock analyst Q&A before earnings | ✅ | |
| Compare two drafts A/B against the same cast | ✅ | |
| Anticipate activist, regulator, or journalist angles | ✅ | |
| Predict quantitative sentiment scores | | ❌ Use a real survey |
| Decide whether to publish | | ❌ Use humans in the room |
| Replace real stakeholder relationships | | ❌ Nothing replaces those |

The skill is a **pressure test**, not an oracle. Reactions are plausible in direction and wording; they are not predictions. Use the report to surface blind spots before publication, not to validate what you already wanted to do.

---

## Modes (ship status)

All 12 modes shipped (v1.0.0):

- ✅ `crisis-pre-flight` — quick pre-flight messaging review
- ✅ `crisis-tabletop` — full multi-round tabletop with social dynamics + memory + debate
- ✅ `launch-pre-mortem` — product / capability launch pre-flight
- ✅ `regulatory-response` — comment letter + coalition readiness
- ✅ `deal-comms` — Day 1 / 30 / 100 M&A playbook
- ✅ `earnings-rehearsal` — mock analyst Q&A + NIRI-format prep
- ✅ `positioning-pressure-test` — rebrand / narrative / purpose diagnostic
- ✅ `counterfactual-compare` — A/B / A/B/C draft comparison
- ✅ `red-team-read` — adversarial-only vulnerability pass
- ✅ `activist-proxy` — shareholder activism / proxy-fight response
- ✅ `exec-transition` — CEO / C-suite succession comms
- ✅ `internal-first` — layoffs / RTO / restructuring cascade

See `skills/pre-flight/modes/_index.md` for the full catalog with benchmark methodologies.

---

## Sensitive content

Stimuli often contain material non-public information (MNPI). Running this skill sends content through Anthropic's infrastructure per Claude Code's standard data-use policy. For MNPI or regulated drafts, the orchestrator warns you and asks for explicit confirmation before continuing. Check with your compliance team before running on MNPI drafts.

---

## Extending

### Add a mode

1. Write `skills/pre-flight/modes/<mode>.md` following the `crisis-pre-flight.md` template — default phases, default cast, depth parameters, artifacts list.
2. Write `skills/pre-flight/templates/report-skeletons/<mode>.md` extending `_core.md` with mode-specific sections.
3. Add any mode-specific artifact templates under `templates/artifacts/`.
4. Add an evidence entry to `reference/methodology-sources.md` citing the real-world workflow the mode implements.
5. Add a row to `modes/_index.md`.

No skill-file code changes. The scoping-designer learns the new mode from its file.

### Change the persona-bundle schema

The schema is versioned at `templates/persona-bundle.schema.md`. Bumping the version requires updating: persona-researcher task prompt, critic rubric (if new fields become critical checks), reaction schema (if new fields surface in reactions). The current schema is v2 (added: persona_type, salience, priority_tier, signature_opener, forbidden_phrases, rhetorical_constraints, expert_reflections, use_constraint, freshness_ttl_days, refresh_triggers; signature-quote floor ≥3).

### Industries

Not applicable — the skill is industry-agnostic. Nothing ships industry-specific. For every run, the ground-truth-researcher builds a factbase from public sources and the persona-architect + persona-researcher pair build the cast from public record.

---

## Research and evidence

Every mode, phase, artifact, and schema decision in this skill is grounded in a named real-world workflow or published methodology. See:

- `skills/pre-flight/reference/methodology-sources.md` — full evidence trail per mode
- `skills/pre-flight/reference/phase-library.md` — I/O contracts per phase
- `skills/pre-flight/reference/failure-modes.md` — V1 + V2 failure signatures and fixes

Parent repo research (from prior build work):

- [`synthesis/SYNTHESIS.md`](../synthesis/SYNTHESIS.md) — V1 design synthesis
- [`research/pre-flight/`](../research/pre-flight/) — what Pre-Flight actually is (open source, built on CAMEL-AI OASIS)
- [`research/competitors/`](../research/competitors/) — 16-competitor map (SightsAI, Ask Rally, Evidenza, Artificial Societies, Hotwire Spark, etc.)
- [`research/pre-ai-methods/`](../research/pre-ai-methods/) — focus groups, Delphi, tabletop, red team
- [`research/academic/`](../research/academic/) — multi-agent literature (Park et al. 2024, Li et al. 2024, Concordia, AutoGen)
- [`research/claude-sdk/`](../research/claude-sdk/) — Claude Agent SDK reference

---

## Evaluating fidelity

V2 M1 is shippable when:

1. **Quote accuracy ≥ 95%** across 15 test stimuli — no invented quotes reach the report.
2. **Persona distinctiveness** — a knowledgeable reader can match shuffled reactions to personas ≥ 80% of the time.
3. **Surprise-signal rate** — ≥1 non-obvious finding per stimulus that a single-Claude run would not have surfaced.
4. **Plan approval gate works** — user can edit the run-plan and cast-spec before research fires.
5. **Runtime** — 12-persona `crisis-pre-flight` run completes in <6 minutes wall-clock.
6. **Research quality** — persona bundles hit schema floors (≥3 signature quotes named, ≥4 concerns, ≥4 forbidden_phrases, ≥3 rhetorical_constraints, ≥3 red_lines) consistently.

---

## License and credit

Skill: unlicensed (R&D).

Inspirations credited:

- [Pre-Flight / Guo Hangjiang](https://github.com/666ghj/MiroFish) — the core swarm-simulation idea
- [CAMEL-AI OASIS](https://github.com/camel-ai/oasis) — Pre-Flight's engine
- [Anthropic multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) — orchestrator-worker pattern
- [Park et al. 2024 "Generative Agent Simulations of 1,000 People"](https://arxiv.org/abs/2411.10109) — interview-grounded persona fidelity + multi-lens expert-reflection module
- [Li et al. 2024 on persona drift](https://arxiv.org/abs/2402.10962) — signature_opener / forbidden_phrases / rhetorical_constraints mitigations
- [Constitutional AI (Bai et al. 2022)](https://arxiv.org/abs/2212.08073) — critique-and-revise pattern
- [Mitchell, Agle & Wood 1997](https://www.ronaldmitchell.org/publications/mitchell%20and%20agle%201997.pdf) — stakeholder salience (Power × Legitimacy × Urgency)
- Real-world PR workflow anchors cited in `reference/methodology-sources.md`
