"""Shared cross-channel topic registry.

Phase 3A scope:
- persist a small topic registry to disk
- create/update topics from relay events only
- keep runtime behavior unchanged unless another component reads this file
"""

from __future__ import annotations

import fcntl
import json
import os
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
TOPICS_FILE = PROJECT_DIR / "memory" / ".shared-topics.json"
TOPICS_LOCK_FILE = TOPICS_FILE.with_suffix(TOPICS_FILE.suffix + ".lock")

STATE_VERSION = 1
TOPIC_STATUS_OPEN = "open"
TOPIC_STATUS_ANSWERED = "answered"
TOPIC_STATUS_COMPLETED = "completed"


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _default_state() -> dict:
    return {"version": STATE_VERSION, "topics": []}


@contextmanager
def _topics_lock(lock_type: int):
    TOPICS_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOPICS_LOCK_FILE, "a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file, lock_type)
        try:
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def _read_state_unlocked() -> dict:
    if not TOPICS_FILE.exists():
        return _default_state()
    try:
        with open(TOPICS_FILE, "r", encoding="utf-8") as f:
            raw = f.read()
        if not raw.strip():
            return _default_state()
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return _default_state()
    if not isinstance(data, dict):
        return _default_state()
    topics = data.get("topics", [])
    if not isinstance(topics, list):
        topics = []
    return {"version": STATE_VERSION, "topics": topics}


def _write_state_unlocked(state: dict) -> None:
    TOPICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = TOPICS_FILE.with_suffix(TOPICS_FILE.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, TOPICS_FILE)


def _atomic_update(fn):
    with _topics_lock(fcntl.LOCK_EX):
        state = _read_state_unlocked()
        result = fn(state)
        _write_state_unlocked(state)
        return result


def _preview(text: str | None, *, limit: int = 220) -> str:
    value = " ".join((text or "").split())
    if len(value) <= limit:
        return value
    return value[: limit - 1] + "…"


def _origin_key(relay_entry: dict) -> str:
    from_channel = relay_entry.get("from_channel") or "unknown"
    ctx = relay_entry.get("from_context") or {}
    if from_channel == "slack":
        channel = ctx.get("channel") or "unknown"
        thread_ts = ctx.get("thread_ts")
        if thread_ts:
            return f"slack:{channel}:{thread_ts}"
        return f"slack:{channel}"
    if from_channel == "telegram":
        chat_id = ctx.get("chat_id")
        if chat_id:
            return f"telegram:{chat_id}"
    return f"relay:{relay_entry.get('id', 'unknown')}"


def _topic_status(relay_status: str | None) -> str:
    if relay_status == "delivered":
        return TOPIC_STATUS_COMPLETED
    if relay_status == "answered":
        return TOPIC_STATUS_ANSWERED
    return TOPIC_STATUS_OPEN


def _ensure_link(refs: list[dict], candidate: dict) -> None:
    if candidate and candidate not in refs:
        refs.append(candidate)


def _build_summary(relay_entry: dict) -> str:
    from_user = relay_entry.get("from_user") or "noen"
    question = _preview(relay_entry.get("message"))
    answer = _preview(relay_entry.get("answer"))
    if answer:
        return f"{from_user} spurte Simon: {question} | Simon svarte: {answer}"
    return f"{from_user} spurte Simon: {question}"


def get_shared_topics(*, status: str | None = None) -> list[dict]:
    with _topics_lock(fcntl.LOCK_SH):
        state = _read_state_unlocked()
    topics = state["topics"]
    if status:
        topics = [topic for topic in topics if topic.get("status") == status]
    return topics


def find_shared_topic(topic_id: str) -> dict | None:
    for topic in get_shared_topics():
        if topic.get("id") == topic_id:
            return topic
    return None


