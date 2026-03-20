# /draft-reply

Draft a reply to a specific email in [OWNER_NAME]'s voice with validation and approval flow.

## Usage

```
/draft-reply $ARGUMENTS
```

Or: "Draft a reply to that email", "Help me respond to the meeting request"

## Arguments

- `[uid]` or `[search query]` — Target email (e.g., `501234` or `from:contact@example.com`)
- `--short` — Force ultra-brief style
- `--formal` — Force formal style
- `--english` / `--norwegian` — Force language

## Details

Full workflow, voice calibration, confidence scoring, and templates: `.claude/skills/draft-reply/SKILL.md`
