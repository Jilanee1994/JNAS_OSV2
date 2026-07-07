"""History models for autonomous code generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class GenerationHistoryEntry:
    """A single generation run record."""

    prompt: str
    generated_files: list[str] = field(default_factory=list)
    retries: int = 0
    compile_errors: list[str] = field(default_factory=list)
    final_status: str = "pending"
    duration: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class GenerationHistory:
    """Store generation history in memory and optionally external memory."""

    def __init__(self, memory_manager: object | None = None) -> None:
        self.entries: list[GenerationHistoryEntry] = []
        self.memory_manager = memory_manager

    def add(self, entry: GenerationHistoryEntry) -> None:
        """Store a generation history entry."""
        self.entries.append(entry)
        if self.memory_manager is not None and entry.final_status == "success":
            save_memory = getattr(self.memory_manager, "save_memory", None)
            if callable(save_memory):
                save_memory(f"code_generation:{entry.created_at.isoformat()}", self.to_dict(entry))

    def to_dict(self, entry: GenerationHistoryEntry) -> dict[str, object]:
        """Convert a history entry to JSON-compatible data."""
        return {
            "prompt": entry.prompt,
            "generated_files": entry.generated_files,
            "retries": entry.retries,
            "compile_errors": entry.compile_errors,
            "final_status": entry.final_status,
            "duration": entry.duration,
            "created_at": entry.created_at.isoformat(),
        }
