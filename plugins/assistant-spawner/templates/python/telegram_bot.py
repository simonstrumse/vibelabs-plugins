#!/usr/bin/env python3
"""Telegram bot that bridges messages to Claude Code running in the Assistent project."""

import asyncio
import functools
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
from task_queue import TaskQueue, P_WATCHER
from heartbeat import (
    HEARTBEAT_INTERVAL_SECONDS,
    HEARTBEAT_STARTUP_DELAY_SECONDS,
    _load_heartbeat_checklist,
    _is_heartbeat_ok,
    build_heartbeat_prompt,
)
from runtime_support import (
    build_runtime_context,
    compose_system_prompt,
    inject_runtime_context,
    prepare_runtime_environment,
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
ALLOWED_CHAT_IDS = {[OWNER_TELEGRAM_ID]}  # Owner's Telegram user ID
ACTIVE_PLAN_FILE = os.path.join(PROJECT_DIR, ".claude", "plans", "active-telegram-plan.md")
CLAUDE_PLANS_DIR = os.path.expanduser("~/.claude/plans")

# Session manager (separate file from Slack)
SESSIONS_FILE = os.path.join(PROJECT_DIR, "memory", ".sessions-telegram.json")
sessions = SessionManager(SESSIONS_FILE)

# Task queue (initialized in main)
task_queue: TaskQueue | None = None

# Global lock for all assistant subprocess calls.
_claude_lock = asyncio.Lock()

# Track active Claude subprocess per chat for /cancel
_active_procs: dict[int, asyncio.subprocess.Process] = {}

# Track last known token usage per session key for /context
_last_usage: dict[str, dict] = {}

# Track last failed request per chat for /retry
_last_failed_request: dict[int, dict] = {}

CLAUDE_USAGE_SCRIPT = os.path.join(
    PROJECT_DIR, "scripts", "fetch_claude_usage_windows.swift")


def _is_engine_failure(text: str) -> bool:
    if not text:
        return False
    checks = (
        "Error: Claude binary not found",
        "Claude timed out",
        "Something went wrong. Check the logs or try again.",
    )
    return any(marker in text for marker in checks)


def _with_failure_guidance(text: str) -> str:
    return (
        text.rstrip()
        + "\n\nTry this:\n"
        + "/retry\n"
        + "/new"
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
        from_="owner",
        msg=text,
        type_="command",
        command=command or _command_name(text),
    )


async def _reply_command(update: Update, text: str, *, command: str) -> None:
    await _safe_reply(update.message, text)
    log_message(
        ch="telegram",
        dir="out",
        from_="assistant",
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

# System prompt that shapes Claude's behavior when running as a Telegram EA.
# CLAUDE.md (loaded automatically from the project dir) provides API docs and
# tools. This prompt tells Claude *how to act* as an executive assistant.
EA_SYSTEM_PROMPT = compose_system_prompt("""\
You ARE [ASSISTANT_FULL_NAME], [OWNER_FULL_NAME]'s executive assistant. \
You speak as [ASSISTANT_NAME] — first person, never third person. Operating via Telegram.

SYSTEMS YOU MANAGE:
- Calendar, Drive, Docs, Sheets, Contacts, Tasks (via GoogleServices)
- Telegram: this chat (telegram_bot.py)

PERSONALITY:
- Communicate like [OWNER_NAME]: direct, brief, [DEFAULT_LANGUAGE] by default, English when needed.
- Keep Telegram messages short. Use bullet points, not paragraphs.
- Don't explain what you're doing — just do it and report results.

AUTONOMY RULES:
- You CAN: check calendar, search, create drafts, update TASKS.md, \
check on existing tasks, research, browse the web, manage files.
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

CONVERSATION HISTORY (3-layer system):
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
        return "unknown"
    try:
        if isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(float(value))
        elif isinstance(value, str):
            raw = value.strip()
            if not raw:
                return "unknown"
            if raw.endswith("Z"):
                raw = raw[:-1] + "+00:00"
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is not None:
                dt = dt.astimezone()
        else:
            return "unknown"
        return dt.strftime("%a %H:%M")
    except (TypeError, ValueError, OSError):
        return "unknown"


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
    return f"{label}: {used:.0f}% used · {left:.0f}% remaining · resets {reset_at}"


async def _fetch_claude_usage_windows() -> tuple[dict | None, str | None]:
    """Fetch Claude 5h/7d usage windows via local Swift helper."""
    if not os.path.isfile(CLAUDE_USAGE_SCRIPT):
        return None, "usage script missing"

    try:
        proc = await asyncio.create_subprocess_exec(
            "swift", CLAUDE_USAGE_SCRIPT,
            cwd=PROJECT_DIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        return None, "swift not installed"
    except OSError:
        return None, "could not start usage script"

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=20)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return None, "timeout fetching usage"

    out = stdout.decode("utf-8", errors="replace").strip()
    err = stderr.decode("utf-8", errors="replace").strip()

    if proc.returncode != 0:
        if err:
            return None, err.splitlines()[-1][:140]
        if out:
            return None, out.splitlines()[-1][:140]
        return None, "unknown error from usage script"

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return None, "invalid usage format"

    if not isinstance(data, dict):
        return None, "invalid usage format"
    return data, None


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
        log_message(ch="telegram", dir="in", from_="owner", msg=combined)

        session_id, is_new = sessions.get_session(key)
        sessions.touch_activity(key)  # Mark active during processing (not just on message receive)
        sid_preview = (session_id[:8] if session_id else "new")
        log.info("Processing for %s (session %s, %s): %s",
                 chat_id, sid_preview, "new" if is_new else "resume",
                 combined[:100])
        dbg.info("MSG_IN | chat=%s | session=%s (%s) | msg=%s",
                 chat_id, sid_preview, "new" if is_new else "resume",
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

            # Translate technical tool names to friendly status
            _STATUS_MAP = {
                "Running: Bash": "Running a command",
                "Running: Read": "Reading files",
                "Running: Write": "Writing something",
                "Running: Edit": "Making an edit",
                "Running: Grep": "Searching the codebase",
                "Running: Glob": "Looking for files",
                "Running: WebFetch": "Fetching from the web",
                "Running: WebSearch": "Searching the web",
                "Running: TaskOutput": "Waiting for a result",
                "Running: Task": "Delegating to specialist...",
                "Running: Skill": "Using a skill",
                "Running: NotebookEdit": "Writing in notebook",
                "Running: ToolSearch": "Finding the right tool",
                "Running: TodoWrite": "Noting a to-do",
                "Running: TodoRead": "Checking the to-do list",
                "Running: TaskCreate": "Creating a task",
                "Running: TaskUpdate": "Updating task list",
                "Running: TaskList": "Checking tasks",
            }
            # Prefix-based matching for MCP tools (mcp__service__action)
            _MCP_PREFIX = {
                "mcp__claude-in-chrome__": "Controlling the browser",
                "mcp__Neon__": "Querying the database",
            }
            friendly = _STATUS_MAP.get(status)
            if not friendly and status.startswith("Running: "):
                tool_name = status[len("Running: "):]
                # Check MCP prefix matches
                for prefix, msg in _MCP_PREFIX.items():
                    if tool_name.startswith(prefix):
                        friendly = msg
                        break
                if not friendly:
                    friendly = "Working on it"
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
            sessions.touch_activity(key)  # Mark active during streaming
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

        usage_key = _session_key(chat_id)

        def _store_usage(usage):
            _last_usage[usage_key] = usage

        # Acquire global Claude lock — only one Claude process at a time
        # (project-level lock in Claude Code prevents concurrent subprocesses)
        _t_lock_wait = time.time()
        if _claude_lock.locked():
            log.info("Message from %s waiting for lock (another task running)", chat_id)
            dbg.info("LOCK_WAIT | chat=%s | lock is held", chat_id)
            await _safe_send(bot, chat_id, "\u23f3 Hold on, working on something else first...")
        async with _claude_lock:
            _t_lock_acquired = time.time()
            _t_lock_ms = int((_t_lock_acquired - _t_lock_wait) * 1000)
            if _t_lock_ms > 100:
                dbg.info("LOCK_ACQUIRED | waited %dms", _t_lock_ms)

            _claude_prompt = inject_runtime_context(
                combined,
                _telegram_runtime_context(
                    chat_id,
                    purpose="Direct Telegram chat with [OWNER_NAME]",
                ),
            )

            _t_claude_start = time.time()
            try:
                response = await run_assistant_streaming(
                    _claude_prompt,
                    system_prompt=EA_SYSTEM_PROMPT,
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
                    model=model,
                )
            finally:
                _active_procs.pop(chat_id, None)
                _t_claude_end = time.time()
                _t_total_ms = int((_t_claude_end - _t_claude_start) * 1000)
                dbg.info("TIMING | run=%dms (%.1fs) | chat=%s",
                         _t_total_ms, _t_total_ms / 1000, chat_id)
        current_sid, _ = sessions.get_session(key)
        _sid = current_sid[:8] if current_sid else ""
        _engine_error = _is_engine_failure(response)

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
        sessions.reset_by_session_id(current_sid)
        _set_failed_request(chat_id, failed_payload)
        response = (
            "Sorry, something went wrong — the session was corrupt and has been reset.\n"
            "Resend your message and it should work."
        )

    if _engine_error:
        _set_failed_request(chat_id, failed_payload)
        response = _with_failure_guidance(response)
    else:
        _set_failed_request(chat_id, None)

    if response:
        log_message(ch="telegram", dir="out", from_="assistant", msg=response, sid=_sid)

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
    log_message(ch="telegram", dir="in", from_="owner",
                type_="photo", msg=caption or "[photo]", caption=caption)

    prompt = (
        f"[OWNER_NAME] sent an image in the chat. The file is saved here: {img_path}\n"
        f"Use the Read tool to view the image and respond.\n"
    )
    if caption:
        prompt += f"Caption from [OWNER_NAME]: {caption}\n"
    else:
        prompt += "No caption — describe what you see and ask if needed.\n"

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
                          f"\u23f3 Transcribing audio ({dur}s) with Whisper large-v3-turbo...")

        # Transcribe in background thread (CPU-bound)
        text = await asyncio.get_running_loop().run_in_executor(
            None, lambda: transcribe_audio(voice_path)
        )

        if not text:
            await _safe_reply(update.message, "Could not transcribe (empty result).")
            return

        # Log voice transcription
        log_message(ch="telegram", dir="in", from_="owner",
                    type_="voice", msg=text, transcription=text)

        # Show Whisper transcription (clearly labeled)
        await _safe_reply(update.message, f"\U0001f3a4 _Whisper:_ {text}")

        # Forward to Claude with voice context
        voice_prompt = f"[Voice message from [OWNER_NAME], transcribed with Whisper]: {text}"
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
    sessions.touch_activity(key)
    prev_session = sessions.get_previous_session(key)
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
                    session_manager=sessions, session_key=key))
        if result.status == "failed":
            await _reply_command(
                update,
                "Couldn't confirm memory was saved safely. Keeping the current conversation.",
                command="new",
            )
            return
    else:
        result = None

    session_id = sessions.reset_session(key)
    if result and result.changed_files:
        saved = ", ".join(path.replace("memory/", "") for path in result.changed_files)
        prefix = f"Saved to {saved}. "
    elif result and result.status == "skipped":
        prefix = "No important new memory to save. "
    else:
        prefix = ""
    if session_id:
        await _reply_command(
            update,
            f"{prefix}Fresh conversation started (session {session_id[:8]}...)",
            command="new",
        )
    else:
        await _reply_command(
            update,
            f"{prefix}Fresh conversation started.",
            command="new",
        )


@authorized
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/status — quick calendar status."""
    chat_id = update.effective_chat.id
    key = _session_key(chat_id)
    _log_command_request(update, command="status")
    prompt = "What's on my calendar for today? Be brief."
    resolved_model = None
    sessions.touch_activity(key)
    try:
        await update.message.chat.send_action("typing")
    except TelegramError:
        pass
    async with sessions.get_lock(key):
        session_id, is_new = sessions.get_session(key)
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
    _log_command_request(update, command="context")
    usage = _last_usage.get(_session_key(chat_id))
    session_id, _ = sessions.get_session(key)
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

        lines.append(f"📊 *Session {session_label}*")
        lines.append(f"`[{bar}]` {pct:.1f}%")
        lines.append(f"Input: {inp:,} / 200k tokens")
        lines.append(f"Output: {out:,} tokens")
        if cached:
            lines.append(f"Cache read: {cached:,}")
        if cache_created:
            lines.append(f"Cache created: {cache_created:,}")
    else:
        lines.append(f"📊 *Session {session_label}*")
        lines.append("No token data yet — send a message first.")

    # --- Memory files breakdown ---
    lines.append("")
    lines.append("📁 *Context surfaces*")

    memory_dir = os.path.join(PROJECT_DIR, "memory")
    rules_dir = os.path.join(PROJECT_DIR, ".claude", "rules")
    steering_md = os.path.join(PROJECT_DIR, "CLAUDE.md")
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
    lines.append(f"Loaded every turn: ~{_est_tokens(auto_total):,} tok")
    lines.append(f"_(steering + rules + SOUL = {_fmt(auto_total)})_")

    lines.append("")
    lines.append("*Selectively available on demand*")
    lines.append(f"MEMORY.md (durable): {_fmt(memory_sz)} (~{_est_tokens(memory_sz):,} tok)")
    lines.append(f"STATE.md (operational): {_fmt(state_sz)} (~{_est_tokens(state_sz):,} tok)")
    lines.append(f"SUMMARY.md (background): {_fmt(summary_sz)} (~{_est_tokens(summary_sz):,} tok)")
    lines.append(f"HISTORY.md: {_fmt(history_sz)}")
    lines.append(f"ACTIVE_THREADS.md: {_fmt(active_threads_sz)}")
    lines.append(f"TASKS.md: {_fmt(tasks_sz)}")
    lines.append(f"Daily summaries: {sum_count} files, {_fmt(sum_sz)}")
    lines.append(f"Conversation logs: {conv_count} files, {_fmt(conv_sz)}")
    lines.append("Raw conversation logs are not loaded automatically; use grep when needed.")

    # Warnings
    if usage:
        pct = (usage.get("input_tokens", 0) / 200_000) * 100
        if pct > 80:
            lines.append("\n⚠️ Context almost full. Consider /new.")
        elif pct > 50:
            lines.append("\n⚡ Over halfway.")

    await _reply_command(update, "\n".join(lines), command="context")


@authorized
async def cmd_usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/usage — show 5h + weekly usage remaining."""
    chat_id = update.effective_chat.id
    _log_command_request(update, command="usage")
    lines = ["📈 *Usage*"]

    data, err = await _fetch_claude_usage_windows()
    if err:
        lines.append(f"Usage unavailable: {err}")
    else:
        line_5h = _format_window_line("5h", data.get("five_hour"))
        line_7d = _format_window_line("7d", data.get("seven_day"))
        if line_5h:
            lines.append(line_5h)
        if line_7d:
            lines.append(line_7d)
        if not line_5h and not line_7d:
            lines.append("No 5h/7d usage fields found in the response.")

    await _reply_command(update, "\n".join(lines), command="usage")


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
    sessions.touch_activity(key)

    await _reply_command(update, "Researching (Sonnet)...", command="research")
    model_override = "sonnet"

    await _queue_and_process(chat_id, query, update, context,
                             model=model_override)


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
            "The image from the previous failed request no longer exists. Resend it.",
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
        "/status — quick calendar overview\n"
        "/plan <task> — research and write an implementation plan\n"
        "/execute — execute the active plan\n"
        "/research <question> — research a topic (Sonnet, faster)\n"
        "/retry — retry last failed request\n"
        "/cancel — stop the running task\n"
        "/usage — show 5h + weekly usage remaining\n"
        "/context — show context window usage\n"
        "/heartbeat — run heartbeat check now\n"
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
    await _reply_command(update, "Running heartbeat check...", command="heartbeat")
    await run_heartbeat(bot=context.bot)


# ---------------------------------------------------------------------------
# Heartbeat — periodic autonomous check driven by HEARTBEAT.md
# ---------------------------------------------------------------------------

HEARTBEAT_SESSION_KEY = "heartbeat:triage"
HEARTBEAT_MAX_AGE_HOURS = 24


def _heartbeat_session_age() -> float:
    """Return age of heartbeat session in hours."""
    last = sessions._last_activity.get(HEARTBEAT_SESSION_KEY)
    if not last:
        return float('inf')
    return (datetime.now() - last).total_seconds() / 3600


async def run_heartbeat(bot=None) -> None:
    """Run heartbeat: read HEARTBEAT.md, check items, notify if needed.

    Uses a dedicated session that persists across runs so the heartbeat
    remembers what it already handled. Auto-resets after 24h.
    """
    checklist = _load_heartbeat_checklist()
    if checklist is None:
        log.debug("Heartbeat: HEARTBEAT.md missing or empty, skipping")
        return

    # Don't interrupt active conversations
    if _claude_lock.locked():
        log.info("Heartbeat: skipping — assistant already running")
        return

    async with _claude_lock:
        session_id, is_new = sessions.get_session(HEARTBEAT_SESSION_KEY)

        # Auto-reset stale heartbeat sessions
        if not is_new and _heartbeat_session_age() > HEARTBEAT_MAX_AGE_HOURS:
            log.info("Heartbeat: session older than %dh, resetting",
                     HEARTBEAT_MAX_AGE_HOURS)
            prev_session = sessions.get_previous_session(HEARTBEAT_SESSION_KEY)
            if prev_session:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    None, lambda: consolidate_session(
                        prev_session, system_prompt=EA_SYSTEM_PROMPT,
                        session_manager=sessions, session_key=HEARTBEAT_SESSION_KEY))
            session_id = sessions.reset_session(HEARTBEAT_SESSION_KEY)
            is_new = True

        sessions.touch_activity(HEARTBEAT_SESSION_KEY)
        dbg.info("HEARTBEAT | session=%s (%s)",
                 (session_id[:8] if session_id else "new"),
                 "new" if is_new else "resume")

        async def _heartbeat_progress(msg: str) -> None:
            log.info("Heartbeat: %s", msg)

        prompt = build_heartbeat_prompt(checklist)
        triage = await run_assistant_streaming(
            inject_runtime_context(
                prompt,
                build_runtime_context(
                    channel="heartbeat",
                    chat_id=HEARTBEAT_SESSION_KEY,
                    session_key=HEARTBEAT_SESSION_KEY,
                    purpose="Periodic heartbeat check",
                ),
            ),
            system_prompt=EA_SYSTEM_PROMPT,
            session_id=session_id,
            is_new_session=is_new,
            session_manager=sessions,
            session_key=HEARTBEAT_SESSION_KEY,
            progress_callback=_heartbeat_progress,
        )

    # Suppress if nothing noteworthy
    if _is_heartbeat_ok(triage):
        log.info("Heartbeat: nothing noteworthy")
        return

    # Don't forward timeout messages
    if "timed out" in triage.lower():
        log.warning("Heartbeat: timed out, not forwarding: %s", triage[:200])
        return

    log_message(ch="telegram", dir="out", from_="assistant",
                type_="heartbeat", msg=triage)

    log.info("Heartbeat: something noteworthy, notifying")
    if bot:
        for chat_id in ALLOWED_CHAT_IDS:
            await _safe_send(bot, chat_id, triage)
            log.info("Heartbeat: notification sent to chat %s", chat_id)


async def _heartbeat_loop(bot) -> None:
    """Periodic heartbeat loop."""
    await asyncio.sleep(HEARTBEAT_STARTUP_DELAY_SECONDS)
    log.info("Heartbeat: started (interval=%ds)", HEARTBEAT_INTERVAL_SECONDS)
    while True:
        try:
            await run_heartbeat(bot=bot)
        except Exception as e:
            log.warning("Heartbeat: loop error: %s", e)
        await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)


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
                    f"tg:{k}": v if isinstance(v, str) else (v.get("claude", "") if isinstance(v, dict) else "")
                    for k, v in old_data.get("chat_sessions", {}).items()
                },
                "created_sessions": old_data.get("created_sessions", []),
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
    if task.task_type == "heartbeat":
        bot = task.payload.get("bot")
        await run_heartbeat(bot=bot)
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
        # Find zombie python processes from old Claude subprocesses
        # that have init (PID 1) or launchd as parent (orphaned)
        result = sp.run(
            ["pgrep", "-f", "telegram_bot"],
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
    global task_queue

    log.info("Starting Telegram bot bridge for Claude Code")
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

    # Initialize task queue
    task_queue = TaskQueue()

    async def post_init(application):
        await application.bot.set_my_commands([
            BotCommand("help", "Show available commands"),
            BotCommand("new", "Start a fresh conversation"),
            BotCommand("status", "Quick calendar overview"),
            BotCommand("plan", "Research and write an implementation plan"),
            BotCommand("execute", "Execute the active plan"),
            BotCommand("research", "Research a topic (Sonnet, faster)"),
            BotCommand("retry", "Retry the last failed request"),
            BotCommand("cancel", "Stop the running task"),
            BotCommand("usage", "Show 5h + weekly usage remaining"),
            BotCommand("context", "Show context window usage"),
            BotCommand("heartbeat", "Run heartbeat check now"),
        ])

        # Start background tasks: queue consumer + heartbeat loop
        _bg_tasks.append(asyncio.create_task(
            task_queue.start_consumer(_handle_queued_task)))
        _bg_tasks.append(asyncio.create_task(
            _heartbeat_loop(application.bot)))
        log.info("Task queue consumer and heartbeat started")

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
    app.add_handler(CommandHandler("plan", cmd_plan))
    app.add_handler(CommandHandler("execute", cmd_execute))
    app.add_handler(CommandHandler("research", cmd_research))
    app.add_handler(CommandHandler("retry", cmd_retry))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CommandHandler("usage", cmd_usage))
    app.add_handler(CommandHandler("context", cmd_context))
    app.add_handler(CommandHandler("heartbeat", cmd_heartbeat))

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
