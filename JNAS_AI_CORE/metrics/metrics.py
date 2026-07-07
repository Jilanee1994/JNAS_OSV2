"""Metrics snapshot models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MetricsSnapshot:
    """Current metrics values."""

    tasks_executed: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    recovery_attempts: int = 0
    recovery_successes: int = 0
    total_execution_time: float = 0.0
    total_retries: int = 0
    tool_usage: dict[str, int] = field(default_factory=dict)
    planner_usage: dict[str, int] = field(default_factory=dict)
    executor_usage: dict[str, int] = field(default_factory=dict)
    memory_usage: dict[str, int] = field(default_factory=dict)

    @property
    def recovery_success_rate(self) -> float:
        """Return recovery success rate."""
        return self.recovery_successes / self.recovery_attempts if self.recovery_attempts else 0.0

    @property
    def average_execution_time(self) -> float:
        """Return average execution time."""
        return self.total_execution_time / self.tasks_executed if self.tasks_executed else 0.0

    @property
    def average_retries(self) -> float:
        """Return average retries per recovery attempt."""
        return self.total_retries / self.recovery_attempts if self.recovery_attempts else 0.0
