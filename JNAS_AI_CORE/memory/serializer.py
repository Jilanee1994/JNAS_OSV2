"""JSON serialization for memory entries."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from .exceptions import MemorySerializationError
from .models import MemoryEntry


class MemorySerializer:
    """Serialize and deserialize `MemoryEntry` instances as JSON."""

    def to_json(self, entry: MemoryEntry) -> str:
        """Serialize a memory entry to pretty-printed JSON."""
        try:
            return json.dumps(
                self.to_dict(entry),
                ensure_ascii=False,
                indent=4,
                sort_keys=True,
            )
        except (TypeError, ValueError) as exc:
            raise MemorySerializationError(
                f"Unable to serialize memory key '{entry.key}'."
            ) from exc

    def from_json(self, content: str) -> MemoryEntry:
        """Deserialize JSON content into a memory entry."""
        try:
            data = json.loads(content)
            return self.from_dict(data)
        except (TypeError, ValueError, KeyError) as exc:
            raise MemorySerializationError("Unable to deserialize memory entry.") from exc

    def to_dict(self, entry: MemoryEntry) -> dict[str, Any]:
        """Convert a memory entry into a JSON-compatible dictionary."""
        return {
            "id": entry.id,
            "key": entry.key,
            "value": entry.value,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
            "tags": list(entry.tags),
        }

    def from_dict(self, data: dict[str, Any]) -> MemoryEntry:
        """Create a memory entry from a dictionary."""
        return MemoryEntry(
            id=str(data["id"]),
            key=str(data["key"]),
            value=data["value"],
            created_at=self._parse_datetime(str(data["created_at"])),
            updated_at=self._parse_datetime(str(data["updated_at"])),
            tags=[str(tag) for tag in data.get("tags", [])],
        )

    def _parse_datetime(self, value: str) -> datetime:
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise MemorySerializationError(f"Invalid datetime value: {value}") from exc
