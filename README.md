# Vibe Labs — Claude Code Plugins

A collection of Claude Code plugins by [Vibe Labs](https://vibelabs.no).

## Install

```bash
claude plugin marketplace add simonstrumse/vibelabs-plugins
```

## Plugins

### assistant-spawner

Spawn a new AI executive assistant with a single command. Gets you a Telegram bot, email heartbeat, memory system, and a full identity — all configured through a guided conversation.

```bash
claude plugin install assistant-spawner

# Then in a new empty directory:
mkdir ~/my-assistant && cd ~/my-assistant
claude
# → /spawn-assistant
```

**What you get:**
- Telegram bot with owner-only access control
- Heartbeat system for email triage
- File-based memory (STATE, MEMORY, HISTORY, ACTIVE_THREADS)
- CLAUDE.md and SOUL.md generated for your assistant's unique identity
- launchd/systemd service files for always-on operation
- Universal skills: changelog, task system, learning integration

### instaskill

Turn your Instagram saved posts into a searchable, analyzable archive.

```bash
claude plugin install instaskill
```

4 skills: pipeline sync, analysis, deep dives, and video extraction.

### stakeholder-sim

Pressure-test a press release, statement, or campaign brief against a cast of stakeholder persona subagents (press, activists, scientists, regulators, customers, investors) before you publish. Works for any sender in any industry — the skill researches the sender, maps stakeholders, and builds the persona cast per run, or loads a preset library if one applies. Fully agentic pipeline — every extraction, classification, research, and verification step runs on Claude subagents with native tools.

```bash
claude plugin install stakeholder-sim

# Inside Claude Code:
# → /stakeholder-sim path/to/press-release.md
# or just ask naturally: "simulate how journalists and activists would react to this release"
```

**What you get:**
- Orchestrator skill that analyzes the stimulus, researches the sender (or accepts your facts), maps stakeholders, proposes a cast, and pauses for your approval
- 8 specialized subagents: stimulus-analyzer, client-researcher, stakeholder-mapper, persona-builder, persona-worker, critic, synthesizer, quote-verifier
- Optional presets — ships with a 20-persona Aker BioMarine sample library grounded in verbatim public-record quotes
- Structured report: consensus signals, disagreement axes, surprise signals, red-line warnings, proposed revisions, coverage gaps
- Quote verification — every quoted line in the final report is checked verbatim against the findings before you see it

Credits: [Anthropic multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system), [Park et al. 2024](https://arxiv.org/abs/2411.10109), [Mirofish / CAMEL-AI OASIS](https://github.com/666ghj/MiroFish).

## Requirements

- [Claude Code](https://claude.ai/code) CLI installed
- Python 3.10–3.13
- A Telegram account (for the assistant bot — only required for `assistant-spawner`)
