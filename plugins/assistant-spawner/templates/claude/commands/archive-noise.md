# /archive-noise

Quick cleanup of obvious noise emails without full processing.

## What This Does

Archives Tier 3 emails (obvious noise) without analyzing or drafting responses:
- Newsletters
- Marketing emails
- Social notifications (LinkedIn, Discord verifications)
- Deployment success notifications
- Old automated notifications

## How to Run

```
/archive-noise
```

Or ask: "Clean up my inbox", "Archive the noise", "Quick inbox cleanup"

## Safety Checks

Before archiving, this skill:
1. **Never archives VIP contacts** (see `.claude/skills/simon-voice/contacts.md`)
2. **Never archives payment failures** (Stripe, billing)
3. **Never archives security alerts**
4. **Never archives government emails** (.no official domains)
5. **Shows what will be archived** before doing it

## Output Format

```markdown
## Archive Candidates

**Ready to archive (Tier 3 - 100% confidence):**
- 12 newsletters (Substack, Beehiiv)
- 8 LinkedIn notifications
- 5 Vercel success deploys
- 3 Discord verifications

**Total: 28 emails**

Should I archive these? (y/n)
```

## Implementation

```python
from claude_mail.config import Config
from claude_mail.reader import EmailReader

# Tier 3 archive queries (safe to auto-archive)
NOISE_QUERIES = [
    'from:substack.com',
    'from:beehiiv.com',
    'from:linkedin.com -subject:"message"',
    'from:discord.com -subject:"mentioned"',
    'from:vercel.com subject:"deployed" -subject:"failed"',
    'from:github.com subject:"pushed"',
    'from:github.com subject:"merged"',
]

config = Config.from_env()
with EmailReader(config) as reader:
    reader.select_folder("INBOX")
    all_mail = reader.get_all_mail_folder()

    for query in NOISE_QUERIES:
        uids = reader.client.gmail_search(f"in:inbox {query}")
        if uids:
            reader.client.move(uids, all_mail)
```

## Notes

- Faster than /process-inbox for quick cleanups
- Use when you just want noise gone without processing
- Safe defaults - when in doubt, don't archive
