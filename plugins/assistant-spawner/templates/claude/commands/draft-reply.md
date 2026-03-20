# /draft-reply

Draft a reply to a specific email in Simon's voice with validation and approval flow.

## Usage

```
/draft-reply $ARGUMENTS
```

Or: "Draft a reply to Christina's email", "Help me respond to the Startuplab email"

## Arguments

- `[uid]` or `[search query]` — Target email (e.g., `501234` or `from:christina@startuplab.no`)
- `--short` — Force ultra-brief style
- `--formal` — Force formal style
- `--english` / `--norwegian` — Force language

## Details

Full workflow, voice calibration, confidence scoring, and templates: `.claude/skills/draft-reply/SKILL.md`
