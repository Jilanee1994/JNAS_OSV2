"""Patch application for self-healing."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from JNAS_AI_CORE.tools.file_tool import FileTool
except ImportError:
    from tools.file_tool import FileTool

from .exceptions import PatchApplicationError


@dataclass
class RecoveryPatch:
    """Full-file patch with rollback metadata."""

    path: Path
    content: str
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class CodePatcher:
    """Apply generated code patches using the existing FileTool."""

    def __init__(self, file_tool: FileTool | None = None) -> None:
        self.file_tool = file_tool or FileTool()
        self._backups: dict[Path, str | None] = {}

    def apply_patch(self, patch: RecoveryPatch) -> Path:
        """Apply a full-file content patch."""
        if not patch.content:
            raise PatchApplicationError("Patch content must not be empty.")
        path = Path(patch.path)
        self._backups[path] = path.read_text(encoding="utf-8") if path.exists() else None
        self.file_tool.write(path, patch.content)
        return path

    def rollback(self, path: Path) -> None:
        """Rollback a previously patched file."""
        path = Path(path)
        if path not in self._backups:
            raise PatchApplicationError(f"No rollback state for {path}.")
        previous = self._backups[path]
        if previous is None:
            if path.exists():
                path.unlink()
            return
        self.file_tool.write(path, previous)
