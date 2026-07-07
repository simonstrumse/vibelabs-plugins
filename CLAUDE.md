# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin marketplace** (`vibelabs-plugins`). The root `.claude-plugin/marketplace.json` is the catalog; each plugin lives in `plugins/<name>/` and is self-contained — no shared code, no monorepo tooling, no build system, no test suite. Plugins are markdown-driven skill/agent packages, occasionally paired with a standalone Python script for deterministic work.

## Structure every plugin follows

```
plugins/<name>/
├── .claude-plugin/plugin.json   # required: name, displayName, description, version, author, keywords
├── skills/<skill-name>/SKILL.md # one or more skills, each with YAML frontmatter
├── agents/*.md                  # optional subagents, whitelisted from a skill's allowed-tools via Agent(name1, name2)
├── commands/                    # optional slash commands
├── templates/, reference/, presets/  # optional material the skill reads and adapts at runtime, not copy-paste boilerplate
└── README.md / CLAUDE.md        # optional plugin-specific docs — read before editing that plugin
```

## Adding or changing a plugin

1. Edit files under `plugins/<name>/`.
2. `plugin.json`'s `version` must be mirrored in the matching entry (`name`, `description`, `version`) in the root `.claude-plugin/marketplace.json` — nothing enforces this automatically and the two drift easily.
3. The root `README.md` has a per-plugin section (install command, feature list) — update it when a plugin's install flow or feature set changes.
4. There is no linter or CI. Sanity-check by hand: `marketplace.json` and every `plugin.json` must be valid JSON, and every `SKILL.md` needs frontmatter with at least `name` and `description`.

## Testing a plugin locally

No dev server exists. To exercise a plugin end-to-end, register this checkout as a local marketplace and install from it:

```bash
claude plugin marketplace add /Users/vibelabs/code/vibelabs-plugins
claude plugin install <name>
```

Then invoke its skill or slash command from a scratch directory.

## SKILL.md frontmatter conventions

Look at a couple of existing skills before writing a new one — fields in use, not all required on every skill:

- `name`, `description` — always required. `description` is the trigger Claude matches user intent against for auto-invocation, so write it as trigger phrases ("Use when...", "Triggers on..."), not a feature summary.
- `allowed-tools` — scopes what the skill can call, including `Agent(agent-a, agent-b)` to whitelist specific subagents by filename stem.
- `model` / `effort` — pins a model (e.g. `claude-opus-4-8`) and reasoning effort for orchestrator skills that need a specific tier.
- `argument-hint` — shown when the skill is invoked as `/skill-name <hint>`.
- `disable-model-invocation: true` — skill only runs on explicit slash-invocation, never auto-triggered from a description match.

## The "agentic over deterministic" convention

Several plugins (`stakeholder-sim`, `pre-flight`, `claude-for-marketing`, `instaskill`) deliberately avoid deterministic scripts for anything requiring judgment — extraction, classification, persona simulation, report writing — in favor of spawning Claude subagents with native tools. Deterministic Python is reserved for plumbing: syncing/downloading data (`instaskill`'s `instagram-pipeline`), byte-identical token conversion (`figma-tokens-to-wp/convert.py`), or verification passes that check subagent output against ground truth (`pre-flight`'s `verify_quotes.py`). When extending these plugins, keep judgment calls in subagent prompts, not in scripts.

## Multi-agent orchestrator pattern (stakeholder-sim, pre-flight)

Both plugins follow the same shape: an orchestrator `SKILL.md` (Opus, high effort) that

1. Runs a research phase — Sonnet subagents build a factbase and propose a persona cast
2. Pauses for mandatory user approval of the plan/cast (non-optional, hard-coded in the orchestrator)
3. Fans out `persona-worker` subagents in parallel
4. Runs a `critic` pass per persona (rubric-gated revise loop, defends against sycophantic collapse to helpful-assistant voice)
5. Synthesizes (Opus) into a report
6. Verifies every quote against the findings files before showing the user

File-passing contract: `analysis.md` → `ground-truth.md` → `cast-roster.md` → `plan.md` → `findings/persona-*.md` → `report.md`. Read `plugins/stakeholder-sim/CLAUDE.md` and `plugins/pre-flight/README.md` for the full per-plugin agent list and mode/preset routing.

## Plugin-specific docs to read before touching that plugin

- `plugins/instaskill/CLAUDE.md` — skill chain (pipeline → analysis → deep-dive/video), trust hierarchy for video (Claude = ground truth, Gemini = additive only, merge = deterministic script)
- `plugins/stakeholder-sim/CLAUDE.md` — full architecture diagram, preset system, how to add a new preset
- `plugins/cmux/README.md` — `ccx` wrapper, `CCX_CMD` env var for swapping the driven agent, session memory management via `cmux-sessions`
- `plugins/figma-tokens-to-wp/skills/figma-tokens-to-wp/SKILL.md` — deterministic converter, calibrated byte-for-byte against Dekode Forge for 4 of 5 output artefacts
