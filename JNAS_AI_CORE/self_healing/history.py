"""Recovery history models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RecoveryHistoryEntry:
    """Historical record for one recovery attempt."""

    original_error: str
    recovery_action: str
    retry_count: int
    success: bool
    execution_time: float
    patch_summary: str = ""
    memory_reference: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class RecoveryHistory:
    """In-memory recovery history for the current engine instance."""

    def __init__(self) -> None:
        self._entries: list[RecoveryHistoryEntry] = []

    def add(self, entry: RecoveryHistoryEntry) -> None:
        """Add a recovery history entry."""
        self._entries.append(entry)

    def list_entries(self) -> list[RecoveryHistoryEntry]:
        """Return all recovery history entries."""
        return list(self._entries)

    def last(self) -> RecoveryHistoryEntry | None:
        """Return the most recent recovery entry."""
        return self._entries[-1] if self._entries else None
