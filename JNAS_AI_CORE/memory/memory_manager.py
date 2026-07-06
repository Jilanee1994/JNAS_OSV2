"""High-level memory manager for JNAS AI Core."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .models import MemoryEntry
from .memory_store import MemoryStore


class MemoryManager:
    """Manage reusable JSON-backed memories."""

    def __init__(
        self,
        storage_dir: Path | None = None,
        store: MemoryStore | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.store = store or MemoryStore(storage_dir=storage_dir, logger=self.logger)

    def save_memory(
        self,
        key: str,
        value: Any,
        tags: list[str] | None = None,
    ) -> MemoryEntry:
        """Create or update a memory entry."""
        self._validate_key(key)
        if self.store.exists(key):
            entry = self.store.load(key)
            entry.value = value
            entry.tags = list(tags or entry.tags)
            entry.touch()
        else:
            entry = MemoryEntry(key=key, value=value, tags=list(tags or []))
        return self.store.save(entry)

    def load_memory(self, key: str) -> MemoryEntry:
        """Load a memory entry by key."""
        self._validate_key(key)
        return self.store.load(key)

    def delete_memory(self, key: str) -> None:
        """Delete a memory entry by key."""
        self._validate_key(key)
        self.store.delete(key)

    def list_memories(self) -> list[MemoryEntry]:
        """Return all stored memories."""
        return self.store.list_entries()

    def search_memory(self, keyword: str) -> list[MemoryEntry]:
        """Search memory keys, values, and tags for a keyword."""
        if not keyword or not keyword.strip():
            return []
        needle = keyword.strip().lower()
        return [
            entry
            for entry in self.list_memories()
            if self._matches(entry, needle)
        ]

    def clear_memory(self) -> None:
        """Delete all stored memories."""
        self.store.clear()

    def _matches(self, entry: MemoryEntry, keyword: str) -> bool:
        text = " ".join(
            [
                entry.key,
                str(entry.value),
                " ".join(entry.tags),
            ]
        ).lower()
        return keyword in text

    def _validate_key(self, key: str) -> None:
        if not key or not key.strip():
            raise ValueError("Memory key must be a non-empty string.")
