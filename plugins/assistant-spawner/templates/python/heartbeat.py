"""Generic heartbeat — periodic autonomous check driven by HEARTBEAT.md.

Reads memory/HEARTBEAT.md to decide what to check. If the file is empty
or missing, heartbeat is disabled. Runs a Claude turn with the checklist;
if nothing needs attention the agent replies HEARTBEAT_OK (suppressed).

Inspired by OpenClaw's heartbeat pattern:
  Timer → read HEARTBEAT.md → Claude turn → suppress or notify.
"""

import asyncio
import logging
import os
import re
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
HEARTBEAT_FILE = os.path.join(PROJECT_DIR, "memory", "HEARTBEAT.md")

# Defaults — configurable per deployment
HEARTBEAT_INTERVAL_SECONDS = 1800  # 30 minutes
HEARTBEAT_STARTUP_DELAY_SECONDS = 60  # wait for bot to stabilize
HEARTBEAT_OK_TOKEN = "HEARTBEAT_OK"
HEARTBEAT_ACK_MAX_CHARS = 300  # suppress replies shorter than this if they contain the OK token


def _load_heartbeat_checklist() -> str | None:
    """Read HEARTBEAT.md. Returns None if missing, empty, or only headers/whitespace."""
    try:
        content = Path(HEARTBEAT_FILE).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None

    # Strip markdown headers, comments (> lines), horizontal rules, and whitespace
    meaningful = re.sub(r"^(#.*|>.*|---+|\s*)$", "", content, flags=re.MULTILINE).strip()
    if not meaningful:
        return None

    return content


def _is_heartbeat_ok(response: str) -> bool:
    """Check if the response indicates nothing needs attention.

    Following OpenClaw's pattern: if HEARTBEAT_OK appears at start or end,
    and remaining content is short, suppress the response.
    """
    if not response:
        return True

    stripped = response.strip()
    if stripped == HEARTBEAT_OK_TOKEN:
        return True

    # Check if OK token is at start or end with minimal surrounding text
    without_token = stripped.replace(HEARTBEAT_OK_TOKEN, "").strip()
    if HEARTBEAT_OK_TOKEN in stripped and len(without_token) < HEARTBEAT_ACK_MAX_CHARS:
        return True

    return False


def build_heartbeat_prompt(checklist: str) -> str:
    """Build the heartbeat prompt from the checklist content."""
    return (
        "Read memory/HEARTBEAT.md and follow its checklist strictly.\n"
        "Check each item. Do not infer or repeat old tasks from prior chats.\n\n"
        f"{checklist}\n\n"
        f"If nothing needs attention, reply with exactly: {HEARTBEAT_OK_TOKEN}\n"
        "If something IS noteworthy, write a brief summary (under 300 words)."
    )