def find_shared_topic_by_prefix(topic_prefix: str) -> dict | None:
    matches = [
        topic for topic in get_shared_topics()
        if topic.get("id", "").startswith(topic_prefix)
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def find_shared_topic_for_slack_thread(channel: str, thread_ts: str | None) -> dict | None:
    if not channel or not thread_ts:
        return None
    origin_key = f"slack:{channel}:{thread_ts}"
    for topic in get_shared_topics():
        if topic.get("origin_key") == origin_key:
            return topic
    return None


def get_recent_shared_topics(*, limit: int = 10) -> list[dict]:
    topics = list(get_shared_topics())
    topics.sort(key=lambda topic: topic.get("updated_at", ""), reverse=True)
    return topics[:limit]


def build_runtime_lines(topic: dict) -> list[str]:
    if not topic:
        return []
    lines = [f"Linked Topic ID: {topic.get('id', 'ukjent')}"]
    status = topic.get("status")
    if status:
        lines.append(f"Linked Topic Status: {status}")
    summary = _preview(topic.get("summary"), limit=320)
    if summary:
        lines.append(f"Linked Topic Summary: {summary}")
    latest_answer = _preview(topic.get("latest_answer"), limit=220)
    if latest_answer:
        lines.append(f"Linked Topic Latest Answer: {latest_answer}")
    return lines


def sync_topic_from_relay(
    relay_entry: dict,
    *,
    answered_in_context: dict | None = None,
) -> str:
    """Create/update one shared topic from a relay entry and return its topic ID."""

    def _update(state: dict) -> str:
        topics = state["topics"]
        relay_id = relay_entry.get("id")
        topic_id = relay_entry.get("shared_topic_id")
        origin_key = _origin_key(relay_entry)
        topic = None

        if topic_id:
            topic = next((item for item in topics if item.get("id") == topic_id), None)
        if topic is None:
            topic = next(
                (item for item in topics if item.get("origin_key") == origin_key),
                None,
            )
        if topic is None and relay_id:
            topic = next(
                (item for item in topics if relay_id in item.get("relay_ids", [])),
                None,
            )

        now = _now_iso()
        if topic is None:
            topic = {
                "id": f"topic_{uuid.uuid4().hex[:12]}",
                "created_at": now,
                "updated_at": now,
                "source": "relay",
                "origin_key": origin_key,
                "status": TOPIC_STATUS_OPEN,
                "participants": [],
                "relay_ids": [],
                "links": {
                    "slack_threads": [],
                    "telegram_chats": [],
                },
                "latest_question": "",
                "latest_answer": "",
                "summary": "",
                "last_relay_status": relay_entry.get("status"),
            }
            topics.append(topic)

        topic["updated_at"] = now
        topic["status"] = _topic_status(relay_entry.get("status"))
        topic["last_relay_status"] = relay_entry.get("status")

        from_user = relay_entry.get("from_user")
        if from_user and from_user not in topic["participants"]:
            topic["participants"].append(from_user)
        if relay_entry.get("answer") and "Simon" not in topic["participants"]:
            topic["participants"].append("Simon")

        if relay_id and relay_id not in topic["relay_ids"]:
            topic["relay_ids"].append(relay_id)

        if relay_entry.get("message"):
            topic["latest_question"] = relay_entry["message"]
        if relay_entry.get("answer"):
            topic["latest_answer"] = relay_entry["answer"]

        from_channel = relay_entry.get("from_channel")
        from_context = relay_entry.get("from_context") or {}
        if from_channel == "slack":
            channel = from_context.get("channel")
            if channel:
                _ensure_link(
                    topic["links"]["slack_threads"],
                    {
                        "channel": channel,
                        "thread_ts": from_context.get("thread_ts") or "",
                    },
                )
        elif from_channel == "telegram":
            chat_id = from_context.get("chat_id")
            if chat_id:
                _ensure_link(
                    topic["links"]["telegram_chats"],
                    {"chat_id": str(chat_id)},
                )

        if answered_in_context:
            chat_id = answered_in_context.get("chat_id")
            if chat_id:
                _ensure_link(
                    topic["links"]["telegram_chats"],
                    {"chat_id": str(chat_id)},
                )

        topic["summary"] = _build_summary(relay_entry)
        return topic["id"]

    return _atomic_update(_update)
