# mirofish

Claude Code plugin for stakeholder reaction simulation — pressure-test a press release, statement, or policy announcement against a cast of persona subagents before you publish.

## Structure

```
plugins/mirofish/
├── .claude-plugin/plugin.json
├── skills/
│   └── mirofish/
│       ├── SKILL.md              # orchestrator (Opus 4.6, high effort)
│       ├── personas/             # 20 named stakeholder bundles + index + template
│       ├── templates/            # schema, rubric, skeleton, spawn prompt
│       ├── reference/            # ground truth, routing table, failure modes
│       └── scripts/verify_quotes.py
└── agents/
    ├── persona-worker.md         # Sonnet 4.6 roleplay agent (parallel)
    ├── critic.md                 # Sonnet 4.6 quality-gate
    └── synthesizer.md            # Opus 4.6 report writer
```

## Architecture

Orchestrator-worker pattern (Anthropic's empirically strongest multi-agent shape — 90% uplift). Opus lead + Sonnet workers + Opus synthesis.

```
Orchestrator → plan.md → user approval → parallel persona-worker × N
     → parallel critic × N → (REVISE once) → synthesizer → report.md → verify_quotes.py
```

## Key design principles

- **Rich persona bundles, not demographic strings.** Each persona is a markdown file with signature quotes verbatim from public sources, concrete red_lines, rhetorical-style notes, and a reaction_pattern. Grounded in Park et al. 2024's finding that interview-grounded personas hit 85% of human test-retest reliability.
- **Mandatory critic loop.** Every persona reaction passes a rubric check (in-character, grounded, non-sycophantic, within red_lines, schema-compliant) before synthesis. Constitutional-AI pattern against the dominant failure mode (sycophantic collapse to helpful-assistant voice).
- **Parallel spawn.** All persona-workers in one assistant turn → concurrent execution. 12-persona run completes in ~2 minutes.
- **Quote verification.** Post-synthesis script checks every quoted line in the report appears verbatim in a findings file. Catches invented quotes.
- **User approves the cast.** The skill pauses after classifying the release and selecting personas. Non-negotiable step.

## Invoke

```
/mirofish path/to/press-release.md
```

Or naturally:

> Simulate how ASOC, Greenpeace, DN, and NBIM would react to this Q4 earnings release.

## Swap the persona library

The shipped library is Aker BioMarine (krill / Antarctic fishing, verified 2026-04-16). To retarget an industry, replace `skills/mirofish/personas/` + `skills/mirofish/reference/aker-ground-truth.md` + `skills/mirofish/reference/routing-table.md`. Orchestrator, workers, critic, synthesizer, schema, and verify script are generic.

## When not to use

- Quantitative sentiment prediction — use a real poll.
- Replacing stakeholder relationships — nothing does.
- Deciding whether to publish — use humans.

This is a pressure test, not an oracle.

## References

- [Mirofish / Guo Hangjiang](https://github.com/666ghj/MiroFish)
- [CAMEL-AI OASIS](https://github.com/camel-ai/oasis)
- [Anthropic multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system)
- [Park et al. 2024](https://arxiv.org/abs/2411.10109)
- [Constitutional AI](https://arxiv.org/abs/2212.08073)
