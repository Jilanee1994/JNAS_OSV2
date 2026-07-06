"""Execution plan model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .task import Task


@dataclass
class ExecutionPlan:
    """Structured plan created from a user goal."""

    goal: str
    tasks: list[Task]
    plan_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
