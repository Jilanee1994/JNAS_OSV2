"""Execution context model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

try:
    from JNAS_AI_CORE.planner import Task
except ImportError:
    from planner import Task


@dataclass
class ExecutionContext:
    """Runtime context for a plan execution."""

    plan_id: str
    current_task: Task | None = None
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
