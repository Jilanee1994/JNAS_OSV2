"""Session model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from .checkpoint import Checkpoint
from .models import TimelineEvent, utc_now
from .progress import Progress
from .status import SessionStatus


@dataclass
class Session:
    """A persistent AI project execution session."""

    project_name: str
    worker_name: str
    current_task: str = ""
    session_id: str = field(default_factory=lambda: str(uuid4()))
    status: str = SessionStatus.CREATED
    progress: Progress = field(default_factory=Progress)
    start_time: datetime = field(default_factory=utc_now)
    last_update: datetime = field(default_factory=utc_now)
    completed_tasks: list[str] = field(default_factory=list)
    remaining_tasks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    self_healing_attempts: int = 0
    memory_usage: dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    checkpoints: list[Checkpoint] = field(default_factory=list)
    timeline: list[TimelineEvent] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        """Update last-modified timestamp."""
        self.last_update = utc_now()

    def add_timeline(self, event_type: str, message: str, metadata: dict[str, Any] | None = None) -> None:
        """Append a timeline event."""
        self.timeline.append(TimelineEvent(event_type, message, metadata=metadata or {}))
        self.touch()
