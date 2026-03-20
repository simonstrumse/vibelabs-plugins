# /email-status

Quick check of current inbox state without processing.

## What This Does

Provides a snapshot of Simon's inbox:
- Total emails in INBOX
- Unread count
- Top senders
- Oldest unanswered emails
- Pending payment issues

## How to Run

```
/email-status
```

Or ask: "How's my inbox?", "Email status", "What's in my inbox?"

## Output Format

```markdown
## Inbox Status

**Current state:** X emails in inbox (Y unread)

### Top Senders (last 7 days)
1. christina@startuplab.no - 5 emails
2. cwb@norscanas.no - 3 emails
...

### Oldest Unanswered (from VIPs)
- 3 days: Christina - RE: Startup event
- 2 days: Fredrik - Project update

### Urgent Items
- Stripe payment failure: Easypick AS (3 failures)
- Domain expiring: vibelabs.no (7 days)

### Quick Archive Candidates
- 12 newsletters
- 8 GitHub notifications
- 5 Vercel deployments
```

## Implementation

```python
from claude_mail.config import Config
from claude_mail.reader import EmailReader
from collections import defaultdict

config = Config.from_env()
with EmailReader(config) as reader:
    reader.select_folder("INBOX")

    # Get counts
    status = reader.get_folder_status("INBOX")
    total = status[b'MESSAGES']
    unseen = status[b'UNSEEN']

    # Get recent for analysis
    messages = reader.gmail_search_messages("in:inbox newer_than:7d", include_body=False)

    # Analyze senders
    sender_counts = defaultdict(int)
    for msg in messages:
        sender_counts[msg.from_address] += 1
```

## Notes

- This is read-only, no archiving
- Use when you want a quick overview before deciding to run full /process-inbox
- Good for morning inbox check
