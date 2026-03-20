"""Lightweight email watcher — pure Python, zero Claude tokens.

Checks [ASSISTANT_NAME]'s Gmail inbox via API every 15 minutes. Only enqueues a heartbeat
triage task when new unread emails appear. State persists across restarts.
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

from task_queue import TaskQueue, P_WATCHER

log = logging.getLogger(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(PROJECT_DIR, "memory", ".heartbeat-state.json")

# Add google-accounts client to path
sys.path.insert(0, str(Path.home() / '.config/google-accounts'))

CHECK_INTERVAL_SECONDS = 900  # 15 minutes


class HeartbeatWatcher:
    """Watches [ASSISTANT_NAME]'s Gmail for new unread emails without spawning Claude."""

    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue
        self.last_unread_ids: set[str] = set()
        self.last_check_time: float = 0
        self._load_state()

    def _load_state(self) -> None:
        """Load persisted state from disk."""
        if not os.path.exists(STATE_FILE):
            return
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
            self.last_unread_ids = set(data.get("last_unread_ids", []))
            self.last_check_time = data.get("last_check_time", 0)
            log.info("Watcher: loaded state — %d known unread IDs",
                     len(self.last_unread_ids))
        except Exception as e:
            log.warning("Watcher: failed to load state: %s", e)

    def _save_state(self) -> None:
        """Persist state to disk."""
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        try:
            with open(STATE_FILE, "w") as f:
                json.dump({
                    "last_unread_ids": list(self.last_unread_ids),
                    "last_check_time": self.last_check_time,
                }, f)
        except Exception as e:
            log.warning("Watcher: failed to save state: %s", e)

    def _check_gmail(self) -> bool:
        """Synchronous Gmail API check. Returns True if new unread emails exist."""
        from client import get_gmail_service
        gmail = get_gmail_service('[EMAIL_ACCOUNT_KEY]')

        results = gmail.users().messages().list(
            userId='me', q='is:unread in:inbox', maxResults=20
        ).execute()

        current_ids = {m['id'] for m in results.get('messages', [])}
        new_ids = current_ids - self.last_unread_ids

        self.last_unread_ids = current_ids
        self.last_check_time = time.time()
        self._save_state()

        if new_ids:
            log.info("Watcher: %d new unread email(s) detected", len(new_ids))
            return True

        log.debug("Watcher: no new emails (%d unread total)", len(current_ids))
        return False

    async def check(self) -> bool:
        """Async wrapper for Gmail check (runs in executor)."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._check_gmail)

    async def run_and_enqueue(self) -> None:
        """Called by scheduler. Checks Gmail, enqueues triage if new mail found."""
        try:
            has_new = await self.check()
            if has_new:
                self.task_queue.enqueue(
                    priority=P_WATCHER,
                    task_type="heartbeat_triage",
                )
        except Exception as e:
            log.warning("Watcher check failed: %s", e)

    async def run_loop(self) -> None:
        """Run the watcher as a continuous loop with CHECK_INTERVAL_SECONDS between checks."""
        log.info("Watcher: starting loop (interval=%ds)", CHECK_INTERVAL_SECONDS)
        # Initial delay to let the bot finish starting
        await asyncio.sleep(10)
        while True:
            await self.run_and_enqueue()
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)
