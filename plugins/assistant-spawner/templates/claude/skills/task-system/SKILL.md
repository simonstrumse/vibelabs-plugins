---
name: task-system
description: Converts actionable emails into structured tasks in TASKS.md with full email archives in .claude/emails/. Handles task lifecycle from creation through completion and email archival.
---

# Task System Skill

> Invoked when: creating tasks from emails, managing TASKS.md

## Structure

```
TASKS.md                     # Main task list
.claude/emails/task-XXX-*.md # Full email content per task
```

## Task Lifecycle

Email → Classified actionable → Task created → Work done → Completed → Email archived

## Creating a Task

### 1. Email Archive File (`.claude/emails/task-XXX-description.md`)

```markdown
# Email: [Description]
## Metadata
- **Task ID**: TASK-XXX
- **Gmail Thread ID**: [id]
- **Gmail Link**: https://mail.google.com/mail/u/0/#inbox/[id]
- **From**: [sender]
- **Subject**: [subject]
- **Date**: [date]
- **Status**: PENDING
## Email Content
[Full body]
## Context
[Why it matters]
## Action Required
[What to do]
```

### 2. TASKS.md Entry

```markdown
### TASK-XXX: [Title]
**Priority**: High/Medium/Low | **Due**: [date] | **Status**: 🔴 Pending
[Description]
**Source**: [Email](.claude/emails/task-XXX-*.md) | [Gmail](link)
```

### 3. Sequential numbering: TASK-001, TASK-002, etc.

## Status Icons

🔴 Pending | 🟡 In Progress | 🟢 Scheduled | ✅ Completed

## Completing

1. Update TASKS.md → ✅
2. Move to Completed section
3. Add completion date
4. Archive source email
5. Update email file status

## Integration with Skills

`/process-inbox`: Check TASKS.md first, no duplicates, update if new emails in thread.
