"""Append-only conversation logger — JSONL, one file per day.

Logs all messages in/out across channels (Telegram, email),
including direct command invocations/results when wrappers call it explicitly.
NOT loaded into context — search with grep/jq when needed.

Storage: memory/conversations/YYYY-MM-DD.jsonl
"""

import json
import os
from datetime import datetime
from pathlib import Path
from threading import Lock

LOG_DIR = Path(__file__).parent / "memory" / "conversations"
_lock = Lock()


def log_message(*, ch: str, dir: str, from_: str, msg: str,
                type_: str = "text", **extra) -> None:
    """Append a message to today's JSONL conversation log.

    Args:
        ch: Channel — "telegram", "email"
        dir: Direction — "in" or "out"
        from_: Sender — "owner", "assistant", or email/name
        msg: Message content
        type_: Message type — "text", "voice", "photo", "heartbeat"
        **extra: Additional fields (sid, transcription, caption, to, subject, etc.)
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    entry = {
        "ts": datetime.now().astimezone().isoformat(),
        "ch": ch,
        "dir": dir,
        "from": from_,
        "type": type_,
        "msg": msg,
        **extra,
    }
    with _lock:
        with open(LOG_DIR / f"{today}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
