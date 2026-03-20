#!/usr/bin/env python3
"""Telegram bot that bridges messages to Claude Code running in the Assistent project."""

import asyncio
import functools
import glob
import json
import logging
import os
import re
import signal
import time
from datetime import datetime

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from telegram import BotCommand, Update
from telegram.error import TelegramError
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from bot_common import (
    PROJECT_DIR,
    PHOTO_MAX_SIZE,
    IMAGE_EXTENSIONS,
    SessionManager,
    run_assistant,
    run_assistant_streaming,
    consolidate_session,
    split_message,
    extract_image_markers,
    validate_image_path,
    dbg,
)
from conversation_logger import log_message
from engine_config import (
    ENGINE_CLAUDE,
    ENGINE_CODEX,
    get_engine_state,
    set_engine_state,
)
from task_queue import TaskQueue
from watcher import HeartbeatWatcher
from relay import (
    get_relays, mark_forwarded, mark_answered, find_relay_by_prefix,
    cleanup_old as relay_cleanup,
)
from runtime_support import (
    build_runtime_context,
    compose_system_prompt,
    inject_runtime_context,
    prepare_runtime_environment,
)
from shared_topics import (
    find_shared_topic_by_prefix,
    get_recent_shared_topics,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN environment variable is required. "
        "Set it before starting the bot."
    )
ALLOWED_CHAT_IDS = {462445799}  # Simon's Telegram user ID
ACTIVE_PLAN_FILE = os.path.join(PROJECT_DIR, ".claude", "plans", "active-telegram-plan.md")
CLAUDE_PLANS_DIR = os.path.expanduser("~/.claude/plans")

# Session manager (separate file from Slack)
SESSIONS_FILE = os.path.join(PROJECT_DIR, "memory", ".sessions-telegram.json")
sessions = SessionManager(SESSIONS_FILE)

# Task queue and watcher (initialized in main)
task_queue: TaskQueue | None = None
watcher: HeartbeatWatcher | None = None

# Global lock for all assistant subprocess calls.
_claude_lock = asyncio.Lock()

# Track active Claude subprocess per chat for /cancel
_active_procs: dict[int, asyncio.subprocess.Process] = {}

# Track last known token usage per session key for /context
_last_usage: dict[str, dict] = {}

# Track last known rate-limit windows per session key for /usage (Codex)
_last_rate_limits: dict[str, dict] = {}

# Track last failed request per chat for /retry
_last_failed_request: dict[int, dict] = {}

CLAUDE_USAGE_SCRIPT = os.path.join(
    PROJECT_DIR, "scripts", "fetch_claude_usage_windows.swift")
CODEX_SESSIONS_GLOB = os.path.expanduser("~/.codex/sessions/*/*/*/*.jsonl")
GEMINI3_PROBE_STATE_FILE = os.path.join(
    PROJECT_DIR, "memory", ".gemini3-probe-state.json")
GEMINI3_PROBE_INTERVAL_SECONDS = 3600  # hourly
GEMINI3_PROBE_STARTUP_DELAY_SECONDS = 30
GEMINI3_PROBE_MODEL = "gemini-3-pro-image-preview"
GEMINI3_PROBE_LOCATION = "global"


def _engine_usage_key(chat_id: int, engine: str) -> str:
    return f"{_session_key(chat_id)}:{engine}"


def _resolve_engine_model(*, model_override: str | None = None,
                          claude_only_override: bool = False) -> tuple[str, str | None]:
    state = get_engine_state()
    engine = state["engine"]
    engine_model = state["models"].get(engine)
    if model_override is None:
        return engine, engine_model
    if claude_only_override and engine != ENGINE_CLAUDE:
        return engine, engine_model
    return engine, model_override


def _is_engine_failure(text: str) -> bool:
    if not text:
        return False
    checks = (
        "Error: Claude binary not found",
        "Error: Codex binary not found",
        "Claude timed out",
        "Codex timed out",
        "Codex failed with code",
        "Something went wrong. Check the logs or try again.",
        "unsupported assistant engine",
    )
    return any(marker in text for marker in checks)


def _with_failure_guidance(text: str) -> str:
    return (
        text.rstrip()
        + "\n\nPrøv dette:\n"
        + "/retry\n"
        + "/engine claude\n"
        + "/engine codex\n"
        + "/engine <engine> <model>"
    )


def _command_name(text: str | None) -> str:
    raw = (text or "").strip()
    if not raw.startswith("/"):
        return raw or "unknown"
    return raw.split()[0][1:]


def _log_command_request(update: Update, *, command: str | None = None) -> None:
    text = update.message.text or ""
    log_message(
        ch="telegram",
        dir="in",
        from_="simon",
        msg=text,
        type_="command",
        command=command or _command_name(text),
    )


async def _reply_command(update: Update, text: str, *, command: str) -> None:
    await _safe_reply(update.message, text)
    log_message(
        ch="telegram",
        dir="out",
        from_="emma",
        msg=text,
        type_="command_result",
        command=command,
    )


def _cleanup_retry_artifact(payload: dict | None) -> None:
    if not payload or payload.get("kind") != "photo":
        return
    path = payload.get("image_path")
    if not path:
        return
    try:
        os.unlink(path)
    except OSError:
        pass


def _set_failed_request(chat_id: int, payload: dict | None) -> None:
    existing = _last_failed_request.get(chat_id)
    if payload is None:
        _last_failed_request.pop(chat_id, None)
        _cleanup_retry_artifact(existing)
        return

    old_path = existing.get("image_path") if existing else None
    new_path = payload.get("image_path")
    if old_path and old_path != new_path:
        _cleanup_retry_artifact(existing)
    _last_failed_request[chat_id] = payload


def _failed_request_keeps_file(chat_id: int, path: str) -> bool:
    payload = _last_failed_request.get(chat_id)
    return bool(
        payload
        and payload.get("kind") == "photo"
        and payload.get("image_path") == path
    )

# ---------------------------------------------------------------------------
# Heartbeat context injection — bridges heartbeat → chat context
# ---------------------------------------------------------------------------
_HEARTBEAT_OUTBOUND_FILE = os.path.join(PROJECT_DIR, "memory", ".heartbeat-outbound.jsonl")
_HEARTBEAT_TTL_HOURS = 4  # Ignore heartbeat context older than this


