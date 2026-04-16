# stakeholder-sim — Claude Code skill

Pressure-test a press release, statement, or campaign brief by spawning a cast of stakeholder persona subagents in parallel, running a critic quality-gate, and synthesizing a structured report. Works for any sender in any industry — the skill researches the sender and builds the persona cast per run via WebFetch/WebSearch, or loads a preset library if one applies.

---

## What it does

You point the skill at a press release draft. The skill:

1. **Analyzes the stimulus** (agent) — extracts sender, topic, release type, key claims, named stakeholders.
2. **Asks the user** whether to use a preset, research the sender from scratch, or accept user-provided facts.
3. **Builds client ground truth** (agent + WebFetch/WebSearch) — corporate structure, controversies, leadership, standard framings.
4. **Maps the stakeholder landscape** (agent) — proposes 12-20 named stakeholder roles across activists, scientists, regulators, press, customers, investors, internal.
5. **Pauses for your approval** — you see the plan, edit the cast, say go.
6. **Builds each persona** (agent + WebFetch/WebSearch, in parallel) — verbatim signature quotes, concrete red_lines, reaction patterns.
7. **Spawns persona workers** (all in parallel) — each inhabits its persona and writes a reaction.
8. **Critic-passes each reaction** (in parallel) — rubric check for in-character, grounded, non-sycophantic, within red_lines. Revises once if needed.
9. **Synthesizes a report** — TL;DR, reaction distribution, consensus signals, disagreement axes, surprise signals, red-line warnings, proposed revisions, coverage gaps.
10. **Verifies every quote** (agent) — confirms quoted lines appear verbatim in findings. Corrects hallucinations before you see the report.

A 12-persona run takes ~2-4 minutes wall-clock. A 20-persona run with full research takes ~6-8 minutes.

---

## Install

With the vibelabs marketplace already installed:

```bash
claude plugin install stakeholder-sim
```

Or fresh:

```bash
claude plugin marketplace add simonstrumse/vibelabs-plugins
claude plugin install stakeholder-sim
```

---

## Invoke

```
/stakeholder-sim path/to/press-release.md
```

With a preset:

```
/stakeholder-sim path/to/release.md --preset aker-biomarine
```

Or naturally, since the skill has descriptive triggers:

> Simulate how journalists, activists, and investors would react to this Nordea Q4 earnings release.

> Pre-flight this CCAMLR statement — use the Aker preset.

> Red team this campaign brief. Cast size 8, no sell-side analysts.

---

## Folder layout

```
plugins/stakeholder-sim/
├── .claude-plugin/plugin.json
├── CLAUDE.md                           # plugin overview
├── README.md                           # this file
├── skills/stakeholder-sim/
│   ├── SKILL.md                        # orchestrator
│   ├── templates/
│   │   ├── persona-task.md             # verbatim spawn prompt
│   │   ├── reaction-schema.md          # worker output contract
│   │   ├── critic-rubric.md            # quality-gate rubric
│   │   └── report-skeleton.md          # synthesizer output contract
│   ├── reference/
│   │   ├── routing-heuristics.md       # generic release-type cast guidance
│   │   └── failure-modes.md            # debugging guide
│   └── presets/
│       └── aker-biomarine/             # sample preset (20 verified personas + Aker ground truth)
└── agents/
    ├── stimulus-analyzer.md            # research phase
    ├── client-researcher.md            #   "
    ├── stakeholder-mapper.md           #   "
    ├── persona-builder.md              #   "
    ├── persona-worker.md               # simulation phase
    ├── critic.md                       #   "
    ├── synthesizer.md                  #   "
    └── quote-verifier.md               #   "
```

---

## Architecture

```
Orchestrator (Opus) — SKILL.md
       │
       ▼
   Phase 0: triage preset vs research
       │
       ▼
   Phase 1: stimulus-analyzer → client-researcher → stakeholder-mapper
       │
       ▼
   plan.md  ── user approval ──┐
                               │
                               ▼
   Phase 1 (research mode): persona-builder × N  (parallel)
                               │
                               ▼
   Phase 2: persona-worker × N  (parallel)
                               │
                               ▼
   Phase 3: critic × N  (parallel; revise once)
                               │
                               ▼
   Phase 4: synthesizer → report.md
                               │
                               ▼
   Phase 5: quote-verifier → verification.md
                               │
                               ▼
                          report.md → user
```

