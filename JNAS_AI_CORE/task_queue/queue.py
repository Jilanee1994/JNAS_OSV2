"""Thread-safe persistent priority queues."""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Iterable

from .models import QueuedTask, utc_now
from .persistence import QueuePersistence


class TaskQueue:
    """Priority, delayed, retry, and dead-letter queue."""

    def __init__(self, persistence: QueuePersistence | None = None) -> None:
        self.persistence = persistence or QueuePersistence()
        self._lock = threading.RLock()
        self._tasks: dict[str, QueuedTask] = {task.task_id: task for task in self.persistence.load()}

    def enqueue(self, task: QueuedTask) -> QueuedTask:
        """Add or replace a task."""
        with self._lock:
            task.updated_at = utc_now()
            self._tasks[task.task_id] = task
            self._save()
            return task

    def dequeue_ready(self, limit: int = 1) -> list[QueuedTask]:
        """Return ready pending tasks ordered by priority."""
        now = datetime.now(timezone.utc)
        with self._lock:
            ready = [
                task for task in self._tasks.values()
                if task.status == "pending" and task.run_after <= now
            ]
            ready.sort(key=lambda item: (item.priority, item.created_at))
            selected = ready[:limit]
            for task in selected:
                task.status = "running"
                task.updated_at = utc_now()
            self._save()
            return selected

    def complete(self, task_id: str) -> None:
        """Mark a task complete."""
        self._set_status(task_id, "completed")

    def fail(self, task_id: str, error: str) -> None:
        """Move a task to retry or dead-letter state."""
        with self._lock:
            task = self._tasks[task_id]
            task.error = error
            task.retries += 1
            task.status = "pending" if task.retries <= task.max_retries else "dead_letter"
            task.updated_at = utc_now()
            self._save()

    def pending(self) -> list[QueuedTask]:
        """List pending tasks."""
        return self._by_status("pending")

    def dead_letter(self) -> list[QueuedTask]:
        """List dead-letter tasks."""
        return self._by_status("dead_letter")

    def all_tasks(self) -> list[QueuedTask]:
        """List all queued tasks."""
        with self._lock:
            return list(self._tasks.values())

    def recover_running(self) -> list[QueuedTask]:
        """Return interrupted running tasks to pending state."""
        recovered = []
        with self._lock:
            for task in self._tasks.values():
                if task.status == "running":
                    task.status = "pending"
                    task.updated_at = utc_now()
                    recovered.append(task)
            self._save()
        return recovered

    def extend(self, tasks: Iterable[QueuedTask]) -> None:
        """Add multiple tasks."""
        for task in tasks:
            self.enqueue(task)

    def _set_status(self, task_id: str, status: str) -> None:
        with self._lock:
            task = self._tasks[task_id]
            task.status = status
            task.updated_at = utc_now()
            self._save()

    def _by_status(self, status: str) -> list[QueuedTask]:
        with self._lock:
            return [task for task in self._tasks.values() if task.status == status]

    def _save(self) -> None:
        self.persistence.save(list(self._tasks.values()))
