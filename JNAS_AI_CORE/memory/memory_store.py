"""Filesystem storage for JSON-backed memory entries."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from .exceptions import MemoryNotFound
from .models import MemoryEntry
from .serializer import MemorySerializer


class MemoryStore:
    """Persist memory entries as individual JSON files."""

    def __init__(
        self,
        storage_dir: Path | None = None,
        serializer: MemorySerializer | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        package_root = Path(__file__).resolve().parents[1]
        self.storage_dir = storage_dir or package_root / "workspace" / "memory"
        self.serializer = serializer or MemorySerializer()
        self.logger = logger or logging.getLogger(__name__)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, entry: MemoryEntry) -> MemoryEntry:
        """Write a memory entry to disk."""
        path = self.path_for_key(entry.key)
        content = self.serializer.to_json(entry)
        path.write_text(content, encoding="utf-8")
        self.logger.debug("Saved memory key '%s' to %s.", entry.key, path)
        return entry

    def load(self, key: str) -> MemoryEntry:
        """Load a memory entry by key."""
        path = self.path_for_key(key)
        if not path.exists():
            raise MemoryNotFound(f"Memory key not found: {key}")
        return self.serializer.from_json(path.read_text(encoding="utf-8"))

    def delete(self, key: str) -> None:
        """Delete a memory entry by key."""
        path = self.path_for_key(key)
        if not path.exists():
            raise MemoryNotFound(f"Memory key not found: {key}")
        path.unlink()
        self.logger.debug("Deleted memory key '%s'.", key)

    def list_entries(self) -> list[MemoryEntry]:
        """Load all memory entries from disk."""
        entries = []
        for path in sorted(self.storage_dir.glob("*.json")):
            entries.append(self.serializer.from_json(path.read_text(encoding="utf-8")))
        return entries

    def clear(self) -> None:
        """Remove all persisted memory entries."""
        for path in self.storage_dir.glob("*.json"):
            path.unlink()
        self.logger.debug("Cleared memory store at %s.", self.storage_dir)

    def exists(self, key: str) -> bool:
        """Return whether a memory key exists."""
        return self.path_for_key(key).exists()

    def path_for_key(self, key: str) -> Path:
        """Return the storage path for a memory key."""
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.storage_dir / f"{digest}.json"
