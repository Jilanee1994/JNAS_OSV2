"""Metrics collector."""

from __future__ import annotations

import threading

from .metrics import MetricsSnapshot


class MetricsCollector:
    """Thread-safe in-memory metrics collector."""

    def __init__(self) -> None:
        self.snapshot = MetricsSnapshot()
        self._lock = threading.RLock()

    def record_task(self, success: bool, duration: float = 0.0) -> None:
        """Record task execution."""
        with self._lock:
            self.snapshot.tasks_executed += 1
            self.snapshot.total_execution_time += duration
            if success:
                self.snapshot.successful_tasks += 1
            else:
                self.snapshot.failed_tasks += 1

    def record_recovery(self, success: bool, retries: int = 0) -> None:
        """Record recovery attempt."""
        with self._lock:
            self.snapshot.recovery_attempts += 1
            self.snapshot.total_retries += retries
            if success:
                self.snapshot.recovery_successes += 1

    def record_usage(self, category: str, name: str) -> None:
        """Record usage in a named category."""
        with self._lock:
            target = getattr(self.snapshot, f"{category}_usage")
            target[name] = target.get(name, 0) + 1

    def get_snapshot(self) -> MetricsSnapshot:
        """Return the current snapshot."""
        with self._lock:
            return self.snapshot