def _save_heartbeat_outbound(chat_id: int, message: str) -> None:
    """Append heartbeat message to outbound queue for later injection."""
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "chat_id": chat_id,
        "message": message,
        "consumed": False,
    }
    tmp = _HEARTBEAT_OUTBOUND_FILE + ".tmp"
    try:
        # Append to JSONL (atomic: read existing, append, write via tmp+replace)
        lines = []
        if os.path.exists(_HEARTBEAT_OUTBOUND_FILE):
            with open(_HEARTBEAT_OUTBOUND_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
        lines.append(json.dumps(entry, ensure_ascii=False) + "\n")
        with open(tmp, "w", encoding="utf-8") as f:
            f.writelines(lines)
        os.replace(tmp, _HEARTBEAT_OUTBOUND_FILE)
    except OSError as e:
        log.warning("Failed to save heartbeat outbound: %s", e)


def _peek_heartbeat_context(chat_id: int) -> str | None:
    """Read pending heartbeat context for a chat WITHOUT consuming it.

    Returns formatted context string or None.  Filters by chat_id and TTL.
    """
    try:
        with open(_HEARTBEAT_OUTBOUND_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, FileNotFoundError):
        return None

    now = datetime.now()
    pending = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("consumed", True):
            continue
        if entry.get("chat_id") != chat_id:
            continue
        ts = entry.get("timestamp", "")
        try:
            entry_time = datetime.fromisoformat(ts)
            age_hours = (now - entry_time).total_seconds() / 3600
            if age_hours > _HEARTBEAT_TTL_HOURS:
                continue
        except (ValueError, TypeError):
            continue
        pending.append(entry)

    if not pending:
        return None

    # Build context from all pending heartbeats
    parts = []
    for entry in pending:
        ts = entry.get("timestamp", "ukjent")
        msg = entry.get("message", "")
        parts.append(f"[Heartbeat kl {ts}]\n{msg}")

    header = (
        "[HEARTBEAT-KONTEKST: Emma sendte følgende heartbeat-oppsummering(er) "
        "til Simon. Simons neste melding kan være et svar på noe her. "
        "Bruk kun hvis relevant.]"
    )
    return header + "\n\n" + "\n\n---\n\n".join(parts)


def _mark_heartbeats_consumed(chat_id: int) -> None:
    """Mark all pending heartbeats for a chat as consumed. Call after successful processing."""
    try:
        with open(_HEARTBEAT_OUTBOUND_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, FileNotFoundError):
        return

    updated = []
    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
        try:
            entry = json.loads(line_s)
        except json.JSONDecodeError:
            updated.append(line)
            continue
        if entry.get("chat_id") == chat_id and not entry.get("consumed", True):
            entry["consumed"] = True
        updated.append(json.dumps(entry, ensure_ascii=False) + "\n")

    tmp = _HEARTBEAT_OUTBOUND_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.writelines(updated)
        os.replace(tmp, _HEARTBEAT_OUTBOUND_FILE)
    except OSError:
        pass  # Best effort

# System prompt that shapes Claude's behavior when running as a Telegram EA.
# CLAUDE.md (loaded automatically from the project dir) provides API docs and
# tools. This prompt tells Claude *how to act* as an executive assistant.
EA_SYSTEM_PROMPT = compose_system_prompt("""\
You ARE Emma Brekke, Simon Souyris Strumse's executive assistant. \
You speak as Emma — first person, never third person. Operating via Telegram.

SYSTEMS YOU MANAGE:
- Email: emma@vibelabs.no (your account), simonstrumse@gmail.com, \
simon@vibelabs.no, hello@vibelabs.no, oslo@seaexperience.no (read-only unless Simon asks)
- Calendar, Drive, Docs, Sheets, Contacts, Tasks (via GoogleServices)
- Slack: Emma has her own Slack bot (slack_bot.py, Socket Mode). \
Default: post to Slack through the bot. Only use Chrome for Slack if Simon explicitly asks.
- Telegram: this chat (telegram_bot.py)
- Relay: Slack↔Telegram bridge (relay.py) — forward questions between channels.

PERSONALITY:
- Communicate like Simon: direct, brief, Norwegian by default, English when needed.
- Keep Telegram messages short. Use bullet points, not paragraphs.
- Don't explain what you're doing — just do it and report results.
- When drafting emails, use Simon's voice (see email-learnings.md and CLAUDE.md).

EMAIL DELEGATION:
- ALL email work goes through the email specialist subagent.
- When Simon asks about email, inbox, drafts, or anything email-related: \
delegate to the email specialist using the Task tool (subagent_type: "email-specialist").
- This includes: reading emails, processing inbox, drafting replies, archiving, \
sending, and any email research.
- DO NOT read, draft, or send emails yourself — always delegate.
- Forward the specialist's report to Simon as-is (it's already Telegram-formatted).

AUTONOMY RULES:
- You CAN: check calendar, search, create drafts, update TASKS.md, \
check on existing tasks, research, browse the web, manage files, post to Slack.
- You MUST ASK before: accepting invitations, deleting anything, \
making purchases, responding to financial/legal matters.

TASK AWARENESS:
- Check TASKS.md for active tasks and their status.
- If a task is overdue or critical, proactively mention it.

PERSISTENT MEMORY:
- Read memory/MEMORY.md for durable facts, preferences, and learned patterns.
- Read memory/STATE.md for current operational context, live priorities, watchouts, and active project status.
- When you learn something important, write it to memory/MEMORY.md immediately.
- Keep MEMORY.md concise and durable. Put time-sensitive operational context in memory/STATE.md.

CONVERSATION HISTORY (3-lag system):
- For quick current context: read memory/STATE.md first
- For background context: read memory/SUMMARY.md if relevant
- For a specific day: read memory/summaries/YYYY-MM-DD.md
- For exact messages: grep memory/conversations/*.jsonl
- NEVER load raw JSONL into context.

FORMAT:
- Keep responses under 500 words for Telegram readability.
- Use emoji sparingly (one per section header max).

IMAGES IN TELEGRAM:
- You CAN send images in this Telegram chat.
- For EXISTING files: [SEND_IMAGE:/absolute/path/to/image.png]
- For NEW files you create: auto-detected and sent.
- Supported: PNG, JPG, JPEG, WebP, GIF, BMP.
""")

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# Avoid leaking bot token via verbose HTTP client INFO logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


class _RedactTelegramTokenFilter(logging.Filter):
    """Mask bot token if a dependency logs full Telegram API URLs."""

    _token_url_re = re.compile(r"(https://api\\.telegram\\.org/bot)([^/]+)(/)")

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
            redacted = self._token_url_re.sub(r"\\1<redacted>\\3", msg)
            if redacted != msg:
                record.msg = redacted
                record.args = ()
        except Exception:
            pass
        return True


logging.getLogger().addFilter(_RedactTelegramTokenFilter())

# ---------------------------------------------------------------------------
# Email specialist agent — loaded for heartbeat use
# ---------------------------------------------------------------------------
_AGENT_FILE = os.path.join(PROJECT_DIR, ".claude", "agents", "email-specialist.md")


def _load_email_specialist_prompt() -> str:
    """Read the email specialist agent body (after frontmatter) for use as system prompt.

    The heartbeat uses this directly as system_prompt — it needs the rules
    (voice, classification, drafting) but not the full workflow skills.
    """
    try:
        with open(_AGENT_FILE) as f:
            content = f.read()
        # Skip YAML frontmatter (between --- markers)
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
        return content
    except (FileNotFoundError, OSError) as e:
        log.warning("Could not load email specialist agent file: %s — using fallback", e)
        return (
            "You are Emma Brekke, Simon's executive assistant handling email triage. "
            "Read CLAUDE.md and email-learnings.md for context. "
            "Check memory/ACTIVE_THREADS.md for thread-specific instructions and "
            "memory/STATE.md for current operational context."
        )


EMAIL_SPECIALIST_PROMPT = compose_system_prompt(_load_email_specialist_prompt())


# ---------------------------------------------------------------------------
# Telegram helpers
# ---------------------------------------------------------------------------

def _session_key(chat_id: int) -> str:
    """Build a session key for a Telegram chat."""
    return f"tg:{chat_id}"


def _telegram_runtime_context(chat_id: int, *, purpose: str,
                              extra_lines: list[str] | None = None) -> str:
    key = _session_key(chat_id)
    return build_runtime_context(
        channel="telegram",
        chat_id=str(chat_id),
        session_key=key,
        purpose=purpose,
        extra_lines=extra_lines,
    )


def authorized(func):
    """Decorator to restrict access to allowed chat IDs."""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id not in ALLOWED_CHAT_IDS:
            log.warning("Unauthorized access from chat_id=%s",
                        update.effective_chat.id)
            return
        return await func(update, context)
    return wrapper


async def _safe_reply(target, text: str) -> None:
    """Send a message with error handling for Telegram API failures."""
    for chunk in split_message(text):
        try:
            await target.reply_text(chunk)
        except TelegramError as e:
            log.error("Telegram error sending message: %s", e)


async def _safe_send(bot, chat_id: int, text: str) -> None:
    """Send a bot message with error handling for Telegram API failures."""
    for chunk in split_message(text):
        try:
            await bot.send_message(chat_id=chat_id, text=chunk)
        except TelegramError as e:
            log.error("Telegram error sending to %s: %s", chat_id, e)


async def _safe_send_photo(bot, chat_id: int, photo_path: str,
                           caption: str | None = None) -> None:
    """Send a photo via Telegram, falling back to document for large files."""
    if not validate_image_path(photo_path):
        return
    if not os.path.isfile(photo_path):
        log.warning("Photo not found: %s", photo_path)
        return
    try:
        file_size = os.path.getsize(photo_path)
        file_name = os.path.basename(photo_path)
        with open(photo_path, "rb") as f:
            if file_size <= PHOTO_MAX_SIZE:
                await bot.send_photo(chat_id=chat_id, photo=f,
                                     caption=caption or file_name)
            else:
                await bot.send_document(chat_id=chat_id, document=f,
                                        caption=caption or file_name)
        log.info("Sent image to %s: %s (%d bytes)", chat_id, photo_path,
                 file_size)
    except TelegramError as e:
        log.error("Telegram error sending photo %s: %s", photo_path, e)
    except Exception as e:
        log.error("Error sending photo %s: %s", photo_path, e)


def _parse_reset_time(value) -> str:
    """Format reset timestamp to local short form."""
    if value is None:
        return "ukjent"
    try:
        if isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(float(value))
        elif isinstance(value, str):
            raw = value.strip()
            if not raw:
                return "ukjent"
            if raw.endswith("Z"):
                raw = raw[:-1] + "+00:00"
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is not None:
                dt = dt.astimezone()
        else:
            return "ukjent"
        return dt.strftime("%a %H:%M")
    except (TypeError, ValueError, OSError):
        return "ukjent"


def _format_window_line(label: str, window: dict | None) -> str | None:
    """Render a single usage window as one line."""
    if not isinstance(window, dict):
        return None
    used_raw = window.get("utilization")
    try:
        used = max(0.0, min(100.0, float(used_raw)))
    except (TypeError, ValueError):
        return None
    left = max(0.0, 100.0 - used)
    reset_at = _parse_reset_time(window.get("resets_at"))
    return f"{label}: {used:.0f}% brukt · {left:.0f}% igjen · reset {reset_at}"


async def _fetch_claude_usage_windows() -> tuple[dict | None, str | None]:
    """Fetch Claude 5h/7d usage windows via local Swift helper."""
    if not os.path.isfile(CLAUDE_USAGE_SCRIPT):
        return None, "usage-script mangler"

    try:
        proc = await asyncio.create_subprocess_exec(
            "swift", CLAUDE_USAGE_SCRIPT,
            cwd=PROJECT_DIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        return None, "swift ikke installert"
    except OSError:
        return None, "kunne ikke starte usage-script"

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=20)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return None, "timeout ved henting av usage"

    out = stdout.decode("utf-8", errors="replace").strip()
    err = stderr.decode("utf-8", errors="replace").strip()

    if proc.returncode != 0:
        if err:
            return None, err.splitlines()[-1][:140]
        if out:
            return None, out.splitlines()[-1][:140]
        return None, "ukjent feil fra usage-script"

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return None, "ugyldig usage-format"

    if not isinstance(data, dict):
        return None, "ugyldig usage-format"
    return data, None


def _load_gemini3_probe_state() -> dict:
    """Load persisted Gemini 3 probe state."""
    default = {
        "enabled": True,
        "stop_after_success": True,
        "last_status": None,
        "last_http_status": None,
        "last_checked_at": None,
        "last_message": None,
        "last_notified_status": None,
    }
    try:
        with open(GEMINI3_PROBE_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return default
        out = default.copy()
        out.update(data)
        return out
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return default


def _save_gemini3_probe_state(state: dict) -> None:
    """Persist Gemini 3 probe state."""
    tmp = GEMINI3_PROBE_STATE_FILE + ".tmp"
    try:
        os.makedirs(os.path.dirname(GEMINI3_PROBE_STATE_FILE), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.replace(tmp, GEMINI3_PROBE_STATE_FILE)
    except OSError as e:
        log.warning("Gemini probe: failed to save state: %s", e)


async def _run_cmd_with_timeout(
    *argv: str,
    timeout: float = 20.0,
    stdin_data: bytes | None = None,
) -> tuple[int, str, str]:
    """Run a command with timeout and return (code, stdout, stderr)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdin=(asyncio.subprocess.PIPE if stdin_data is not None else None),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=PROJECT_DIR,
        )
    except FileNotFoundError:
        return 127, "", f"command not found: {argv[0]}"
    except OSError as e:
        return 126, "", str(e)

    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(input=stdin_data), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return 124, "", "timeout"

    stdout = stdout_b.decode("utf-8", errors="replace").strip()
    stderr = stderr_b.decode("utf-8", errors="replace").strip()
    return proc.returncode or 0, stdout, stderr


async def _run_gemini3_image_probe_once() -> tuple[str, int | None, str]:
    """Probe Gemini 3 image preview availability via Vertex REST."""
    code, project_out, project_err = await _run_cmd_with_timeout(
        "gcloud", "config", "get-value", "project", timeout=15)
    project_id = project_out.strip()
    if code != 0 or not project_id:
        msg = project_err or project_out or "kunne ikke lese aktivt gcloud-prosjekt"
        return "probe_error", None, msg[:220]

    code, token_out, token_err = await _run_cmd_with_timeout(
        "gcloud", "auth", "print-access-token", timeout=20)
    token = token_out.strip()
    if code != 0 or not token:
        msg = token_err or token_out or "kunne ikke hente OAuth-token"
        return "probe_error", None, msg[:220]

    url = (
        "https://aiplatform.googleapis.com/v1/projects/"
        f"{project_id}/locations/{GEMINI3_PROBE_LOCATION}/publishers/google/models/"
        f"{GEMINI3_PROBE_MODEL}:generateContent"
    )
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": "Generate a tiny blue square test image."}],
        }],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }

    resp_path = os.path.join(
        "/tmp", f"gemini3_probe_response_{int(time.time())}.json")
    try:
        code, http_status_text, curl_err = await _run_cmd_with_timeout(
            "curl",
            "-sS",
            "-o",
            resp_path,
            "-w",
            "%{http_code}",
            "-X",
            "POST",
            url,
            "-H",
            f"Authorization: Bearer {token}",
            "-H",
            "Content-Type: application/json",
            "--data-binary",
            "@-",
            timeout=45,
            stdin_data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        )
    finally:
        pass

    if code != 0:
        return "probe_error", None, (curl_err or "curl-feil")[:220]

    try:
        http_status = int(http_status_text.strip() or "0")
    except ValueError:
        return "probe_error", None, f"ugyldig HTTP-status: {http_status_text[:80]}"

    body_text = ""
    try:
        with open(resp_path, "r", encoding="utf-8") as f:
            body_text = f.read(2000)
    except OSError:
        body_text = ""
    finally:
        try:
            os.remove(resp_path)
        except OSError:
            pass

    if http_status == 200:
        return "ok", http_status, "200 OK"

    err_status = ""
    err_msg = ""
    if body_text:
        try:
            body = json.loads(body_text)
            if isinstance(body, dict):
                err = body.get("error")
                if isinstance(err, dict):
                    err_status = str(err.get("status") or "").strip()
                    err_msg = str(err.get("message") or "").strip()
        except json.JSONDecodeError:
            pass

    status_key = (err_status or f"HTTP_{http_status}").lower()
    msg = (err_msg or err_status or f"HTTP {http_status}")[:220]
    return status_key, http_status, msg


def _format_gemini_probe_notification(
    status_key: str,
    http_status: int | None,
    detail: str,
    checked_at: str,
    disabled: bool,
) -> str:
    """Build a short Telegram notification for Gemini probe status."""
    label = status_key.upper()
    http_part = f"HTTP {http_status}" if http_status is not None else "HTTP ?"
    lines = [
        "🔎 *Gemini 3 probe (hourly)*",
        f"Model: `{GEMINI3_PROBE_MODEL}` ({GEMINI3_PROBE_LOCATION})",
        f"Status: `{label}` · {http_part}",
        f"Detalj: {detail}",
        f"Sjekket: {checked_at}",
    ]
    if disabled:
        lines.append("Auto-probe stoppet etter grønn status.")
    return "\n".join(lines)


async def _gemini3_probe_loop(bot) -> None:
    """Hourly probe for Gemini 3 image preview with status-change alerts."""
    await asyncio.sleep(GEMINI3_PROBE_STARTUP_DELAY_SECONDS)
    log.info("Gemini probe: started (interval=%ds)", GEMINI3_PROBE_INTERVAL_SECONDS)

    while True:
        try:
            state = _load_gemini3_probe_state()
            if not state.get("enabled", True):
                await asyncio.sleep(GEMINI3_PROBE_INTERVAL_SECONDS)
                continue

            status_key, http_status, detail = await _run_gemini3_image_probe_once()
            checked_at = datetime.now().isoformat(timespec="seconds")

            state["last_status"] = status_key
            state["last_http_status"] = http_status
            state["last_message"] = detail
            state["last_checked_at"] = checked_at

            last_notified = state.get("last_notified_status")
            notify = status_key != last_notified
            disabled = False

            if status_key == "ok" and state.get("stop_after_success", True):
                state["enabled"] = False
                disabled = True

            _save_gemini3_probe_state(state)

            if notify:
                text = _format_gemini_probe_notification(
                    status_key=status_key,
                    http_status=http_status,
                    detail=detail,
                    checked_at=checked_at,
                    disabled=disabled,
                )
                for chat_id in ALLOWED_CHAT_IDS:
                    await _safe_send(bot, chat_id, text)
                    log.info("Gemini probe: notified chat %s (%s)", chat_id, status_key)
                state["last_notified_status"] = status_key
                _save_gemini3_probe_state(state)
        except Exception as e:
            log.warning("Gemini probe: loop error: %s", e)

        await asyncio.sleep(GEMINI3_PROBE_INTERVAL_SECONDS)


def _format_codex_usage_lines(rate_limits: dict | None) -> list[str]:
    """Render Codex primary/secondary rate-limit windows."""
    if not isinstance(rate_limits, dict):
        return ["Ingen Codex usage-data ennå. Kjør en Codex-melding først."]

    lines: list[str] = []
    primary = rate_limits.get("primary")
    secondary = rate_limits.get("secondary")

    if isinstance(primary, dict):
        line = _format_window_line("5h", {
            "utilization": primary.get("used_percent"),
            "resets_at": primary.get("resets_at"),
        })
        if line:
            lines.append(line)

    if isinstance(secondary, dict):
        line = _format_window_line("7d", {
            "utilization": secondary.get("used_percent"),
            "resets_at": secondary.get("resets_at"),
        })
        if line:
            lines.append(line)

    return lines or ["Ingen Codex usage-data ennå. Kjør en Codex-melding først."]


def _read_last_lines(path: str, max_lines: int = 2500) -> list[str]:
    """Read up to max_lines from end of file without loading the full file."""
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            chunk_size = 8192
            buf = b""
            lines = 0
            while pos > 0 and lines <= max_lines:
                take = min(chunk_size, pos)
                pos -= take
                f.seek(pos, os.SEEK_SET)
                buf = f.read(take) + buf
                lines = buf.count(b"\n")
            text = buf.decode("utf-8", errors="replace")
            all_lines = text.splitlines()
            if len(all_lines) > max_lines:
                return all_lines[-max_lines:]
            return all_lines
    except OSError:
        return []


def _fetch_codex_rate_limits_from_sessions() -> tuple[dict | None, str | None]:
    """Fetch latest Codex rate_limits from local session logs."""
    try:
        files = glob.glob(CODEX_SESSIONS_GLOB)
    except OSError:
        return None, "kunne ikke lese Codex session-mappe"
    if not files:
        return None, "fant ingen Codex sessions"

    try:
        files.sort(key=os.path.getmtime, reverse=True)
    except OSError:
        files.sort(reverse=True)

    for path in files[:10]:
        for line in reversed(_read_last_lines(path, max_lines=2500)):
            if "\"type\":\"event_msg\"" not in line:
                continue
            if "\"token_count\"" not in line or "\"rate_limits\"" not in line:
                continue
            try:
                evt = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = evt.get("payload")
            if not isinstance(payload, dict):
                continue
            if payload.get("type") != "token_count":
                continue
            rate_limits = payload.get("rate_limits")
            if isinstance(rate_limits, dict):
                return rate_limits, None

    return None, "fant ingen token_count/rate_limits i nylige Codex sessions"


# ---------------------------------------------------------------------------
# Message queue and processing
# ---------------------------------------------------------------------------

async def _queue_and_process(chat_id: int, prompt: str, update: Update,
                             context: ContextTypes.DEFAULT_TYPE,
                             model: str | None = None,
                             retry_payload: dict | None = None) -> None:
    """Queue a prompt and process when the lock is available.

    Messages that arrive while Claude is processing get batched into one
    combined prompt — similar to typing in the terminal while Claude works.
    All queued messages are joined with blank lines and sent as a single turn.

    Uses send+edit streaming: first text chunk sends a new message, subsequent
    chunks edit it in-place with a cursor indicator. No notification spam.
    """
    key = _session_key(chat_id)
    sessions.get_pending(key).append((prompt, update))

    async with sessions.get_lock(key):
        queued = list(sessions.get_pending(key))
        sessions.get_pending(key).clear()

        if not queued:
            return  # already processed as part of an earlier batch

        prompts = [p for p, _ in queued]
        last_update = queued[-1][1]
        combined = "\n\n".join(prompts)

        if len(queued) > 1:
            log.info("Batched %d messages for chat %s", len(queued), chat_id)

        # Log incoming message(s) to conversation log
        log_message(ch="telegram", dir="in", from_="simon", msg=combined)

        engine, resolved_model = _resolve_engine_model(model_override=model)
        session_id, is_new = sessions.get_session(key, engine=engine)
        sessions.touch_activity(key)  # Mark active during processing (not just on message receive)
        sid_preview = (session_id[:8] if session_id else "new")
        log.info("Processing for %s (%s session %s, %s): %s",
                 chat_id, engine, sid_preview, "new" if is_new else "resume",
                 combined[:100])
        dbg.info("MSG_IN | chat=%s | engine=%s | session=%s (%s) | msg=%s",
                 chat_id, engine, sid_preview, "new" if is_new else "resume",
                 combined[:300])

        bot = context.bot

        # --- Streaming send+edit state ---
        # (must be defined before the lock scope for final-edit access)
        _streaming_msg_id: int | None = None
        _streaming_text: str = ""
        _last_edit: float = 0
        _status_text: str = ""  # Current tool status shown as suffix
        _last_sent_display: str = ""  # Track last sent text to avoid MESSAGE_NOT_MODIFIED

        async def _tg_text_chunk(chunk: str) -> None:
            """Handle streaming text — send first message, then edit in-place."""
            nonlocal _streaming_msg_id, _streaming_text, _last_edit, _status_text
            nonlocal _last_sent_display
            _streaming_text += chunk
            now = time.time()

            if now - _last_edit < 0.5:  # Max 2 edits/sec (Telegram rate limit safe)
                return

            display = _streaming_text[:4000] + "\u258c"  # Cursor indicator

            if display == _last_sent_display:
                return  # No change — skip to avoid MESSAGE_NOT_MODIFIED

            if _streaming_msg_id is None:
                # First chunk — send new message
                try:
                    msg = await bot.send_message(chat_id=chat_id, text=display)
                    _streaming_msg_id = msg.message_id
                    _last_sent_display = display
                except TelegramError as e:
                    log.warning("Failed to send streaming message: %s", e)
                    return
            else:
                # Subsequent chunks — edit existing message
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=_streaming_msg_id,
                        text=display,
                    )
                    _last_sent_display = display
                except TelegramError:
                    pass

            _last_edit = now
            _status_text = ""  # Clear status once real text flows

        async def _tg_status(status: str) -> None:
            """Show tool execution status when no text is streaming."""
            nonlocal _streaming_msg_id, _status_text, _last_edit
            nonlocal _last_sent_display
            _status_text = status
            now = time.time()

            if now - _last_edit < 1.0:  # Slower rate for status updates
                return

            # Translate technical tool names to Emma-style status
            _EMMA_STATUS = {
                "Running: Bash": "Fikser litt greier",
                "Running: Read": "Blar gjennom noen filer",
                "Running: Write": "Skriver ned noe",
                "Running: Edit": "Justerer litt",
                "Running: Grep": "Graver i arkivet",
                "Running: Glob": "Leter rundt",
                "Running: WebFetch": "Henter noe fra nettet",
                "Running: WebSearch": "Googler litt",
                "Running: TaskOutput": "Venter på svar",
                "Running: Task": "Delegerer til spesialist...",
                "Running: Skill": "Trekker frem et triks",
                "Running: NotebookEdit": "Skriver i notatboka",
                "Running: ToolSearch": "Finner riktig verktøy",
                "Running: TodoWrite": "Noterer ned hva jeg må gjøre",
                "Running: TodoRead": "Sjekker huskelista",
                "Running: TaskCreate": "Lager en oppgave",
                "Running: TaskUpdate": "Oppdaterer oppgavelista",
                "Running: TaskList": "Sjekker oppgavene",
            }
            # Prefix-based matching for MCP tools (mcp__service__action)
            _EMMA_MCP_PREFIX = {
                "mcp__claude-in-chrome__": "Styrer nettleseren",
                "mcp__Neon__": "Snakker med databasen",
            }
            friendly = _EMMA_STATUS.get(status)
            if not friendly and status.startswith("Running: "):
                tool_name = status[len("Running: "):]
                # Check MCP prefix matches
                for prefix, msg in _EMMA_MCP_PREFIX.items():
                    if tool_name.startswith(prefix):
                        friendly = msg
                        break
                if not friendly:
                    friendly = "Jobber med det"
            elif not friendly:
                friendly = status
            display = f"\u23f3 {friendly}..."

            if display == _last_sent_display:
                return  # No change — skip to avoid MESSAGE_NOT_MODIFIED

            if _streaming_msg_id is None:
                # No message yet — send a status-only message
                try:
                    msg = await bot.send_message(
                        chat_id=chat_id, text=display)
                    _streaming_msg_id = msg.message_id
                    _last_sent_display = display
                except TelegramError:
                    return
            elif not _streaming_text:
                # Message exists but no text yet — update with status
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=_streaming_msg_id,
                        text=display,
                    )
                    _last_sent_display = display
                except TelegramError:
                    pass

            _last_edit = now

        # Telegram-specific streaming callbacks
        async def _tg_progress(msg: str) -> None:
            sessions.touch_activity(key)  # Keep heartbeat from interrupting
            # If we already have a streaming message, skip "still working"
            # messages — the live streaming text IS the progress indicator
            if _streaming_msg_id and _streaming_text:
                return
            try:
                await bot.send_chat_action(chat_id=chat_id, action="typing")
            except TelegramError:
                pass
            if not _streaming_msg_id:
                await _safe_send(bot, chat_id, f"\u23f3 {msg}")

        async def _tg_image(path: str) -> None:
            await _safe_send_photo(bot, chat_id, path)

        def _register_proc(proc):
            _active_procs[chat_id] = proc

        usage_key = _engine_usage_key(chat_id, engine)

        def _store_usage(usage):
            _last_usage[usage_key] = usage

        def _store_rate_limits(rate_limits):
            _last_rate_limits[usage_key] = rate_limits

        # Acquire global Claude lock — only one Claude process at a time
        # (project-level lock in Claude Code prevents concurrent subprocesses)
        _t_lock_wait = time.time()
        if _claude_lock.locked():
            log.info("Message from %s waiting for lock (another task running)", chat_id)
            dbg.info("LOCK_WAIT | chat=%s | lock is held", chat_id)
            await _safe_send(bot, chat_id, "\u23f3 Vent litt, holder på med noe annet først...")
        async with _claude_lock:
            _t_lock_acquired = time.time()
            _t_lock_ms = int((_t_lock_acquired - _t_lock_wait) * 1000)
            if _t_lock_ms > 100:
                dbg.info("LOCK_ACQUIRED | waited %dms", _t_lock_ms)
            # Inject heartbeat context if pending (AFTER log, BEFORE Claude)
            _hb_ctx = _peek_heartbeat_context(chat_id)
            if _hb_ctx:
                _claude_prompt = _hb_ctx + "\n\n" + combined
                log.info("Injected heartbeat context into prompt for chat %s", chat_id)
            else:
                _claude_prompt = combined

            _claude_prompt = inject_runtime_context(
                _claude_prompt,
                _telegram_runtime_context(
                    chat_id,
                    purpose="Direct Telegram chat with Simon",
                    extra_lines=[
                        "Pending heartbeat context is injected below when present."
                    ] if _hb_ctx else None,
                ),
            )

            _t_claude_start = time.time()
            try:
                response = await run_assistant_streaming(
                    _claude_prompt,
                    system_prompt=EA_SYSTEM_PROMPT,
                    engine=engine,
                    session_id=session_id,
                    is_new_session=is_new,
                    session_manager=sessions,
                    session_key=key,
                    progress_callback=_tg_progress,
                    image_callback=_tg_image,
                    text_callback=_tg_text_chunk,
                    status_callback=_tg_status,
                    proc_callback=_register_proc,
                    usage_callback=_store_usage,
                    rate_limits_callback=_store_rate_limits,
                    model=resolved_model,
                )
            finally:
                _active_procs.pop(chat_id, None)
                _t_claude_end = time.time()
                _t_total_ms = int((_t_claude_end - _t_claude_start) * 1000)
                dbg.info("TIMING | engine=%s | run=%dms (%.1fs) | chat=%s",
                         engine, _t_total_ms, _t_total_ms / 1000, chat_id)
        current_sid, _ = sessions.get_session(key, engine=engine)
        _sid = current_sid[:8] if current_sid else ""
        _engine_error = _is_engine_failure(response)

        # Consume heartbeat context AFTER successful Claude processing
        if _hb_ctx and not _engine_error:
            _mark_heartbeats_consumed(chat_id)
            log.info("Marked heartbeat context consumed for chat %s", chat_id)

    # Extract [SEND_IMAGE:...] markers and send those images
    response, marker_images = extract_image_markers(response)
    for img_path in marker_images:
        await _safe_send_photo(context.bot, chat_id, img_path)

    dbg.info("MSG_OUT | chat=%s | len=%d | preview=%s",
             chat_id, len(response), response[:200])

    # Detect empty response from crashed/corrupt session → reset and notify
    failed_payload = retry_payload or {"kind": "prompt", "prompt": combined}

    if not response and not _streaming_text:
        log.warning("Empty response for chat %s (session %s) — resetting session",
                     chat_id, _sid)
        sessions.reset_by_session_id(current_sid, engine=engine)
        _set_failed_request(chat_id, failed_payload)
        response = (
            "Beklager, noe gikk galt — sesjonen var korrupt og er nå tilbakestilt.\n"
            "Send meldingen din på nytt, så skal det fungere."
        )

    if _engine_error:
        _set_failed_request(chat_id, failed_payload)
        response = _with_failure_guidance(response)
    else:
        _set_failed_request(chat_id, None)

    if response:
        log_message(ch="telegram", dir="out", from_="emma", msg=response, sid=_sid)

        # Final message: edit the streaming message or send new
        if _streaming_msg_id:
            # Edit existing streaming message to show final response (no cursor)
            final_chunks = split_message(response)
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=_streaming_msg_id,
                    text=final_chunks[0],
                )
            except TelegramError:
                pass
            # Send additional chunks as new messages if response exceeds 4096
            for extra_chunk in final_chunks[1:]:
                await _safe_send(context.bot, chat_id, extra_chunk)
        else:
            await _safe_reply(last_update.message, response)


# ---------------------------------------------------------------------------
# Telegram handlers
# ---------------------------------------------------------------------------

@authorized
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward user messages to Claude Code and reply with the result."""
    chat_id = update.effective_chat.id
    sessions.touch_activity(_session_key(chat_id))

    try:
        await update.message.chat.send_action("typing")
    except TelegramError:
        pass

    await _queue_and_process(chat_id, update.message.text, update, context)


@authorized
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download photos from Telegram, save to disk, and let Claude see them."""
    chat_id = update.effective_chat.id
    sessions.touch_activity(_session_key(chat_id))

    try:
        await update.message.chat.send_action("typing")
    except TelegramError:
        pass

    # Get highest resolution photo
    photo = update.message.photo[-1]  # last element = largest size
    tg_file = await context.bot.get_file(photo.file_id)

    # Save to memory dir
    ext = os.path.splitext(tg_file.file_path or "")[1] or ".jpg"
    img_path = os.path.join(
        PROJECT_DIR, "memory",
        f".photo_{chat_id}_{photo.file_unique_id}{ext}"
    )
    await tg_file.download_to_drive(img_path)
    log.info("Downloaded photo from %s: %s (%dx%d)",
             chat_id, img_path, photo.width, photo.height)

    # Build prompt — include caption if present
    caption = update.message.caption or ""

    # Log photo to conversation log
    log_message(ch="telegram", dir="in", from_="simon",
                type_="photo", msg=caption or "[photo]", caption=caption)

    prompt = (
        f"Simon sendte et bilde i chatten. Filen er lagret her: {img_path}\n"
        f"Bruk Read-verktøyet for å se på bildet og svar.\n"
    )
    if caption:
        prompt += f"Bildetekst fra Simon: {caption}\n"
    else:
        prompt += "Ingen bildetekst — beskriv hva du ser og spør om det trengs.\n"

    try:
        await _queue_and_process(
            chat_id,
            prompt,
            update,
            context,
            retry_payload={
                "kind": "photo",
                "prompt": prompt,
                "image_path": img_path,
                "caption": caption,
            },
        )
    finally:
        if not _failed_request_keeps_file(chat_id, img_path):
            try:
                os.unlink(img_path)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Voice message transcription (faster-whisper)
# ---------------------------------------------------------------------------

_whisper_model = None


def _get_whisper_model():
    """Load faster-whisper model on first use (lazy to avoid slow startup)."""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        log.info("Loading Whisper model (large-v3-turbo, int8_float32)... this may take a moment")
        _whisper_model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8_float32")
        log.info("Whisper model loaded")
    return _whisper_model


def transcribe_audio(audio_path: str) -> str:
    """Transcribe an audio file using faster-whisper (auto-detect language)."""
    model = _get_whisper_model()
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True,
        # Auto-detect language (no hardcoded "no") for mixed Norwegian/English
    )
    text = " ".join(seg.text for seg in segments).strip()
    log.info("Transcribed %s (lang=%s, prob=%.2f): %s",
             os.path.basename(audio_path), info.language,
             info.language_probability, text[:100])
    return text


@authorized
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Transcribe voice/audio messages and forward text to Claude."""
    chat_id = update.effective_chat.id
    sessions.touch_activity(_session_key(chat_id))

    try:
        await update.message.chat.send_action("typing")
    except TelegramError:
        pass

    voice = update.message.voice or update.message.audio
    if not voice:
        await _safe_reply(update.message, "Could not process audio.")
        return

    # Download to temp file
    voice_path = os.path.join(
        PROJECT_DIR, "memory",
        f".voice_{chat_id}_{voice.file_unique_id}.ogg"
    )
    try:
        tg_file = await context.bot.get_file(voice.file_id)
        await tg_file.download_to_drive(voice_path)
    except TelegramError as e:
        log.error("Failed to download voice file: %s", e)
        await _safe_reply(update.message, "Could not download voice message.")
        return

    try:
        # Show that we're processing the actual audio file
        dur = voice.duration or 0
        await _safe_reply(update.message,
                          f"\u23f3 Transkriberer lydfil ({dur}s) med Whisper large-v3-turbo...")

        # Transcribe in background thread (CPU-bound)
        text = await asyncio.get_running_loop().run_in_executor(
            None, lambda: transcribe_audio(voice_path)
        )

        if not text:
            await _safe_reply(update.message, "Kunne ikke transkribere (tomt resultat).")
            return

        # Log voice transcription
        log_message(ch="telegram", dir="in", from_="simon",
                    type_="voice", msg=text, transcription=text)

        # Show Whisper transcription (clearly labeled)
        await _safe_reply(update.message, f"\U0001f3a4 _Whisper:_ {text}")

        # Forward to Claude with voice context
        voice_prompt = f"[Stemmemelding fra Simon, transkribert med Whisper]: {text}"
        await _queue_and_process(chat_id, voice_prompt, update, context)

    except ImportError:
        await _safe_reply(
            update.message,
            "Voice transcription unavailable (faster-whisper not installed)."
        )
    except Exception as e:
        log.error("Voice handling error: %s", e)
        await _safe_reply(update.message,
                          "Could not process voice message. Try again.")
    finally:
        try:
            os.unlink(voice_path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@authorized
async def cmd_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/new — consolidate memory from current conversation, then start fresh."""
    chat_id = update.effective_chat.id
    key = _session_key(chat_id)
    engine, model = _resolve_engine_model()
    sessions.touch_activity(key)
    prev_session = sessions.get_previous_session(key, engine=engine)
    _log_command_request(update, command="new")

    if prev_session:
        await _reply_command(
            update,
            "Saving memory from this conversation...",
            command="new",
        )
        async with _claude_lock:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, lambda: consolidate_session(
                    prev_session, system_prompt=EA_SYSTEM_PROMPT,
                    session_manager=sessions, engine=engine,
                    model=model, session_key=key))
        if result.status == "failed":
            await _reply_command(
                update,
                "Kunne ikke bekrefte at memory ble lagret trygt. Jeg beholder samme samtale.",
                command="new",
            )
            return
    else:
        result = None

    session_id = sessions.reset_session(key, engine=engine)
    if result and result.changed_files:
        saved = ", ".join(path.replace("memory/", "") for path in result.changed_files)
        prefix = f"Lagret i {saved}. "
    elif result and result.status == "skipped":
        prefix = "Ingen viktig ny memory å lagre. "
    else:
        prefix = ""
    if session_id:
        await _reply_command(
            update,
            f"{prefix}Fresh conversation started ({engine} session {session_id[:8]}...)",
            command="new",
        )
    else:
        await _reply_command(
            update,
            f"{prefix}Fresh conversation started ({engine}).",
            command="new",
        )


@authorized
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/status — quick email + calendar status."""
    chat_id = update.effective_chat.id
    key = _session_key(chat_id)
    _log_command_request(update, command="status")
    prompt = (
        "Give me a quick status: how many unread emails do I have, "
        "and what's on my calendar for today? Be brief."
    )
    engine, resolved_model = _resolve_engine_model()
    sessions.touch_activity(key)
    try:
        await update.message.chat.send_action("typing")
    except TelegramError:
        pass
    async with sessions.get_lock(key):
        session_id, is_new = sessions.get_session(key, engine=engine)
        async with _claude_lock:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: run_assistant(
                    inject_runtime_context(
                        prompt,
                        _telegram_runtime_context(
                            chat_id,
                            purpose="Quick Telegram status check",
                        ),
                    ),
                    system_prompt=EA_SYSTEM_PROMPT,
                    engine=engine,
                    session_id=session_id, is_new_session=is_new,
                    session_manager=sessions,
                    session_key=key,
                    model=resolved_model,
                ),
            )
    if _is_engine_failure(response):
        _set_failed_request(chat_id, {"kind": "prompt", "prompt": prompt})
        response = _with_failure_guidance(response)
    else:
        _set_failed_request(chat_id, None)
    await _reply_command(update, response, command="status")


@authorized
async def cmd_inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/inbox — process inbox."""
    chat_id = update.effective_chat.id
    key = _session_key(chat_id)
    _log_command_request(update, command="inbox")
    prompt = (
        "Check my inbox. Show me unread emails that need attention, "
        "classify them by priority, and draft replies for anything "
        "urgent. Archive obvious noise."
    )
    engine, resolved_model = _resolve_engine_model()
    sessions.touch_activity(key)
    try:
        await update.message.chat.send_action("typing")
    except TelegramError:
        pass
    async with sessions.get_lock(key):
        session_id, is_new = sessions.get_session(key, engine=engine)
        async with _claude_lock:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: run_assistant(
                    inject_runtime_context(
                        prompt,
                        _telegram_runtime_context(
                            chat_id,
                            purpose="Telegram inbox triage",
                        ),
                    ),
                    system_prompt=EA_SYSTEM_PROMPT,
                    engine=engine,
                    session_id=session_id, is_new_session=is_new,
                    session_manager=sessions,
                    session_key=key,
                    model=resolved_model,
                ),
            )
    if _is_engine_failure(response):
        _set_failed_request(chat_id, {"kind": "prompt", "prompt": prompt})
        response = _with_failure_guidance(response)
    else:
        _set_failed_request(chat_id, None)
    await _reply_command(update, response, command="inbox")


PLAN_PROMPT_TEMPLATE = """\
The user wants you to PLAN (not implement) the following task:

{description}

YOUR JOB:
1. Explore the codebase to understand what exists
2. Identify the files, functions, and patterns relevant to this task
3. Design a step-by-step implementation plan
4. Write the plan to: {plan_file}

PLAN FORMAT (write to the file):
# Plan: [short title]

## What
[1-2 sentence summary of what will be done]

## Files to modify
[List of files with brief description of changes]

## Steps
1. [Step 1 — concrete, actionable]
2. [Step 2]
...

## Verification
[How to test that it works]

IMPORTANT:
- Do NOT implement anything. Only research and write the plan.
- Be specific — include function names, file paths, code patterns you found.
- After writing the plan file, respond with a SHORT summary of what you planned.
"""

EXECUTE_PROMPT_TEMPLATE = """\
Read the implementation plan at: {plan_file}

Execute the plan step by step. After completing each step, note what you did.
When done, respond with a summary of what was implemented and how to verify it works.

If the plan file doesn't exist or is empty, tell the user to run /plan first.
"""


@authorized
async def cmd_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/plan — research and write an implementation plan."""
    description = update.message.text.partition(" ")[2].strip()
    _log_command_request(update, command="plan")
    if not description:
        await _reply_command(
            update,
            "Usage: /plan <what you want to build>\n"
            "Example: /plan add a /remind command that schedules reminders",
            command="plan",
        )
        return

    chat_id = update.effective_chat.id
    key = _session_key(chat_id)
    sessions.touch_activity(key)

    await _reply_command(
        update,
        "Planning... I'll explore the codebase and write a plan.",
        command="plan",
    )

    prompt = PLAN_PROMPT_TEMPLATE.format(
        description=description,
        plan_file=ACTIVE_PLAN_FILE,
    )
    await _queue_and_process(chat_id, prompt, update, context)


def _find_newest_plan() -> str | None:
    """Find the newest plan file across both plan directories."""
    import glob as g
    candidates = []
    # 1. Project plan file (from /plan command)
    if os.path.exists(ACTIVE_PLAN_FILE):
        candidates.append(ACTIVE_PLAN_FILE)
    # 2. Claude Code plan files (from EnterPlanMode/ExitPlanMode)
    if os.path.isdir(CLAUDE_PLANS_DIR):
        for f in g.glob(os.path.join(CLAUDE_PLANS_DIR, "*.md")):
            # Skip agent sub-files (e.g. vectorized-mixing-prism-agent-xxx.md)
            if "-agent-" in os.path.basename(f):
                continue
            candidates.append(f)
    if not candidates:
        return None
    # Return the most recently modified
    return max(candidates, key=os.path.getmtime)


@authorized
async def cmd_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/execute — execute the newest plan (from /plan or plan mode)."""
    plan_file = _find_newest_plan()
    _log_command_request(update, command="execute")
    if not plan_file:
        await _reply_command(
            update,
            "No active plan found. Run /plan first.",
            command="execute",
        )
        return

    chat_id = update.effective_chat.id
    key = _session_key(chat_id)
    sessions.touch_activity(key)

    plan_name = os.path.basename(plan_file)
    await _reply_command(
        update,
        f"Executing plan: `{plan_name}`...",
        command="execute",
    )
    prompt = EXECUTE_PROMPT_TEMPLATE.format(plan_file=plan_file)
    await _queue_and_process(chat_id, prompt, update, context)


@authorized
async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/cancel — kill the running Claude process."""
    chat_id = update.effective_chat.id
    proc = _active_procs.get(chat_id)
    _log_command_request(update, command="cancel")
    if proc and proc.returncode is None:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
        await _reply_command(update, "Cancelled.", command="cancel")
        log.info("Cancelled Claude process for chat %s (pid %s)", chat_id, proc.pid)
    else:
        await _reply_command(update, "Nothing running to cancel.", command="cancel")


@authorized
async def cmd_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/context — show context window usage + memory breakdown."""
    chat_id = update.effective_chat.id
    key = _session_key(chat_id)
    engine, _ = _resolve_engine_model()
    _log_command_request(update, command="context")
    usage = _last_usage.get(_engine_usage_key(chat_id, engine))
    session_id, _ = sessions.get_session(key, engine=engine)
    session_label = session_id[:8] if session_id else "new"

    lines = []

    # --- Session token usage ---
    if usage:
        inp = usage.get("input_tokens", 0)
        out = usage.get("output_tokens", 0)
        cached = usage.get("cache_read_input_tokens", 0)
        cache_created = usage.get("cache_creation_input_tokens", 0)
        total = inp + out
        max_ctx = 200_000
        pct = (inp / max_ctx) * 100

        bar_len = 20
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)

        lines.append(f"📊 *Session {session_label} ({engine})*")
        lines.append(f"`[{bar}]` {pct:.1f}%")
        lines.append(f"Input: {inp:,} / 200k tokens")
        lines.append(f"Output: {out:,} tokens")
        if cached:
            lines.append(f"Cache read: {cached:,}")
        if cache_created:
            lines.append(f"Cache created: {cache_created:,}")
    else:
        lines.append(f"📊 *Session {session_label} ({engine})*")
        lines.append("No token data yet — send a message first.")

    # --- Memory files breakdown ---
    lines.append("")
    lines.append("📁 *Context surfaces*")

    memory_dir = os.path.join(PROJECT_DIR, "memory")
    rules_dir = os.path.join(PROJECT_DIR, ".claude", "rules")
    steering_md = os.path.join(
        PROJECT_DIR, "CLAUDE.md" if engine == ENGINE_CLAUDE else "AGENTS.md")
    soul_md = os.path.join(PROJECT_DIR, "SOUL.md")
    tasks_md = os.path.join(PROJECT_DIR, "TASKS.md")

    def _fsize(path):
        try:
            return os.path.getsize(path)
        except OSError:
            return 0

    def _dir_stats(dirpath, ext):
        """Return (file_count, total_bytes) for files with given extension."""
        count, total = 0, 0
        try:
            for f in os.listdir(dirpath):
                if f.endswith(ext):
                    count += 1
                    total += _fsize(os.path.join(dirpath, f))
        except OSError:
            pass
        return count, total

    def _fmt(b):
        if b < 1024:
            return f"{b} B"
        return f"{b / 1024:.1f} KB"

    def _est_tokens(b):
        return b // 4  # ~4 bytes per token rough estimate

    # Auto-loaded every turn (engine steering + rules) plus runtime-loaded SOUL.md
    steering_sz = _fsize(steering_md)
    soul_sz = _fsize(soul_md)
    rules_count, rules_sz = _dir_stats(rules_dir, ".md")
    auto_total = steering_sz + rules_sz + soul_sz
    steering_label = os.path.basename(steering_md)
    lines.append(
        f"{steering_label} + SOUL.md + {rules_count} rules: "
        f"{_fmt(auto_total)} (~{_est_tokens(auto_total):,} tok)"
    )

    # Selective memory files
    memory_sz = _fsize(os.path.join(memory_dir, "MEMORY.md"))
    state_sz = _fsize(os.path.join(memory_dir, "STATE.md"))
    summary_sz = _fsize(os.path.join(memory_dir, "SUMMARY.md"))
    history_sz = _fsize(os.path.join(memory_dir, "HISTORY.md"))
    active_threads_sz = _fsize(os.path.join(memory_dir, "ACTIVE_THREADS.md"))
    tasks_sz = _fsize(tasks_md)

    # Daily summaries
    sum_count, sum_sz = _dir_stats(os.path.join(memory_dir, "summaries"), ".md")

    # Conversation logs
    conv_count, conv_sz = _dir_stats(os.path.join(memory_dir, "conversations"), ".jsonl")
    lines.append(f"Lastes eksplisitt hver turn: ~{_est_tokens(auto_total):,} tok")
    lines.append(f"_(steering + rules + SOUL = {_fmt(auto_total)})_")

    lines.append("")
    lines.append("*Selektivt tilgjengelig ved behov*")
    lines.append(f"MEMORY.md (durable): {_fmt(memory_sz)} (~{_est_tokens(memory_sz):,} tok)")
    lines.append(f"STATE.md (operativt): {_fmt(state_sz)} (~{_est_tokens(state_sz):,} tok)")
    lines.append(f"SUMMARY.md (bakgrunn): {_fmt(summary_sz)} (~{_est_tokens(summary_sz):,} tok)")
    lines.append(f"HISTORY.md: {_fmt(history_sz)}")
    lines.append(f"ACTIVE_THREADS.md: {_fmt(active_threads_sz)}")
    lines.append(f"TASKS.md: {_fmt(tasks_sz)}")
    lines.append(f"Daglige oppsummeringer: {sum_count} filer, {_fmt(sum_sz)}")
    lines.append(f"Samtalelogger: {conv_count} filer, {_fmt(conv_sz)}")
    lines.append("Rå samtalelogger lastes ikke automatisk; bruk grep ved behov.")

    # Warnings
    if usage:
        pct = (usage.get("input_tokens", 0) / 200_000) * 100
        if pct > 80:
            lines.append("\n⚠️ Context nesten full. Vurder /new.")
        elif pct > 50:
            lines.append("\n⚡ Over halvveis.")

    await _reply_command(update, "\n".join(lines), command="context")


@authorized
async def cmd_usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/usage — show 5h + weekly usage remaining."""
    chat_id = update.effective_chat.id
    engine, _ = _resolve_engine_model()
    _log_command_request(update, command="usage")
    lines = [f"📈 *Usage ({engine})*"]

    if engine == ENGINE_CLAUDE:
        data, err = await _fetch_claude_usage_windows()
        if err:
            lines.append(f"Claude usage utilgjengelig: {err}")
        else:
            line_5h = _format_window_line("5h", data.get("five_hour"))
            line_7d = _format_window_line("7d", data.get("seven_day"))
            if line_5h:
                lines.append(line_5h)
            if line_7d:
                lines.append(line_7d)
            if not line_5h and not line_7d:
                lines.append("Fant ingen 5h/7d usage-felter i responsen.")
    else:
        usage_key = _engine_usage_key(chat_id, ENGINE_CODEX)
        rate_limits = _last_rate_limits.get(usage_key)
        if not rate_limits:
            rate_limits, err = _fetch_codex_rate_limits_from_sessions()
            if err:
                lines.append(f"Codex usage utilgjengelig: {err}")
        if rate_limits:
            _last_rate_limits[usage_key] = rate_limits
            lines.extend(_format_codex_usage_lines(rate_limits))
        elif len(lines) == 1:
            lines.extend(_format_codex_usage_lines(None))

    await _reply_command(update, "\n".join(lines), command="usage")


@authorized
async def cmd_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/topics — show recent shared relay topics or details for one topic."""
    args = context.args or []
    _log_command_request(update, command="topics")
    if args:
        topic = find_shared_topic_by_prefix(args[0])
        if not topic:
            await _reply_command(
                update,
                f"Fant ingen topic som matcher '{args[0]}'.",
                command="topics",
            )
            return

        lines = [
            f"🧠 *Topic {topic['id']}*",
            f"Status: {topic.get('status', 'ukjent')}",
            f"Oppdatert: {topic.get('updated_at', 'ukjent')}",
        ]
        participants = topic.get("participants") or []
        if participants:
            lines.append(f"Deltakere: {', '.join(participants)}")
        lines.append(f"Summary: {topic.get('summary', 'ingen')}")

        question = topic.get("latest_question")
        if question:
            lines.append(f"Siste spørsmål: {question}")
        answer = topic.get("latest_answer")
        if answer:
            lines.append(f"Siste svar: {answer}")

        links = topic.get("links") or {}
        slack_threads = links.get("slack_threads") or []
        telegram_chats = links.get("telegram_chats") or []
        if slack_threads:
            ref = slack_threads[0]
            lines.append(
                f"Slack: {ref.get('channel', '?')} / {ref.get('thread_ts') or 'ingen tråd'}"
            )
        if telegram_chats:
            ref = telegram_chats[0]
            lines.append(f"Telegram: {ref.get('chat_id', '?')}")
        await _reply_command(update, "\n".join(lines), command="topics")
        return

    topics = get_recent_shared_topics(limit=8)
    if not topics:
        await _reply_command(update, "Ingen shared topics ennå.", command="topics")
        return

    lines = ["🧠 *Siste shared topics*"]
    for topic in topics:
        short_id = topic.get("id", "topic")[:18]
        status = topic.get("status", "ukjent")
        summary = topic.get("summary", "")
        if len(summary) > 110:
            summary = summary[:109] + "…"
        lines.append(f"`{short_id}` · {status}")
        if summary:
            lines.append(summary)
    lines.append("\nDetaljer: `/topics <id-prefix>`")
    await _reply_command(update, "\n".join(lines), command="topics")


@authorized
async def cmd_research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/research — research a topic using Sonnet (faster, cheaper)."""
    query = update.message.text.partition(" ")[2].strip()
    _log_command_request(update, command="research")
    if not query:
        await _reply_command(
            update,
            "Usage: /research <question>\n"
            "Example: /research what auth libraries work best with FastAPI",
            command="research",
        )
        return

    chat_id = update.effective_chat.id
    key = _session_key(chat_id)
    engine, _ = _resolve_engine_model()
    sessions.touch_activity(key)

    if engine == ENGINE_CLAUDE:
        await _reply_command(update, "Researching (Sonnet)...", command="research")
        model_override = "sonnet"
    else:
        await _reply_command(update, "Researching...", command="research")
        model_override = None

    await _queue_and_process(chat_id, query, update, context,
                             model=model_override)


@authorized
async def cmd_engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/engine — show or switch global assistant engine."""
    chat_id = update.effective_chat.id
    args = context.args or []
    _log_command_request(update, command="engine")

    if not args:
        state = get_engine_state()
        current = state["engine"]
        c_model = state["models"].get(ENGINE_CLAUDE) or "(default)"
        x_model = state["models"].get(ENGINE_CODEX) or "(default)"
        await _reply_command(
            update,
            "Assistant engine (global):\n"
            f"- current: {current}\n"
            f"- {ENGINE_CLAUDE} model: {c_model}\n"
            f"- {ENGINE_CODEX} model: {x_model}\n\n"
            "Switch examples:\n"
            "/engine claude\n"
            "/engine codex\n"
            "/engine codex gpt-5.4\n"
            "/engine claude default",
            command="engine",
        )
        return

    engine = args[0].strip().lower()
    if engine not in {ENGINE_CLAUDE, ENGINE_CODEX}:
        await _reply_command(
            update,
            "Usage: /engine <claude|codex> [model]",
            command="engine",
        )
        return

    try:
        if len(args) >= 2:
            raw_model = " ".join(args[1:]).strip()
            if raw_model.lower() in {"default", "none", "-"}:
                model_value = None
            else:
                model_value = raw_model
            state = set_engine_state(
                engine, model=model_value, updated_by=f"telegram:{chat_id}")
        else:
            state = set_engine_state(
                engine, updated_by=f"telegram:{chat_id}")
    except ValueError as e:
        await _reply_command(update, str(e), command="engine")
        return

    current = state["engine"]
    c_model = state["models"].get(ENGINE_CLAUDE) or "(default)"
    x_model = state["models"].get(ENGINE_CODEX) or "(default)"
    await _reply_command(
        update,
        "Updated assistant engine:\n"
        f"- current: {current}\n"
        f"- {ENGINE_CLAUDE} model: {c_model}\n"
        f"- {ENGINE_CODEX} model: {x_model}",
        command="engine",
    )


@authorized
async def cmd_retry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/retry — retry last failed prompt."""
    chat_id = update.effective_chat.id
    payload = _last_failed_request.get(chat_id)
    _log_command_request(update, command="retry")
    if not payload:
        await _reply_command(update, "No failed request to retry.", command="retry")
        return

    sessions.touch_activity(_session_key(chat_id))
    if payload.get("kind") == "photo" and not os.path.exists(payload.get("image_path", "")):
        _set_failed_request(chat_id, None)
        await _reply_command(
            update,
            "Bildet fra forrige feilede forespørsel finnes ikke lenger. Send det på nytt.",
            command="retry",
        )
        return

    await _reply_command(update, "Retrying last failed request...", command="retry")
    await _queue_and_process(
        chat_id,
        payload["prompt"],
        update,
        context,
        retry_payload=payload,
    )


@authorized
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help — list available commands."""
    _log_command_request(update, command="help")
    text = (
        "Available commands:\n\n"
        "/help — show this list\n"
        "/new — start a fresh conversation (saves memory first)\n"
        "/status — quick email + calendar overview\n"
        "/inbox — process and triage inbox\n"
        "/plan <task> — research and write an implementation plan\n"
        "/execute — execute the active plan\n"
        "/research <question> — research a topic (Sonnet, faster)\n"
        "/engine — show/switch assistant engine\n"
        "/retry — retry last failed request\n"
        "/cancel — stop the running task\n"
        "/usage — show 5h + weekly usage remaining\n"
        "/context — show context window usage\n"
        "/topics — show shared relay topics\n"
        "/heartbeat — manually check for new emails\n"
        "\nYou can also just send a regular message and I'll handle it."
    )
    await _reply_command(update, text, command="help")


@authorized
async def cmd_heartbeat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/heartbeat — manually trigger the heartbeat check."""
    sessions.touch_activity(_session_key(update.effective_chat.id))
    _log_command_request(update, command="heartbeat")
    try:
        await update.message.chat.send_action("typing")
    except TelegramError:
        pass
    await _reply_command(update, "Checking emails...", command="heartbeat")
    await run_heartbeat_triage(bot=context.bot)


# ---------------------------------------------------------------------------
# Heartbeat — proactive email/calendar check
# ---------------------------------------------------------------------------

HEARTBEAT_TRIAGE_PROMPT = """\
Check Emma's inbox (emma@vibelabs.no) for new unread emails.

⛔ ACCOUNT RESTRICTION: ONLY check and act on emma@vibelabs.no.
DO NOT read, archive, modify, or touch ANY other email account.
Never access simonstrumse@gmail.com, simon@vibelabs.no, hello@vibelabs.no, or oslo@seaexperience.no during heartbeat.

FOR EACH UNREAD EMAIL in emma@vibelabs.no:
- Check ACTIVE_THREADS.md for thread-specific auto-reply instructions.
- If you can handle it (scheduling, info requests, simple questions): reply as Emma.
- If it's sensitive, private, financial, or unsure: note it for Simon.
- You have READ access to Simon's calendar, contacts, and email history for context.

RESPONSE:
- If NOTHING needs attention: respond with exactly HEARTBEAT_SKIP
- If something IS noteworthy: write a brief summary.
  Group by: \u2705 Handled \u2192 \u27a1\ufe0f Forwarded to Simon \u2192 \u2753 Needs your input.
  Keep under 300 words.
"""


HEARTBEAT_SESSION_KEY = "heartbeat:emma-vibelabs"
HEARTBEAT_MAX_AGE_HOURS = 24


def _heartbeat_session_age() -> float:
    """Return age of heartbeat session in hours (based on last activity)."""
    last = sessions._last_activity.get(HEARTBEAT_SESSION_KEY)
    if not last:
        return float('inf')
    return (datetime.now() - last).total_seconds() / 3600


async def run_heartbeat_triage(bot=None) -> None:
    """Run heartbeat triage with a persistent session.

    Uses a dedicated session that persists across runs so the heartbeat
    remembers what it already handled. Auto-resets after 24h.
    Acquires the global Claude lock to prevent project-lock contention.
    """
    # Check if assistant is already running — skip rather than block
    if _claude_lock.locked():
        log.info("Heartbeat: skipping — assistant process already running")
        return

    engine, resolved_model = _resolve_engine_model()
    async with _claude_lock:
        session_id, is_new = sessions.get_session(
            HEARTBEAT_SESSION_KEY, engine=engine)

        # Auto-reset stale heartbeat sessions
        if not is_new and _heartbeat_session_age() > HEARTBEAT_MAX_AGE_HOURS:
            log.info("Heartbeat: session older than %dh, consolidating and resetting",
                     HEARTBEAT_MAX_AGE_HOURS)
            prev_session = sessions.get_previous_session(
                HEARTBEAT_SESSION_KEY, engine=engine)
            if prev_session:
                loop = asyncio.get_running_loop()
                consolidation = await loop.run_in_executor(
                    None, lambda: consolidate_session(
                        prev_session, system_prompt=EMAIL_SPECIALIST_PROMPT,
                        session_manager=sessions, engine=engine,
                        model=resolved_model, session_key=HEARTBEAT_SESSION_KEY))
                if consolidation.status == "failed":
                    log.warning(
                        "Heartbeat: consolidation failed, keeping existing session %s",
                        prev_session[:8],
                    )
                else:
                    session_id = sessions.reset_session(
                        HEARTBEAT_SESSION_KEY, engine=engine)
                    is_new = True
            else:
                session_id = sessions.reset_session(
                    HEARTBEAT_SESSION_KEY, engine=engine)
                is_new = True

        sessions.touch_activity(HEARTBEAT_SESSION_KEY)
        dbg.info("HEARTBEAT | engine=%s | session=%s (%s)",
                 engine, (session_id[:8] if session_id else "new"),
                 "new" if is_new else "resume")

        # Must pass a callback to force streaming mode (not blocking run_in_executor)
        # so the asyncio _claude_lock is held for the entire duration.
        async def _heartbeat_progress(msg: str) -> None:
            log.info("Heartbeat: %s", msg)

        triage = await run_assistant_streaming(
            inject_runtime_context(
                HEARTBEAT_TRIAGE_PROMPT,
                build_runtime_context(
                    channel="heartbeat",
                    chat_id=HEARTBEAT_SESSION_KEY,
                    session_key=HEARTBEAT_SESSION_KEY,
                    purpose="Unread email triage for emma@vibelabs.no",
                ),
            ),
            system_prompt=EMAIL_SPECIALIST_PROMPT,
            engine=engine,
            session_id=session_id,
            is_new_session=is_new,
            session_manager=sessions,
            session_key=HEARTBEAT_SESSION_KEY,
            progress_callback=_heartbeat_progress,
            model=resolved_model,
        )

    if "HEARTBEAT_SKIP" in triage:
        log.info("Heartbeat: nothing noteworthy")
        return

    # Don't forward timeout messages to chat — they're noise, not results
    if "timed out" in triage.lower():
        log.warning("Heartbeat: triage timed out, not forwarding: %s",
                     triage[:200])
        return

    log_message(ch="telegram", dir="out", from_="emma",
                type_="heartbeat", msg=triage)

    log.info("Heartbeat: something noteworthy, notifying")
    if bot:
        for chat_id in ALLOWED_CHAT_IDS:
            _save_heartbeat_outbound(chat_id, triage)
            await _safe_send(bot, chat_id, triage)
            log.info("Heartbeat: notification sent to chat %s", chat_id)


# ---------------------------------------------------------------------------
# Cross-channel relay: Slack → Telegram → Slack
# ---------------------------------------------------------------------------
RELAY_POLL_INTERVAL = 5  # seconds


async def cmd_relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /relay <id_prefix> <answer> — answer a Slack relay."""
    if update.effective_chat.id not in ALLOWED_CHAT_IDS:
        return
    _log_command_request(update, command="relay")

    args = context.args or []
    if len(args) < 2:
        await _reply_command(
            update,
            "Bruk: /relay <id> <svar>\n"
            "Eksempel: /relay abc123 Ja, 9. mars funker",
            command="relay",
        )
        return

    id_prefix = args[0]
    answer = " ".join(args[1:])

    relay = find_relay_by_prefix(id_prefix)
    if not relay:
        await _reply_command(
            update,
            f"Fant ingen relay med ID som starter med '{id_prefix}'.",
            command="relay",
        )
        return

    if relay.get("status") not in ("forwarded", "pending"):
        await _reply_command(
            update,
            f"Relay {id_prefix} er allerede besvart.",
            command="relay",
        )
        return

    mark_answered(
        relay["id"],
        answer,
        answered_in_context={"chat_id": str(update.effective_chat.id)},
    )
    await _reply_command(
        update,
        f"✅ Svar sendt tilbake til {relay['from_user']} på Slack.",
        command="relay",
    )

    log_message(ch="telegram", dir="in", from_="simon",
                msg=f"/relay {id_prefix} {answer}", type_="relay_answer")


async def _poll_relay_requests(bot) -> None:
    """Poll for pending relays and forward them to Simon on Telegram."""
    await asyncio.sleep(15)  # Wait for bot to fully start
    log.info("Relay request poller started (interval=%ds)", RELAY_POLL_INTERVAL)

    while True:
        try:
            pending = get_relays(status="pending")
            for relay in pending:
                short_id = relay["id"][:8]
                from_user = relay.get("from_user", "noen")
                from_channel = relay.get("from_channel", "?")
                message = relay.get("message", "")

                text = (f"📨 *Relay fra {from_user} ({from_channel}):*\n\n"
                        f"{message}\n\n"
                        f"_Svar:_ `/relay {short_id} <ditt svar>`")

                for chat_id in ALLOWED_CHAT_IDS:
                    await _safe_send(bot, chat_id, text)

                mark_forwarded(relay["id"])
                log.info("relay: forwarded %s to Telegram from %s/%s",
                         short_id, from_channel, from_user)

                log_message(ch="telegram", dir="out", from_="emma",
                            msg=text, type_="relay_forward")

            # Periodic cleanup
            relay_cleanup(max_age_hours=48)
        except Exception as e:
            log.warning("relay: poll error: %s", e)

        await asyncio.sleep(RELAY_POLL_INTERVAL)


# ---------------------------------------------------------------------------
# Session migration helper
# ---------------------------------------------------------------------------

def _migrate_sessions_if_needed() -> None:
    """Migrate from old .sessions.json (int keys) to new format (str keys)."""
    old_file = os.path.join(PROJECT_DIR, "memory", ".sessions.json")
    if os.path.exists(old_file) and not os.path.exists(SESSIONS_FILE):
        try:
            with open(old_file) as f:
                old_data = json.load(f)
            new_data = {
                "version": 2,
                "chat_sessions": {
                    f"tg:{k}": {"claude": v}
                    for k, v in old_data.get("chat_sessions", {}).items()
                },
                "created_sessions": {
                    "claude": old_data.get("created_sessions", []),
                    "codex": [],
                },
            }
            os.makedirs(os.path.dirname(SESSIONS_FILE), exist_ok=True)
            with open(SESSIONS_FILE, "w") as f:
                json.dump(new_data, f, indent=2)
            log.info("Migrated sessions from %s to %s", old_file, SESSIONS_FILE)
        except Exception as e:
            log.warning("Failed to migrate sessions: %s", e)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def _handle_queued_task(task) -> None:
    """Task queue consumer handler — dispatches tasks by type."""
    if task.task_type == "heartbeat_triage":
        bot = task.payload.get("bot")
        await run_heartbeat_triage(bot=bot)
    else:
        log.warning("Unknown task type: %s", task.task_type)


def _cleanup_orphaned_processes():
    """Kill orphaned Claude child processes from previous bot sessions.

    When the bot restarts, Bash→Python subprocesses spawned by old Claude
    processes can survive as orphans. This finds and kills them.
    """
    import signal
    our_pid = os.getpid()
    bot_pids = set()
    # Find our own PID to avoid killing ourselves
    bot_pids.add(our_pid)

    killed = 0
    try:
        import subprocess as sp
        # Find zombie python processes running claude_mail/email_service scripts
        # that have init (PID 1) or launchd as parent (orphaned)
        result = sp.run(
            ["pgrep", "-f", "claude_mail|email_service|EmailService"],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            for pid_str in result.stdout.strip().split("\n"):
                pid = int(pid_str)
                if pid == our_pid:
                    continue
                # Check if this is an orphaned process (parent is 1/launchd)
                try:
                    ppid_result = sp.run(
                        ["ps", "-p", str(pid), "-o", "ppid="],
                        capture_output=True, text=True, timeout=2
                    )
                    ppid = int(ppid_result.stdout.strip())
                    # Parent is init/launchd (1) or gone — it's orphaned
                    if ppid == 1:
                        os.kill(pid, signal.SIGKILL)
                        killed += 1
                except (ValueError, ProcessLookupError, PermissionError):
                    pass
    except Exception as e:
        log.debug("Orphan cleanup error (non-fatal): %s", e)

    if killed:
        log.info("Cleaned up %d orphaned process(es) from previous session", killed)


def main():
    global task_queue, watcher

    log.info("Starting Telegram bot bridge for Claude Code EA")
    log.info("Project dir: %s", PROJECT_DIR)

    integrity = prepare_runtime_environment()
    if integrity.created_files:
        log.info("Runtime bootstrap created: %s",
                 ", ".join(integrity.created_files))
    if integrity.drift:
        raise RuntimeError(
            "Startup integrity check failed: " + "; ".join(integrity.drift)
        )

    # Clean up orphaned processes from previous bot sessions
    _cleanup_orphaned_processes()

    # Migrate old sessions file if needed, then load
    _migrate_sessions_if_needed()
    sessions.load()

    # Initialize task queue and watcher
    task_queue = TaskQueue()
    watcher = HeartbeatWatcher(task_queue)

    async def post_init(application):
        await application.bot.set_my_commands([
            BotCommand("help", "Show available commands"),
            BotCommand("new", "Start a fresh conversation"),
            BotCommand("status", "Quick email + calendar overview"),
            BotCommand("inbox", "Process and triage inbox"),
            BotCommand("plan", "Research and write an implementation plan"),
            BotCommand("execute", "Execute the active plan"),
            BotCommand("research", "Research a topic (Sonnet, faster)"),
            BotCommand("engine", "Show or switch assistant engine"),
            BotCommand("retry", "Retry the last failed request"),
            BotCommand("cancel", "Stop the running task"),
            BotCommand("usage", "Show 5h + weekly usage remaining"),
            BotCommand("context", "Show context window usage"),
            BotCommand("topics", "Show shared relay topics"),
            BotCommand("heartbeat", "Check for new emails"),
            BotCommand("relay", "Answer a Slack relay"),
        ])

        # Inject bot reference into watcher tasks so heartbeat can send messages
        original_enqueue = task_queue.enqueue

        def _enqueue_with_bot(priority, task_type, **payload):
            if task_type == "heartbeat_triage":
                payload["bot"] = application.bot
            original_enqueue(priority, task_type, **payload)

        task_queue.enqueue = _enqueue_with_bot

        # Start background tasks: queue consumer + watcher loop
        _bg_tasks.append(asyncio.create_task(
            task_queue.start_consumer(_handle_queued_task)))
        _bg_tasks.append(asyncio.create_task(watcher.run_loop()))
        _bg_tasks.append(asyncio.create_task(
            _poll_relay_requests(application.bot)))
        _bg_tasks.append(asyncio.create_task(
            _gemini3_probe_loop(application.bot)))
        log.info("Task queue consumer, watcher, relay poller, and Gemini probe started")

    async def pre_shutdown(application):
        """Cancel background tasks cleanly on shutdown."""
        for t in _bg_tasks:
            t.cancel()
        _bg_tasks.clear()

    _bg_tasks: list[asyncio.Task] = []
    app = (ApplicationBuilder().token(BOT_TOKEN)
           .post_init(post_init)
           .post_shutdown(pre_shutdown)
           .build())

    # Commands
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("new", cmd_new))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("inbox", cmd_inbox))
    app.add_handler(CommandHandler("plan", cmd_plan))
    app.add_handler(CommandHandler("execute", cmd_execute))
    app.add_handler(CommandHandler("research", cmd_research))
    app.add_handler(CommandHandler("engine", cmd_engine))
    app.add_handler(CommandHandler("retry", cmd_retry))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CommandHandler("usage", cmd_usage))
    app.add_handler(CommandHandler("context", cmd_context))
    app.add_handler(CommandHandler("topics", cmd_topics))
    app.add_handler(CommandHandler("heartbeat", cmd_heartbeat))
    app.add_handler(CommandHandler("relay", cmd_relay))

    # Photos -> Save to disk + let Claude see them
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Voice/audio messages -> Transcribe + Claude Code
    app.add_handler(MessageHandler(
        filters.VOICE | filters.AUDIO, handle_voice))

    # All other text messages -> Claude Code
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    log.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
