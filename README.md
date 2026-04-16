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

### mirofish

Pressure-test a press release against a cast of stakeholder persona subagents (press, activists, scientists, regulators, customers, investors) before you publish. Orchestrator-worker pattern: Opus lead + parallel Sonnet personas + critic loop + Opus synthesis. Ships with a 20-persona Aker BioMarine library grounded in verbatim public-record quotes — swap the folder to retarget any industry.

```bash
claude plugin install mirofish

# Inside Claude Code:
# → /mirofish path/to/press-release.md
# or just ask naturally: "simulate how ASOC and DN would react to this release"
```

**What you get:**
- Orchestrator skill that classifies the release, proposes a persona cast, and pauses for your approval
- 3 subagents: persona-worker (roleplay), critic (rubric quality gate), synthesizer (report writer)
- 20 named stakeholder personas with signature quotes, red lines, and reaction patterns
- Structured report: consensus signals, disagreement axes, surprise signals, red-line warnings, proposed revisions, coverage gaps
- Quote-verification script — every quote in the report is checked verbatim against persona outputs

Inspired by [Mirofish](https://github.com/666ghj/MiroFish) and [Anthropic's multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system).

## Requirements

- [Claude Code](https://claude.ai/code) CLI installed
- Python 3.10–3.13
- A Telegram account (for the assistant bot — only required for `assistant-spawner`)
