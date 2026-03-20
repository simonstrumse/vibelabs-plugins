---
name: spawn-assistant
description: >
  Bootstrap a new AI executive assistant with Telegram bot, heartbeat, memory, and identity.
  Guided setup: /spawn-assistant in an empty directory.
---

# Spawn Assistant

You are setting up a brand new AI executive assistant from scratch. Follow the phases below IN ORDER. Each phase checks if work is already done — never overwrite without asking.

The plugin directory containing templates and references is available at the plugin's install path. Find it by searching for this skill's SKILL.md file — the templates are in `../../templates/` relative to this file.

---

## Phase 0: Prerequisites

Run these checks BEFORE anything else. Stop and explain if any REQUIRED check fails.

```
REQUIRED:
- [ ] Current directory is empty (or user confirms overwriting)
- [ ] Python 3.10–3.13 exists: run `python3 --version` (macOS/Linux) or `python --version` (Windows)
- [ ] Claude Code CLI exists: run `claude --version`

DETECT:
- OS: check `uname -s` (macOS/Linux) or `echo %OS%` (Windows) — needed for Phase 8
- Python command: `python3` or `python` — remember which works
- Claude CLI path: `which claude` or `where claude`
```

If Python is missing or wrong version, tell the user how to install Python 3.12. If Claude CLI is missing, tell them to run `npm install -g @anthropic-ai/claude-code`.

---

## Phase 1: Identity

Ask these questions in **2-3 rounds**, not all at once. Wait for answers before proceeding.

**Round 1:**
- "What should the assistant be called?" (full name, e.g., "Marta Hansen")
- "Who is the owner/boss?" (full name, e.g., "Erik Pedersen")
- "Describe the personality in a sentence or two" (e.g., "Professional but warm, direct, efficient")

**Round 2:**
- "What language should it default to?" (Norwegian / English / other)
- "Does the assistant have an email address?" (optional — if yes, note it for later)

**Round 3:**
- "What is the owner's Telegram user ID?" — explain: "Message @userinfobot on Telegram to get your numeric user ID"
- If they don't have a Telegram bot yet: note this as pending for Phase 5

Store all answers as variables for later phases:
- `ASSISTANT_FULL_NAME` — full name (e.g., "Marta Hansen")
- `ASSISTANT_NAME` — first name (e.g., "Marta")
- `ASSISTANT_NAME_LOWER` — lowercase first name (e.g., "marta") — derived, not asked
- `OWNER_FULL_NAME` — full name (e.g., "Erik Pedersen")
- `OWNER_NAME` — first name (e.g., "Erik")
- `OWNER_NAME_LOWER` — lowercase first name (e.g., "erik") — derived, not asked
- `PERSONALITY` — personality description
- `DEFAULT_LANGUAGE` — default language
- `ASSISTANT_EMAIL` — email address (may be empty)
- `EMAIL_ACCOUNT_KEY` — Google account key for email watcher (derived from assistant name + org, e.g., "marta-company"). Explain: "This maps to `~/.config/google-accounts/`. What key should the email watcher use?" Only ask if ASSISTANT_EMAIL was provided.
- `OWNER_TELEGRAM_ID` — numeric Telegram user ID (may be pending)

---

## Phase 2: Scaffold

Locate the template files. They are in the plugin directory at `templates/` relative to the plugin root.

**Find the plugin path:**
```bash
# The templates are installed with the plugin. Find them:
find ~/.claude/plugins -path "*/assistant-spawner/templates" -type d 2>/dev/null
```

If not found, check `~/.claude/plugins/cache/` as well.

**Create directory structure:**
```
./
├── .claude/
│   ├── agents/
│   ├── commands/
│   ├── rules/
│   ├── skills/
│   ├── plans/
│   └── emails/
├── memory/
│   ├── conversations/
│   └── summaries/
├── logs/
├── scripts/
└── docs/
```

**Copy files from templates:**

1. **Verbatim Python files** (copy without changes from `templates/python/`):
   - `runtime_support.py`, `conversation_logger.py`
   - `memory_updates.py`, `task_queue.py`
   - `requirements.txt`

2. **Claude config files** (copy from `templates/claude/`):
   - `settings.json` → `.claude/settings.json`
   - `rules/*.md` → `.claude/rules/`
   - `skills/*/SKILL.md` → `.claude/skills/*/SKILL.md`
   - `commands/*.md` → `.claude/commands/`

