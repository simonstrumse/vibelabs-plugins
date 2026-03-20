# /clean-inbox

Safe inbox cleaning with preview and approval. Archives only obvious noise.

## What This Does

1. **Fetches inbox emails** via IMAP
2. **Identifies noise** using patterns in `.claude/skills/clean-inbox/patterns.md`
3. **Shows preview** of what will be archived — waits for explicit approval
4. **Archives approved emails** and logs everything
5. **Reports results** with counts and what was archived

## How to Run

```
/clean-inbox
```

Or ask: "Clean my inbox", "Rydd innboks", "Archive noise", "Sjekk mail"

## Safety Rules

- **UNCERTAIN = KEEP** — only archive 100% certain noise
- Never archives VIP contacts (see `.claude/skills/simon-voice/contacts.md`)
- Never archives payment failures, security alerts, or government emails
- Always shows preview before archiving — requires explicit "yes"/"kjør" to proceed
- Everything archived is logged for review

## Difference from /archive-noise

`/clean-inbox` is the full skill with the 8-step safe process, logging, and detailed classification. `/archive-noise` is a quicker, less thorough cleanup.

## Details

See `.claude/skills/clean-inbox/SKILL.md` for the full process and `.claude/skills/clean-inbox/patterns.md` for noise patterns.
