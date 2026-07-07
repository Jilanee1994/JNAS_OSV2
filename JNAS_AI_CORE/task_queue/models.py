"""Persistent task queue models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


@dataclass
class QueuedTask:
    """A task stored in the autonomous OS queue."""

    task_type: str
    payload: dict[str, Any]
    priority: int = 100
    run_after: datetime = field(default_factory=utc_now)
    task_id: str = field(default_factory=lambda: str(uuid4()))
    retries: int = 0
    max_retries: int = 3
    status: str = "pending"
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    error: str = ""