3. **Memory files** (copy from `templates/memory/`):
   - `MEMORY.md`, `STATE.md`, `SUMMARY.md`, `HISTORY.md`, `ACTIVE_THREADS.md` → `memory/`

4. **Create empty files:**
   - `TASKS.md` — empty task list
   - `CHANGELOG.md` — empty changelog
   - `email-learnings.md` — empty learnings log
   - `.gitignore` (generate: exclude `.env`, `venv/`, `logs/`, `memory/.*.json`, `memory/conversations/`, `memory/summaries/`, `__pycache__/`, `*.pyc`)

---

## Phase 3: Generate Identity Files

This is where AI shines — don't just fill in blanks, write genuinely personalized documents.

### CLAUDE.md

Read `reference/claude-md-guide.md` from the plugin directory for the structure.

Generate a CLAUDE.md that includes:
1. **Security rule** with OWNER_NAME, refusal message in DEFAULT_LANGUAGE
2. **Identity** with ASSISTANT_NAME, introduction line, email signature
3. **Channels & Bots** — list only enabled channels (Telegram for now)
4. **Tech Stack** — Python version, mention detected Python command
5. **Autonomy** — CAN do / MUST ASK framework (keep universal)
6. **Approval signals** — send/cancel patterns in DEFAULT_LANGUAGE
7. **Communication Style** — based on PERSONALITY and DEFAULT_LANGUAGE
8. **Memory System** — standard table (copy from guide)

If ASSISTANT_EMAIL was provided, add an email section. If not, skip it.

Write the file as `CLAUDE.md` in the project root.

### SOUL.md

Read `reference/soul-md-guide.md` from the plugin directory for inspiration.

Generate a SOUL.md that:
- Uses ASSISTANT_NAME throughout
- Has 5-6 core values adapted to the PERSONALITY description
- Has boundaries section
- Has a "vibe" paragraph that captures the personality
- Is written in DEFAULT_LANGUAGE
- Does NOT copy any existing assistant's soul — write something unique

Write as `SOUL.md` in the project root.

### AGENTS.md

Copy the contents of CLAUDE.md to AGENTS.md (steering sync).

### Email Specialist Agent (only if email is enabled)

The heartbeat system uses an email specialist agent for inbox triage. Generate `.claude/agents/email-specialist.md`:

```markdown
---
name: email-specialist
description: Handles email reading, classification, drafting, and sending for ASSISTANT_NAME.
model: sonnet
---

# Email Specialist

You are ASSISTANT_NAME's email specialist subagent. You handle all email operations for OWNER_NAME.

## Your Job
- Read and classify emails by priority (Tier 1: urgent, Tier 2: actionable, Tier 3: noise)
- Draft replies in OWNER_NAME's voice (see email-learnings.md and .claude/rules/OWNER_NAME_LOWER-voice.md)
- Archive obvious noise
- Forward important items to OWNER_NAME via Telegram

## Tools Available
- Gmail API via `~/.config/google-accounts/` (account: EMAIL_ACCOUNT_KEY)
- Email learnings: `email-learnings.md`
- Voice reference: `.claude/rules/OWNER_NAME_LOWER-voice.md` (create after first corrections)
- Contact context: `.claude/skills/OWNER_NAME_LOWER-voice/contacts.md` (create as you learn)

## Rules
- NEVER send an email without explicit approval from OWNER_NAME
- When unsure about priority, escalate to OWNER_NAME
- Keep Telegram reports brief and scannable
- Log every send to email-learnings.md

## Heartbeat Mode
When invoked for heartbeat triage, you have a narrower scope:
- ONLY check ASSISTANT_EMAIL inbox
- Handle routine items autonomously (scheduling, info requests)
- Escalate anything sensitive, financial, or ambiguous
- Respond with HEARTBEAT_SKIP if nothing needs attention
```

Replace ASSISTANT_NAME, OWNER_NAME, OWNER_NAME_LOWER, EMAIL_ACCOUNT_KEY, and ASSISTANT_EMAIL with the actual values from Phase 1.

If email is NOT enabled, skip this file. The bot has a fallback prompt that works without it.

---

## Phase 4: Configure Bot Files

Copy `telegram_bot.py`, `bot_common.py`, and `watcher.py` from `templates/python/`.

Then perform **find-and-replace** for ALL `[PLACEHOLDER]` values using the identity gathered in Phase 1:

