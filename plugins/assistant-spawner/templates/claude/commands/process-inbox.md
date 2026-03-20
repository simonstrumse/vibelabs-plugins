# /process-inbox

Full inbox triage: fetch → classify → archive noise → draft replies → present for review.

## Usage

```
/process-inbox
/process-inbox $ARGUMENTS
```

Or: "Process my inbox", "Check my emails", "What emails need attention?"

## Arguments

- `--quick` — Only urgent + unread
- `--drafts-only` — Skip archive, just draft replies
- `--archive-only` — Just clean up noise

## Details

Full workflow, classification rules, draft generation, and approval signals: `.claude/skills/process-inbox/SKILL.md`
