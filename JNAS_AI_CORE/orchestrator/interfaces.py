"""Worker interfaces for the JNAS AI Core orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .router import RoutedTask


@dataclass(frozen=True)
class WorkerResult:
    """Normalized result returned by orchestrator workers."""

    success: bool
    message: str
    result: Any = None
    errors: list[str] = field(default_factory=list)


class BaseWorker(Protocol):
    """Protocol implemented by pluggable orchestrator workers."""

    task_type: str

    def execute(self, task: RoutedTask) -> WorkerResult:
        """Execute a routed task and return a normalized worker result."""
