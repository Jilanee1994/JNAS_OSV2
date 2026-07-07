"""Analytics collector for the AI OS."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass
class AnalyticsSnapshot:
    """Runtime analytics snapshot."""

    execution_count: int = 0
    total_duration: float = 0.0
    failures: int = 0
    healing_attempts: int = 0
    healing_successes: int = 0
    scheduler_runs: int = 0
    llm_performance: dict[str, dict[str, float]] = field(default_factory=dict)

    @property
    def average_duration(self) -> float:
        """Return average execution duration."""
        return self.total_duration / self.execution_count if self.execution_count else 0.0

    @property
    def failure_rate(self) -> float:
        """Return failure rate."""
        return self.failures / self.execution_count if self.execution_count else 0.0


class AnalyticsCollector:
    """Thread-safe analytics collector."""

    def __init__(self) -> None:
        self.snapshot = AnalyticsSnapshot()
        self._lock = threading.RLock()

    def record_execution(self, success: bool, duration: float) -> None:
        """Record an execution result."""
        with self._lock:
            self.snapshot.execution_count += 1
            self.snapshot.total_duration += duration
            if not success:
                self.snapshot.failures += 1

    def record_healing(self, success: bool) -> None:
        """Record self-healing outcome."""
        with self._lock:
            self.snapshot.healing_attempts += 1
            if success:
                self.snapshot.healing_successes += 1

    def record_scheduler_run(self) -> None:
        """Record a scheduler tick."""
        with self._lock:
            self.snapshot.scheduler_runs += 1

    def update_llm_performance(self, performance: dict[str, dict[str, float]]) -> None:
        """Set provider performance analytics."""
        with self._lock:
            self.snapshot.llm_performance = performance

    def get_snapshot(self) -> AnalyticsSnapshot:
        """Return current snapshot."""
        with self._lock:
            return self.snapshot