**Agentic everything.** Every extraction, classification, research, and verification step is a Claude subagent with native tools (WebFetch, WebSearch, Read, Write). There are no regex parsers, hardcoded scrapers, or deterministic scripts. The orchestrator itself is a Claude agent following `SKILL.md`.

**Model strategy.** Orchestrator and synthesizer on Opus 4.6 (coordination and hard reasoning). Research agents, persona workers, critics, and verifier on Sonnet 4.6 (extraction, classification, parallel scale).

**Parallelism.** Persona-builders, persona-workers, and critics all spawn concurrently in a single assistant turn. A 12-persona run uses 12 Sonnet builders + 12 Sonnet workers + 12 Sonnet critics + 1 Opus synthesizer + 1 Sonnet verifier.

**Anti-sycophancy.** (1) Persona bundles with verbatim signature quotes and concrete red_lines, built from public sources by the persona-builder. (2) Mandatory critic pass with an explicit non-sycophancy criterion. (3) Synthesizer preserves disagreement rather than forcing consensus.

**Anti-hallucination.** Quote-verifier reads the final report and flags any quoted line that doesn't appear verbatim (typography differences allowed) in a findings file or the stimulus. Synthesizer reruns once with corrections if needed.

---

## Presets

A preset is a verified persona library for a specific sender. Ship-quality personas — signature quotes sourced with URLs, red_lines concrete, `last_verified` dated. When a preset matches, Phase 0 research is skipped and the cast + ground truth come from the preset directory.

**Shipped preset:** `aker-biomarine` — 20 personas for Aker BioMarine / Aker QRILL Company releases. See `skills/stakeholder-sim/presets/aker-biomarine/README.md`.

**Add your own:** copy the preset directory, swap the 20 personas (use `personas/_template.md`), rewrite `ground-truth.md` and `routing-table.md`. No code changes.

**When no preset applies:** the skill researches on the fly. Equally valid path — presets are optimizations, not requirements.

---

## User-facts mode (for sensitive releases)

If the press release contains material non-public information (MNPI) or your ground truth is in internal documents not meant for web exposure, you can paste factual info about the client directly. The client-researcher agent accepts three modes:

- `user-only` — trust the user file exactly, do no web research
- `augment` — user file is priority, augment gaps with research
- `open-research` — no user file, research from scratch

The skill asks which mode you want during Phase 1a.

---

## When to use

| Use it for | Don't use it for |
|---|---|
| Pre-flighting a press release draft | Quantitative sentiment prediction — use a real poll |
| Anticipating NGO or journalist angles | Replacing stakeholder relationships — nothing does |
| Pressure-testing a sustainability claim | Deciding whether to publish — use humans |
| Pre-wiring a crisis response | Legal advice or regulatory strategy |

This is a pressure test, not an oracle. Use the report to surface blind spots before release.

---

## Sensitive content

Press release drafts often contain material non-public information. Running the skill sends draft content through Anthropic's infrastructure per Claude Code's standard data-use policy. For MNPI or regulated drafts:

- Use `user-only` research mode to keep client facts out of WebFetch calls.
- Do not paste the full stimulus content as part of WebSearch queries.
- Check with your compliance team before running any new category of draft.

---

## Credit

Architectural inspirations:

- [Anthropic's multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) — orchestrator-worker pattern with ~90% uplift over single-agent baseline
- [Park et al. 2024, "Generative Agent Simulations of 1,000 People"](https://arxiv.org/abs/2411.10109) — interview-grounded persona fidelity
- [Constitutional AI (Bai et al. 2022)](https://arxiv.org/abs/2212.08073) — critique-and-revise pattern
- [Mirofish](https://github.com/666ghj/MiroFish) and [CAMEL-AI OASIS](https://github.com/camel-ai/oasis) — open-source swarm-simulation work that informed the persona-stacking pattern