| Placeholder | Replace with | Used in |
|---|---|---|
| `[OWNER_FULL_NAME]` | OWNER_FULL_NAME | system prompt |
| `[OWNER_NAME]` | OWNER_NAME | system prompt, logging |
| `[OWNER_NAME_LOWER]` | OWNER_NAME_LOWER | logger names, paths |
| `[ASSISTANT_FULL_NAME]` | ASSISTANT_FULL_NAME | system prompt, summary |
| `[ASSISTANT_NAME]` | ASSISTANT_NAME | system prompt, logging |
| `[ASSISTANT_NAME_LOWER]` | ASSISTANT_NAME_LOWER | logger namespace, paths |
| `[OWNER_TELEGRAM_ID]` | OWNER_TELEGRAM_ID | ALLOWED_CHAT_IDS |
| `[ASSISTANT_EMAIL]` | ASSISTANT_EMAIL | heartbeat, system prompt |
| `[EMAIL_ACCOUNT_KEY]` | EMAIL_ACCOUNT_KEY | watcher, heartbeat session |
| `[DEFAULT_LANGUAGE]` | DEFAULT_LANGUAGE | system prompt, rules |

**Apply these replacements across ALL copied template files** — Python files, Claude rules, skills, and commands.

### bot_common.py
1. Find `CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")` → replace path with the detected Claude CLI path from Phase 0

### watcher.py (only if email is enabled)
1. Verify `[EMAIL_ACCOUNT_KEY]` was replaced with the actual email account key

