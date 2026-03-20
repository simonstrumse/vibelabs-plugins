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
- `ASSISTANT_NAME`, `OWNER_NAME`, `PERSONALITY`, `DEFAULT_LANGUAGE`
- `ASSISTANT_EMAIL` (may be empty)
- `OWNER_TELEGRAM_ID` (may be pending)

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
   - `runtime_support.py`, `engine_config.py`, `conversation_logger.py`
   - `memory_updates.py`, `task_queue.py`, `relay.py`, `shared_topics.py`
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
- Does NOT copy Emma's soul — write something unique

Write as `SOUL.md` in the project root.

### AGENTS.md

Copy the contents of CLAUDE.md to AGENTS.md (steering sync).

---

## Phase 4: Configure Bot Files

Copy `telegram_bot.py`, `bot_common.py`, and `watcher.py` from `templates/python/`.

Then make these EXACT substitutions in the copied files:

### telegram_bot.py
1. Find `ALLOWED_CHAT_IDS = {462445799}` → replace `462445799` with OWNER_TELEGRAM_ID
2. Find the `EA_SYSTEM_PROMPT` multiline string (starts around line 335) → rewrite it to match the new assistant's identity, name, and email accounts
3. Find `HEARTBEAT_TRIAGE_PROMPT` → rewrite for new assistant, or comment out if no email
4. Find `heartbeat:emma-vibelabs` → replace with `heartbeat:<account_key>` or comment out

### bot_common.py
1. Find `CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")` → replace path with the detected Claude CLI path from Phase 0
2. Find `CODEX_BIN = "/opt/homebrew/bin/codex"` → replace with detected codex path, or set to `None` if not found

### watcher.py (only if email is enabled)
1. Find `'emma-vibelabs'` → replace with the email account key

If OWNER_TELEGRAM_ID is still pending (user didn't have it yet), leave `ALLOWED_CHAT_IDS = {0}` and add a comment: `# TODO: Replace 0 with your Telegram user ID`

---

## Phase 5: Secrets

Generate a `.env` file:

```
# Bot tokens — get these from the respective platforms
TELEGRAM_BOT_TOKEN=

# Uncomment if using Slack:
# SLACK_BOT_TOKEN=
# SLACK_APP_TOKEN=
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
- [ ] telegram_bot.py exists
- [ ] bot_common.py exists
- [ ] memory/MEMORY.md exists
- [ ] .env exists
- [ ] .gitignore exists

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
```

Report each check as ✓ or ✗ with details on failures.

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
✅ Assistant "[ASSISTANT_NAME]" is ready!

Setup complete:
  ✓ Project directory: [PATH]
  ✓ Identity: CLAUDE.md, SOUL.md
  ✓ Telegram bot: telegram_bot.py
  ✓ Memory system: memory/
  ✓ Python environment: venv/
  [✓/✗] Bot token: [configured/pending]
  [✓/✗] Service: [running/not installed]

Next steps:
  [If token pending] → Get bot token from @BotFather and add to .env
  [If service not installed] → Install the launchd/systemd service
  [If email desired] → Run /add-email to set up email integration
  [If Slack desired] → Run /add-slack to set up Slack integration

Test your assistant:
  cd [PATH]
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  python telegram_bot.py
  → Then message your bot on Telegram!
```

---

## Idempotency Rules

Before EVERY file operation:
1. Check if the file already exists
2. If it does, ask: "This file already exists. Overwrite, skip, or show diff?"
3. Never silently overwrite
4. For venv: check if `venv/bin/python` exists before creating
5. For services: check if plist/unit already loaded before installing
