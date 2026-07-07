"""Scheduler job models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class ScheduledJob:
    """A persisted one-time or recurring scheduled job."""

    name: str
    task_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    run_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    interval_seconds: int | None = None
    cron: str | None = None
    enabled: bool = True
    job_id: str = field(default_factory=lambda: str(uuid4()))
    last_run: datetime | None = None
    missed_runs: int = 0
