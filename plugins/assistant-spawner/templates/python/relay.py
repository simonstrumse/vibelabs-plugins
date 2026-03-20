"""Cross-channel relay queue — file-based, shared between Slack and Telegram bots.

Allows Slack-Emma to forward questions to Simon on Telegram and get answers back.
Also supports Telegram→Slack relays.

Storage: memory/.relay-queue.json
Concurrency: fcntl.flock() for safe multi-process access.
"""

import fcntl
import json
import logging
import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path

from shared_topics import sync_topic_from_relay

log = logging.getLogger(__name__)

RELAY_FILE = Path(__file__).parent / "memory" / ".relay-queue.json"
RELAY_LOCK_FILE = RELAY_FILE.with_suffix(RELAY_FILE.suffix + ".lock")

# Status flow: pending → forwarded → answered → delivered
STATUS_PENDING = "pending"
STATUS_FORWARDED = "forwarded"
STATUS_ANSWERED = "answered"
STATUS_DELIVERED = "delivered"


@contextmanager
def _queue_lock(lock_type: int):
    """Lock the relay queue via a sidecar lock file."""
    RELAY_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RELAY_LOCK_FILE, "a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file, lock_type)
        try:
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def _read_queue_unlocked() -> list[dict]:
    """Read the relay queue without taking locks. Caller owns locking."""
    if not RELAY_FILE.exists():
        return []
    try:
        with open(RELAY_FILE, encoding="utf-8") as f:
            raw = f.read()
        if not raw.strip():
            return []
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as e:
        log.warning("relay: failed to read queue: %s", e)
        return []


def _read_queue() -> list[dict]:
    """Read the relay queue from disk. Returns [] if file missing/corrupt."""
    with _queue_lock(fcntl.LOCK_SH):
        return _read_queue_unlocked()


def _write_queue_unlocked(queue: list[dict]) -> None:
    """Write the relay queue to disk atomically. Caller owns locking."""
    RELAY_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = RELAY_FILE.with_suffix(RELAY_FILE.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, RELAY_FILE)


def _atomic_update(fn) -> object:
    """Read queue, apply fn, write back. Returns fn's return value."""
    with _queue_lock(fcntl.LOCK_EX):
        queue = _read_queue_unlocked()
        result = fn(queue)
        _write_queue_unlocked(queue)
        return result


def _get_relay(relay_id: str) -> dict | None:
    queue = _read_queue()
    for relay in queue:
        if relay.get("id") == relay_id:
            return relay
    return None


def _attach_shared_topic_id(relay_id: str, topic_id: str) -> None:
    def _update(queue):
        for relay in queue:
            if relay.get("id") == relay_id:
                relay["shared_topic_id"] = topic_id
                return True
        return False

    _atomic_update(_update)


def _sync_shared_topic(relay_id: str, *, answered_in_context: dict | None = None) -> None:
    relay = _get_relay(relay_id)
    if not relay:
        return
    try:
        topic_id = sync_topic_from_relay(
            relay,
            answered_in_context=answered_in_context,
        )
    except Exception as e:
        log.warning("relay: shared topic sync failed for %s: %s", relay_id[:8], e)
        return

    if relay.get("shared_topic_id") != topic_id:
        _attach_shared_topic_id(relay_id, topic_id)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_relay(*, from_channel: str, from_user: str,
                 from_context: dict, message: str) -> str:
    """Create a new relay request. Returns the relay ID."""
    relay_id = str(uuid.uuid4())
    entry = {
        "id": relay_id,
        "created_at": datetime.now().astimezone().isoformat(),
        "from_channel": from_channel,
        "from_user": from_user,
        "from_context": from_context,
        "message": message,
        "shared_topic_id": None,
        "status": STATUS_PENDING,
        "forwarded_at": None,
        "answer": None,
        "answered_at": None,
        "delivered_at": None,
    }

    def _add(queue):
        queue.append(entry)
        return relay_id

    result = _atomic_update(_add)
    _sync_shared_topic(relay_id)
    log.info("relay: created %s from %s/%s: %s",
             relay_id[:8], from_channel, from_user, message[:80])
    return result


def get_relays(*, status: str | None = None,
               from_channel: str | None = None) -> list[dict]:
    """Get relays, optionally filtered by status and/or from_channel."""
    queue = _read_queue()
    results = queue
    if status:
        results = [r for r in results if r.get("status") == status]
    if from_channel:
        results = [r for r in results if r.get("from_channel") == from_channel]
    return results


def find_relay_by_prefix(id_prefix: str) -> dict | None:
    """Find a single relay by ID prefix (for /relay command shorthand)."""
    queue = _read_queue()
    matches = [r for r in queue if r["id"].startswith(id_prefix)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        log.warning("relay: ambiguous prefix %s (%d matches)", id_prefix, len(matches))
    return None


def mark_forwarded(relay_id: str) -> bool:
    """Mark a relay as forwarded to the target channel."""
    def _update(queue):
        for r in queue:
            if r["id"] == relay_id:
                r["status"] = STATUS_FORWARDED
                r["forwarded_at"] = datetime.now().astimezone().isoformat()
                return True
        return False

    result = _atomic_update(_update)
    if result:
        _sync_shared_topic(relay_id)
        log.info("relay: %s marked forwarded", relay_id[:8])
    return result


def mark_answered(
    relay_id: str,
    answer: str,
    *,
    answered_in_context: dict | None = None,
) -> bool:
    """Mark a relay as answered with the given response."""
    def _update(queue):
        for r in queue:
            if r["id"] == relay_id:
                r["status"] = STATUS_ANSWERED
                r["answer"] = answer
                r["answered_at"] = datetime.now().astimezone().isoformat()
                return True
        return False

    result = _atomic_update(_update)
    if result:
        _sync_shared_topic(relay_id, answered_in_context=answered_in_context)
        log.info("relay: %s answered: %s", relay_id[:8], answer[:80])
    return result


def mark_delivered(relay_id: str) -> bool:
    """Mark a relay as delivered back to the original channel."""
    def _update(queue):
        for r in queue:
            if r["id"] == relay_id:
                r["status"] = STATUS_DELIVERED
                r["delivered_at"] = datetime.now().astimezone().isoformat()
                return True
        return False

    result = _atomic_update(_update)
    if result:
        _sync_shared_topic(relay_id)
        log.info("relay: %s delivered", relay_id[:8])
    return result


def cleanup_old(max_age_hours: int = 48) -> int:
    """Remove delivered/old relays. Returns count removed."""
    cutoff = datetime.now().astimezone() - timedelta(hours=max_age_hours)

    def _clean(queue):
        before = len(queue)
        queue[:] = [
            r for r in queue
            if not (
                r.get("status") == STATUS_DELIVERED
                or datetime.fromisoformat(r["created_at"]) < cutoff
            )
        ]
        return before - len(queue)

    removed = _atomic_update(_clean)
    if removed:
        log.info("relay: cleaned up %d old entries", removed)
    return removed
