"""Priority task queue — serializes Claude Code access so concurrent tasks never collide.

Single consumer guarantees only one Claude subprocess runs at a time.
Priority levels: P0=user, P1=manual command, P2=background, P3=maintenance.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

log = logging.getLogger(__name__)


@dataclass(order=True)
class Task:
    """A queued task with priority ordering."""
    priority: int                                     # 0=user, 1=manual, 2=background, 3=maintenance
    created_at: float                                 # tiebreaker for same priority
    task_type: str = field(compare=False)             # "user_message", etc.
    payload: dict[str, Any] = field(compare=False, default_factory=dict)


# Priority constants
P_USER = 0
P_MANUAL = 1
P_BACKGROUND = 2
P_MAINTENANCE = 3


class TaskQueue:
    """Priority queue with a single async consumer.

    Ensures only one Claude Code process runs at a time, eliminating
    project-lock contention between concurrent tasks.
    """

    def __init__(self):
        self._queue: asyncio.PriorityQueue[Task] = asyncio.PriorityQueue()
        self._running: bool = False
        self._current_task: Task | None = None
        self._consumer_task: asyncio.Task | None = None

    @property
    def is_running(self) -> bool:
        """True if a task is currently being processed."""
        return self._running

    @property
    def current_task(self) -> Task | None:
        """The task currently being processed, if any."""
        return self._current_task

    @property
    def qsize(self) -> int:
        """Number of tasks waiting in the queue."""
        return self._queue.qsize()

    def enqueue(self, priority: int, task_type: str, **payload) -> None:
        """Add a task to the queue."""
        task = Task(
            priority=priority,
            created_at=time.time(),
            task_type=task_type,
            payload=payload,
        )
        self._queue.put_nowait(task)
        log.info("Enqueued task: type=%s priority=%d (queue size: %d)",
                 task_type, priority, self._queue.qsize())

    async def start_consumer(self, handler: Callable[[Task], Awaitable[None]]) -> None:
        """Start the single consumer loop. Call once at startup."""
        self._consumer_task = asyncio.current_task()
        log.info("Task queue consumer started")
        while True:
            task = await self._queue.get()
            self._running = True
            self._current_task = task
            log.info("Processing task: type=%s priority=%d (waited %.1fs)",
                     task.task_type, task.priority,
                     time.time() - task.created_at)
            try:
                await handler(task)
            except Exception as e:
                log.error("Task handler error for %s: %s", task.task_type, e,
                          exc_info=True)
            finally:
                self._running = False
                self._current_task = None
                self._queue.task_done()

    def stop(self) -> None:
        """Cancel the consumer task."""
        if self._consumer_task and not self._consumer_task.done():
            self._consumer_task.cancel()
            log.info("Task queue consumer stopped")