If OWNER_TELEGRAM_ID is still pending (user didn't have it yet), replace `[OWNER_TELEGRAM_ID]` with `0` and add a comment: `# TODO: Replace 0 with your Telegram user ID`

### If email is NOT enabled:
- In `telegram_bot.py`: comment out the `from watcher import HeartbeatWatcher` import and `watcher.run_loop()` task in `main()`
- In `telegram_bot.py`: comment out the `HEARTBEAT_TRIAGE_PROMPT` and `run_heartbeat_triage` function, and the `/heartbeat` command handler
- Remove `watcher.py` (not needed without email)
- The system prompt already won't reference email if `[ASSISTANT_EMAIL]` was left empty

### If email IS enabled — Heartbeat architecture:

The heartbeat is a proactive email monitoring system that runs inside the Telegram bot process:

```
watcher.py (HeartbeatWatcher)
  └─ Checks Gmail every 15 minutes via API (zero Claude tokens)
  └─ If new unread emails found → enqueues "heartbeat_triage" task

telegram_bot.py (run_heartbeat_triage)
  └─ Runs Claude with email specialist prompt
  └─ Claude triages inbox: handles routine, escalates important
  └─ If noteworthy → sends summary to owner on Telegram
  └─ If nothing → responds HEARTBEAT_SKIP (silent)
```

**Key files:**
- `watcher.py` — lightweight Gmail poller (no Claude tokens used)
- `telegram_bot.py` → `HEARTBEAT_TRIAGE_PROMPT` — what Claude does during triage
- `.claude/agents/email-specialist.md` — system prompt for triage Claude session
- `memory/.heartbeat-state.json` — persisted watcher state (last seen email IDs)

**Configurable values in watcher.py:**
- `CHECK_INTERVAL_SECONDS = 900` — how often to check (default: 15 min, minimum safe: 300/5min to avoid Gmail rate limits)

**Configurable values in telegram_bot.py:**
- `HEARTBEAT_MAX_AGE_HOURS = 24` — auto-reset heartbeat session after this many hours
- `HEARTBEAT_SESSION_KEY` — session key for the heartbeat's Claude conversation

**Prerequisites for heartbeat:**
1. Google account must be authenticated: `python ~/.config/google-accounts/authenticate.py --account EMAIL_ACCOUNT_KEY --verify`
2. The account must have Gmail API access enabled
3. `~/.config/google-accounts/` must be on the Python path (watcher.py adds it automatically)

---

## Phase 5: Secrets

Generate a `.env` file:

```
# Bot tokens — get these from the respective platforms
TELEGRAM_BOT_TOKEN=
```

Ask the user: **"Do you have your Telegram bot token? If not, here's how to get one:"**

If they don't have one, explain:
1. Open Telegram and search for @BotFather
2. Send `/newbot`
3. Choose a display name (e.g., "Marta Assistant")
4. Choose a username ending in `bot` (e.g., `marta_assistant_bot`)
5. Copy the token and paste it here

If they provide the token, write it to `.env`.

---

## Phase 6: Python Environment

Run these commands (adapt for OS):

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Report success or failure. If pip fails, diagnose the issue.

---

## Phase 7: Verification

Run these checks and report results:

```
FILES:
- [ ] CLAUDE.md exists and contains ASSISTANT_NAME
- [ ] SOUL.md exists and contains ASSISTANT_NAME
- [ ] AGENTS.md exists and matches CLAUDE.md
- [ ] telegram_bot.py exists and contains no [PLACEHOLDER] strings
- [ ] bot_common.py exists
- [ ] memory/MEMORY.md exists
- [ ] .env exists
- [ ] .gitignore exists

EMAIL (if enabled):
- [ ] .claude/agents/email-specialist.md exists and contains ASSISTANT_NAME
- [ ] watcher.py exists and EMAIL_ACCOUNT_KEY is set (not placeholder)

RUNTIME:
- [ ] venv has telegram package: venv/bin/python -c "import telegram; print('OK')"
- [ ] Claude CLI works: claude --version

SECRETS (if token was provided):
- [ ] Bot token works: venv/bin/python -c "
from telegram import Bot
import asyncio
bot = Bot('TOKEN_HERE')
me = asyncio.run(bot.get_me())
print(f'Bot: @{me.username} — OK')
"

HEARTBEAT (if email is enabled):
- [ ] Google account access works: venv/bin/python -c "
import sys; sys.path.insert(0, str(__import__('pathlib').Path.home() / '.config/google-accounts'))
from client import get_gmail_service
gmail = get_gmail_service('EMAIL_ACCOUNT_KEY')
result = gmail.users().messages().list(userId='me', q='is:unread in:inbox', maxResults=1).execute()
count = result.get('resultSizeEstimate', 0)
print(f'Gmail access OK — {count} unread')
"
```

Report each check as pass or fail with details on failures.

**If the heartbeat Gmail check fails**, common causes:
- Account not authenticated: run `python ~/.config/google-accounts/authenticate.py --account EMAIL_ACCOUNT_KEY --verify`
- Gmail API not enabled in the Google Cloud project
- Wrong account key — verify the key matches what's in `~/.config/google-accounts/`

---

## Phase 8: Services (OS-specific)

### macOS (launchd)

Generate a plist file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>[REVERSE_DOMAIN].[ASSISTANT_FIRST_NAME]-telegram</string>
    <key>ProgramArguments</key>
    <array>
        <string>[PROJECT_DIR]/venv/bin/python</string>
        <string>[PROJECT_DIR]/telegram_bot.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>[PROJECT_DIR]</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>[PROJECT_DIR]/logs/telegram-bot.log</string>
    <key>StandardErrorPath</key>
    <string>[PROJECT_DIR]/logs/telegram-bot-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:[PROJECT_DIR]/venv/bin</string>
    </dict>
</dict>
</plist>
```

Ask: "Should I generate a reverse-domain label? (e.g., `no.company.marta-telegram`)"

Save plist to project directory. Then ask: **"Do you want me to install and start the service now?"**

If yes:
```bash
cp [PLIST] ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/[PLIST]
```

### Linux (systemd)

Generate a unit file and print instructions:
```bash
sudo cp [UNIT] /etc/systemd/system/
sudo systemctl enable --now [SERVICE_NAME]
```

### Windows

Print instructions for Task Scheduler or suggest running manually:
```cmd
cd [PROJECT_DIR]
venv\Scripts\activate
python telegram_bot.py
```

---

## Phase 9: Summary

Print a clear summary:

```
Assistant "[ASSISTANT_NAME]" is ready!

Setup complete:
  - Project directory: [PATH]
  - Identity: CLAUDE.md, SOUL.md
  - Telegram bot: telegram_bot.py
  - Memory system: memory/
  - Python environment: venv/
  - Bot token: [configured/pending]
  - Service: [running/not installed]

Next steps:
  [If token pending] Get bot token from @BotFather and add to .env
  [If service not installed] Install the launchd/systemd service
  [If email desired] Set up email integration with google-accounts

Test your assistant:
  cd [PATH]
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  python telegram_bot.py
  Then message your bot on Telegram!
```

---

## Idempotency Rules

Before EVERY file operation:
1. Check if the file already exists
2. If it does, ask: "This file already exists. Overwrite, skip, or show diff?"
3. Never silently overwrite
4. For venv: check if `venv/bin/python` exists before creating
5. For services: check if plist/unit already loaded before installing
