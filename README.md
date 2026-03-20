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

## Requirements

- [Claude Code](https://claude.ai/code) CLI installed
- Python 3.10–3.13
- A Telegram account (for the assistant bot)
