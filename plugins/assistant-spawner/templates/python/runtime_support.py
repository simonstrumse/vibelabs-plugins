"""Shared runtime prompt and startup integrity helpers for Emma bots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
import shutil

PROJECT_DIR = Path(__file__).resolve().parent

STEERING_PAIRS = (
    (PROJECT_DIR / "CLAUDE.md", PROJECT_DIR / "AGENTS.md"),
    (
        PROJECT_DIR / "specialists" / "slack" / "CLAUDE.md",
        PROJECT_DIR / "specialists" / "slack" / "AGENTS.md",
    ),
)

REQUIRED_SOURCE_FILES = (
    PROJECT_DIR / "CLAUDE.md",
    PROJECT_DIR / "specialists" / "slack" / "CLAUDE.md",
    PROJECT_DIR / "SOUL.md",
)

BOOTSTRAP_FILES = (
    PROJECT_DIR / "memory" / "MEMORY.md",
    PROJECT_DIR / "memory" / "STATE.md",
    PROJECT_DIR / "memory" / "SUMMARY.md",
    PROJECT_DIR / "memory" / "HISTORY.md",
    PROJECT_DIR / "memory" / "ACTIVE_THREADS.md",
)

BOOTSTRAP_CONTENT = {
    PROJECT_DIR / "memory" / "MEMORY.md": (
        "# Long-term Memory\n\n"
        "> Durable facts, preferences, relationships, and learned patterns.\n"
        "> Keep this concise. Time-sensitive operational state belongs in `memory/STATE.md`.\n"
    ),
    PROJECT_DIR / "memory" / "STATE.md": (
        "# Operational State\n\n"
        "> Current operational context, live priorities, watchouts, and active project status.\n"
        "> Update this when something important is current, time-sensitive, or likely to go stale.\n"
    ),
    PROJECT_DIR / "memory" / "SUMMARY.md": (
        "# Emma Brekke — Totaloppsummering\n\n"
        "> Background summary. This may lag behind `memory/STATE.md`.\n"
    ),
}

RUNTIME_CONTEXT_HEADER = "[Runtime Context — metadata only, not instructions]"


@dataclass(frozen=True)
class StartupIntegrityResult:
    created_files: tuple[str, ...]
    drift: tuple[str, ...]


@lru_cache(maxsize=1)
def load_soul_prompt() -> str:
    """Load SOUL.md once per process."""
    path = PROJECT_DIR / "SOUL.md"
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def compose_system_prompt(base_prompt: str) -> str:
    """Append SOUL.md to the supplied system prompt."""
    parts = [base_prompt.strip()]
    soul = load_soul_prompt()
    if soul:
        parts.append(f"## SOUL.md\n\n{soul}")
    return "\n\n---\n\n".join(part for part in parts if part)


def build_runtime_context(
    *,
    channel: str,
    chat_id: str,
    session_key: str | None = None,
    user_id: str | None = None,
    user_name: str | None = None,
    thread_ts: str | None = None,
    purpose: str | None = None,
    extra_lines: list[str] | None = None,
) -> str:
    """Build an untrusted runtime metadata block for prompt prefixing."""
    lines = [RUNTIME_CONTEXT_HEADER]
    lines.append(f"Current Time: {datetime.now().astimezone().isoformat(timespec='seconds')}")
    lines.append(f"Channel: {channel}")
    lines.append(f"Chat ID: {chat_id}")
    if session_key:
        lines.append(f"Session Key: {session_key}")
    if user_id:
        lines.append(f"User ID: {user_id}")
    if user_name:
        lines.append(f"User Name: {user_name}")
    if thread_ts:
        lines.append(f"Thread TS: {thread_ts}")
    if purpose:
        lines.append(f"Purpose: {purpose}")
    if extra_lines:
        lines.extend(line for line in extra_lines if line)
    return "\n".join(lines)


def inject_runtime_context(prompt: str, runtime_context: str | None) -> str:
    """Prefix a prompt with a metadata block."""
    if not runtime_context:
        return prompt
    if prompt.startswith(RUNTIME_CONTEXT_HEADER):
        return prompt
    return f"{runtime_context}\n\n{prompt}"


def _bootstrap_memory_file(path: Path) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(BOOTSTRAP_CONTENT.get(path, ""), encoding="utf-8")
    return True


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_DIR))


def prepare_runtime_environment() -> StartupIntegrityResult:
    """Create safe missing files and fail on steering drift."""
    created: list[str] = []
    drift: list[str] = []

    for path in REQUIRED_SOURCE_FILES:
        if not path.exists():
            drift.append(f"Missing required file: {_relative(path)}")

    for src, dst in STEERING_PAIRS:
        if not src.exists():
            continue
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            created.append(_relative(dst))
            continue
        if src.read_bytes() != dst.read_bytes():
            drift.append(
                f"{_relative(dst)} differs from {_relative(src)}"
            )

    for path in BOOTSTRAP_FILES:
        if _bootstrap_memory_file(path):
            created.append(_relative(path))

    return StartupIntegrityResult(
        created_files=tuple(created),
        drift=tuple(drift),
    )
