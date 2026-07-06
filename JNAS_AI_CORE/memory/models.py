"""Data models for JSON-backed memory entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass
class MemoryEntry:
    """A single persisted memory value."""

    key: str
    value: Any
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    tags: list[str] = field(default_factory=list)

    def touch(self) -> None:
        """Refresh the update timestamp."""
        self.updated_at = utc_now()
