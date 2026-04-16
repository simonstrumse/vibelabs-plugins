# Mirofish-style stakeholder simulation — Claude Code skill

A Claude Code plugin that pressure-tests a press release by spawning a cast of stakeholder persona subagents in parallel, critic-passing each reaction, and synthesizing a structured report.

Inspired by [Mirofish](https://github.com/666ghj/MiroFish) (open-source swarm simulation on top of [CAMEL-AI OASIS](https://github.com/camel-ai/oasis)) and [Anthropic's multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) (orchestrator-worker pattern, 90.2% uplift over single-agent Opus).

Ships with a 20-persona library covering the Aker BioMarine / Antarctic krill stakeholder landscape, verified 2026-04-16 and grounded in public-record quotes.

---

## What it does

You paste a press release draft. The skill:

1. **Classifies** it (product launch, CCAMLR response, financial, bycatch incident, sustainability report, M&A, general) and proposes a persona cast from the routing table.
2. **Pauses** for your approval — you can drop personas, add personas, resize the cast.
3. **Spawns** every persona in parallel as a Sonnet 4.6 subagent. Each persona reads only its bundle + the stimulus + the Aker ground-truth file — never other personas' reactions.
4. **Critic-passes** each reaction against a rubric (in-character, grounded, non-sycophantic, within red_lines, schema-compliant). REVISE personas run once more.
5. **Synthesizes** a report: TL;DR, reaction distribution, consensus signals, disagreement axes, surprise signals, red-line warnings, ≤5 proposed revisions, coverage gaps.
6. **Verifies** every quoted line in the report appears verbatim in a findings file. Flags inventions.

Total wall-clock for a 12-persona run: ~2 minutes.

---

## Install

### As a local plugin (recommended during development)

```bash
claude plugin marketplace add /Users/emmafjelldahl/kodeprosjekter/Mirofish/skill
claude plugin install mirofish@mirofish
```

Or start Claude Code with the plugin directly loaded:

```bash
claude --plugin-dir /Users/emmafjelldahl/kodeprosjekter/Mirofish/skill
```

### Invoke

Inside Claude Code:

```
/mirofish path/to/press-release.md
```

Or, since the skill has descriptive triggers, just ask naturally:

```
Simulate how ASOC, Greenpeace, DN, and NBIM would react to this Q4 earnings release — ./releases/q4-2025.md
```

---

## Folder layout

```
skill/
├── .claude-plugin/plugin.json       # plugin manifest
├── skills/mirofish/
│   ├── SKILL.md                     # orchestrator (Opus 4.6)
│   ├── personas/                    # 20 named Aker stakeholder bundles
│   │   ├── _index.md                # human-readable index
│   │   ├── _template.md             # template for adding new personas
│   │   ├── christian-asoc.md
│   │   ├── bengtsson-greenpeace.md
│   │   └── ...                      # (20 total)
│   ├── templates/
│   │   ├── persona-task.md          # verbatim spawn prompt
│   │   ├── reaction-schema.md       # worker output contract
│   │   ├── critic-rubric.md         # quality-gate rubric
│   │   └── report-skeleton.md       # synthesizer output contract
│   ├── reference/
│   │   ├── aker-ground-truth.md     # loaded into every persona spawn
│   │   ├── routing-table.md         # cast-selection defaults
│   │   └── failure-modes.md         # debugging guide
│   └── scripts/
│       └── verify_quotes.py         # post-synthesis quote-verification
└── agents/
    ├── persona-worker.md            # Sonnet 4.6 roleplay agent
    ├── critic.md                    # Sonnet 4.6 rubric grader
    └── synthesizer.md               # Opus 4.6 report writer
```

---

## Architecture

```
Orchestrator (Opus)
       │
       ▼
   plan.md  ── user approval ──┐
       │                       │
       ▼                       │
   Parallel Agent(persona-worker) × N  ← all spawned in a single assistant turn
       │
       ▼
   findings/persona-<id>.md (N files)
       │
       ▼
   Parallel Agent(critic) × N
       │
       ▼ (REVISE branch → persona-worker once more)
   findings/persona-<id>-final.md
       │
       ▼
   Agent(synthesizer)  ── produces report.md
       │
       ▼
   scripts/verify_quotes.py  ── flags unverified quotes
       │
       ▼
   report.md → user
```

**Model strategy.** Orchestrator and synthesizer on Opus 4.6 (high reasoning, hard problems). Personas and critics on Sonnet 4.6 (parallel scale, good-enough voice). Follows Anthropic's published pattern.

**Parallelism.** All persona-worker calls go out in one assistant turn so they run concurrently. A 12-persona run uses 12 parallel Sonnet workers + 12 parallel critics + 1 Opus synthesizer. Cache is shared across workers (same stimulus, same ground truth).

**Anti-sycophancy.** The failure mode that sinks naive "roleplay as X" simulations. Three defences: (1) rich persona bundles with signature quotes — not demographic strings, (2) mandatory critic pass with a non-sycophancy criterion, (3) synthesizer preserves disagreement rather than forcing consensus.

---

## When to use

| You want to | Use this skill | Don't use this skill |
|---|---|---|
| Pre-flight a press release draft | ✅ | |
| Anticipate NGO or journalist angles | ✅ | |
| Pressure-test a sustainability claim | ✅ | |
| Plan a crisis response before going public | ✅ | |
| Predict quantitative sentiment scores | | ❌ Use a real poll |
| Decide whether to publish | | ❌ Use humans |
| Replace real stakeholder relationships | | ❌ Nothing replaces those |

The skill is a **pressure test**, not an oracle. The reactions are plausible in direction and wording; they are not predictions. Use the report to surface blind spots before release, not to validate what you already wanted to do.

---

## Sensitive content

Press release drafts often contain material non-public information. Running this skill sends draft content through Anthropic's infrastructure per Claude Code's standard data-use policy. For MNPI or regulated drafts, check with your compliance team before running.

---

## Extending

### Add a persona

1. Copy `skills/mirofish/personas/_template.md` to `personas/<new-id>.md`.
2. Fill all sections. Signature quotes must be verbatim from public sources. Red lines must be concrete triggers, not abstractions.
3. Add a row to `personas/_index.md`.
4. If the persona belongs in a default cast, edit `reference/routing-table.md`.
5. Set `last_verified` in the frontmatter to today.

### Swap the industry

The skill is Aker-ready but industry-agnostic. To run it for another industry (pharma, aerospace, banking):

1. Replace everything under `personas/` with a new library.
2. Replace `reference/aker-ground-truth.md` with the new industry's facts.
3. Rewrite `reference/routing-table.md` with industry-relevant release types and casts.

Everything else (orchestrator, workers, critic, synthesizer, schema, report skeleton, verify script) is generic.

---

## Research and background

This skill is the output of a structured research pass. See the parent repo:

- [`synthesis/SYNTHESIS.md`](../synthesis/SYNTHESIS.md) — design synthesis
- [`research/mirofish/`](../research/mirofish/) — what Mirofish actually is (it's open source, built on CAMEL-AI OASIS, not a SaaS)
- [`research/competitors/`](../research/competitors/) — 16-competitor map (SightsAI, Ask Rally, Evidenza, and others)
- [`research/pre-ai-methods/`](../research/pre-ai-methods/) — focus groups, Delphi, tabletop exercises, red team
- [`research/academic/`](../research/academic/) — multi-agent literature (Park et al. 2023/2024, Concordia, AutoGen, LangGraph)
- [`research/claude-sdk/`](../research/claude-sdk/) — Claude Agent SDK reference and skill blueprint
- [`research/use-case/aker-biomarine.md`](../research/use-case/aker-biomarine.md) — Aker corporate + controversy context
- [`research/use-case/stakeholder-personas.md`](../research/use-case/stakeholder-personas.md) — the research-grounded persona bundles that populated `personas/`
- [`research/use-case/real-releases/`](../research/use-case/real-releases/) — five real Aker press releases (2022–2026) available as test stimuli

## Evaluating fidelity

A v1 is shippable when:

1. **Quote accuracy** ≥ 95% across 15 test stimuli (no invented quotes).
2. **Persona distinctiveness** — a knowledgeable reader can match shuffled reactions to personas ≥ 80% of the time.
3. **Surprise-signal rate** — ≥1 non-obvious finding per stimulus that a single-Claude run wouldn't have surfaced.
4. **Plan-approval step** works — user can edit the cast before spawn.
5. **Runtime** — 12-persona run completes in <3 min.

Test fixtures are in `research/use-case/real-releases/`. Run them manually.

---

## License and credit

Skill itself: unlicensed (internal R&D).

Inspirations credited:

- [Mirofish / Guo Hangjiang](https://github.com/666ghj/MiroFish) — the core swarm-simulation idea
- [CAMEL-AI OASIS](https://github.com/camel-ai/oasis) — Mirofish's engine
- [Anthropic multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) — orchestrator-worker pattern
- [Park et al. 2024 "Generative Agent Simulations of 1,000 People"](https://arxiv.org/abs/2411.10109) — persona-fidelity approach
- [Constitutional AI (Bai et al.)](https://arxiv.org/abs/2212.08073) — critique-and-revise pattern
