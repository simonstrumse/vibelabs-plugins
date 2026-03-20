---
name: scrub-pii
description: >
  Scrub leaked PII from an existing assistant deployment. Only removes the original
  template author's personal data (Simon Strumse, Emma Brekke, vibelabs.no, etc.).
  Preserves any values the user has already customized. Use /scrub-pii on a deployed bot.
---

# Scrub Original Author PII

This skill removes the original template author's personal data that leaked into early deployments. It **only** targets known author PII — if you've already replaced some values with your own, those are left untouched.

---

## Step 1: Scan for Author PII

Search the current project directory for these **specific strings** from the original template author. Report each match with file, line number, and context.

### Exact strings to find and remove/replace:

**Names:**
- `Simon Souyris Strumse` — author's full name
- `Simon Strumse` — author's short name
- `Emma Brekke` — author's assistant name

**Email addresses:**
- `emma@vibelabs.no`
- `simonstrumse@gmail.com`
- `simon@vibelabs.no`
- `hello@vibelabs.no`
- `oslo@seaexperience.no`
- `christina@startuplab.no` — example contact from author's setup
- `cwb@norscanas.no` — example contact from author's setup

**Identifiers:**
- `emma-vibelabs` — email account key
- `462445799` — author's Telegram user ID
- `U09S7RZG77Y` — author's Slack user ID

**Code identifiers:**
- `simon-voice` — voice profile directory name
- `emma.debug` — debug logger namespace

**Example data from author's setup:**
- `Startuplab` / `startuplab` — example company name
- `Easypick AS` — example vendor name
- `vibelabs.no` — author's domain (in example contexts, not plugin attribution)
- `seaexperience` — author's other org (in email references)

**Run the scan:**
```bash
grep -rn "Simon Souyris Strumse\|Simon Strumse\|Emma Brekke\|emma@vibelabs\|simonstrumse@gmail\|simon@vibelabs\|hello@vibelabs\|oslo@seaexperience\|emma-vibelabs\|462445799\|U09S7RZG77Y\|simon-voice\|emma\.debug\|christina@startuplab\|cwb@norscanas\|Startuplab\|Easypick AS" . --include="*.py" --include="*.md" --include="*.json" --include="*.txt" | grep -v ".claude-plugin/plugin.json" | grep -v "node_modules"
```

### What to SKIP (not author PII):
- `.claude-plugin/plugin.json` — author attribution is intentional, not a leak
- `README.md` credits section
- Any marketplace/plugin metadata
- `.env` files — user's own secrets
- `.git/` directory
- Values the user has already replaced with their own data

---

## Step 2: Report Findings

Present results grouped by category:

```markdown
## Author PII Scan Results

### Names found
| String | Count | Files |
|---|---|---|
| "Emma Brekke" | 5 | telegram_bot.py, CLAUDE.md, ... |
| "Simon" (in context) | 8 | telegram_bot.py, SOUL.md, ... |

### Emails found
| String | Count | Files |
|---|---|---|
| "emma@vibelabs.no" | 3 | telegram_bot.py, watcher.py |

### Identifiers found
| String | Count | Files |
|---|---|---|
| "462445799" | 2 | telegram_bot.py |
| "emma-vibelabs" | 2 | telegram_bot.py, watcher.py |

**Total: X occurrences across Y files**
```

If **zero matches**, tell the user their project is already clean and exit.

---

## Step 3: Determine What Needs Replacing

For each found PII string, check whether the user has already set up their own values elsewhere in the project. The goal is to understand what **their** assistant is called so we can replace author PII with the correct values.

**Detection strategy:**
1. Read `CLAUDE.md` — if it exists and doesn't mention "Emma Brekke" or "Simon", the user likely already customized it. Extract the assistant name and owner name from it.
2. Read `SOUL.md` — same check.
3. Check `ALLOWED_CHAT_IDS` in `telegram_bot.py` — if it's not `462445799`, the user already set their own ID.
4. Check the `EA_SYSTEM_PROMPT` in `telegram_bot.py` — if it mentions a name other than Emma/Simon, that's the user's data.

**If user data is already present:**
- Use the user's existing values as replacements (no need to ask)
- Only ask about values that are still set to the author's PII

