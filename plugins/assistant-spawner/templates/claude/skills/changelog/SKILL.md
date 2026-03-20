---
name: changelog-tracking
description: Manages CHANGELOG.md with a two-part structure (current state snapshot + append-only history). Handles session handover, context recovery, and documenting architectural decisions.
---

# Changelog Tracking Skill

> Invoked when: updating CHANGELOG.md, session handover, documenting changes

## Changelog Structure

CHANGELOG.md has TWO parts:
1. **Current State (TOP)** — snapshot, UPDATED in-place
2. **History (BELOW)** — append-only entries

## Turn-Start Protocol

Before responding to a new request, check if the last turn produced something changelog-worthy. If yes, add entry NOW.

## Fresh Start Protocol

Read "Current State" at top of CHANGELOG.md for instant context recovery. Don't redo completed work.

## Entry Format

```markdown
## [DATE] - [SESSION SUMMARY]

### Direction & Vision
- [Strategic shifts from conversation]

### Changes
- [DESCRIPTION] — [FILES] ([CONTEXT])

### Insights
- [Any educational learnings]

### Technical Notes
- [Gotchas, decisions]

### Pending
- [ ] [Incomplete work]
```

Omit sections that don't apply.

## When to Add Entries

DO: New capabilities, architectural decisions, Gmail/IMAP gotchas, incomplete work, direction shifts, insight blocks.
DON'T WAIT: Until session end, user asks, or context runs low.

## Anti-Patterns

1. Batching at end
2. Vague descriptions ("Fixed bug")
3. Missing WHY
4. No pending items
5. Skipping technical notes
6. Ignoring direction shifts

## CHANGELOG.md Template

```markdown
# Changelog

## Current State
> **Last Updated:** [DATE]
> **Capabilities:** [SUMMARY]

### What's Working
- [x] ...

### What's Next
| Priority | Task | Status |
|----------|------|--------|

---

## History

## [DATE] - [Title]
### Changes
- ...
```

## Updating Current State

Update in-place when: new capability working, new dev phase, significant state change. Always also add history entry.

## Email System Notes

Always note: access method (IMAP vs Maildir), Gmail quirks, Python version, credential handling.