**If no customization detected (fresh deploy with author PII everywhere):**
Ask the user:
- "What is your full name?" (owner)
- "What is the assistant's full name?"
- "What is your Telegram user ID?"
- "What is the assistant's email?" (if email references found)
- "What email account key should be used?" (if `emma-vibelabs` found)

**Only ask about values that were actually found in the scan.** Don't ask about things that aren't present.

---

## Step 4: Replace Author PII Only

For each match from Step 1, replace **only the author's PII** with the user's values. Do NOT touch anything the user has already customized.

### Replacement map:

| Author PII | Replace with |
|---|---|
| `Simon Souyris Strumse` | User's owner full name |
| `Simon Strumse` | User's owner full name |
| `Simon` (in identity/prompt contexts) | User's owner first name |
| `Emma Brekke` | User's assistant full name |
| `Emma` (in identity/prompt contexts) | User's assistant first name |
| `emma@vibelabs.no` | User's assistant email |
| `simonstrumse@gmail.com` | Remove or replace with user's email |
| `simon@vibelabs.no` | Remove (was multi-account, no longer needed) |
| `hello@vibelabs.no` | Remove |
| `oslo@seaexperience.no` | Remove |
| `emma-vibelabs` | User's email account key |
| `462445799` | User's Telegram user ID |
| `U09S7RZG77Y` | Remove (Slack ID, not needed in base setup) |
| `simon-voice` | `<owner_lower>-voice` |
| `emma.debug` | `assistant.debug` (or `<assistant_lower>.debug`) |
| `christina@startuplab.no` | `contact@example.com` |
| `cwb@norscanas.no` | `contact2@example.com` |
| `Startuplab` | `Example Company` |
| `Easypick AS` | `Vendor Inc` |

### Context-sensitive "Simon" and "Emma" replacement:

The words "Simon" and "Emma" appear in many contexts. Only replace them when they refer to the **author's identity**, not when they're part of generic code:

**DO replace:**
- `"Simon's inbox"` → `"<owner>'s inbox"`
- `"reply as Emma"` → `"reply as <assistant>"`
- `"note it for Simon"` → `"note it for <owner>"`
- `from_="simon"` → `from_="owner"` (or user's lowercase name)
- `from_="emma"` → `from_="assistant"`

**Do NOT replace:**
- Variable names that happen to contain these letters
- Strings where the user has already changed the name
- Plugin metadata / author credits

---

## Step 5: Check for Opinionated Features

Scan for features from the original author's setup that may not be needed:

### Gemini 3 Probe
```bash
grep -rn "gemini.*probe\|GEMINI3\|gemini3\|_gemini3_probe" . --include="*.py"
```
If found: "The Gemini 3 image probe is a monitoring tool from the original author. Remove it? (y/n)"

### Codex Engine System
```bash
grep -rn "ENGINE_CODEX\|engine_config\|CODEX_BIN\|run_codex\|cmd_engine" . --include="*.py"
```
If found: "The Codex engine switcher lets you swap between Claude and OpenAI Codex. Remove it to simplify? (y/n)"

### Slack Relay
```bash
grep -rn "_poll_relay\|cmd_relay\|cmd_topics\|from relay import\|from shared_topics import" . --include="*.py"
```
If found: "The Slack relay bridges messages between Slack and Telegram. Do you use this? If not, remove it? (y/n)"

Only remove features the user confirms they don't need.

---

## Step 6: Verify

After all replacements:

1. Re-run the exact same grep from Step 1
2. Confirm zero author PII matches remain
3. Report:

```markdown
## Scrub Complete

**Author PII removed:** X occurrences across Y files
**Features removed:** [list if any]

**Files modified:**
- [list]

**Verification:** Zero author PII remaining
```

---

## Safety Rules

- **Only target author PII** — never overwrite the user's own customized values
- **Show changes before applying** — present diffs, ask for confirmation
- **Never modify .env** — that has the user's own secrets
- **Suggest a backup first:** `cp -r . ../backup-before-scrub`
- **Test after scrubbing:** `python telegram_bot.py` to check for import errors
- **Be conservative with "Simon"/"Emma"** — only replace in identity contexts, not in generic code
