"""File creation and writing for Builder Agent V1."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .project_spec import ProjectSpec
from .utils import call_flexible, strip_markdown_fences, write_text_file


class BuilderFileWriter:
    """Create project folders and persist generated file content."""

    _WRITE_CANDIDATES = ("write_file", "save_file", "write", "create_file")

    def __init__(self, file_tool: Any | None = None) -> None:
        self.file_tool = file_tool

    def create_project_root(self, workspace: Path, spec: ProjectSpec) -> Path:
        """Create and return the project root directory."""
        project_root = workspace / spec.slug
        project_root.mkdir(parents=True, exist_ok=True)
        return project_root

    def write_file(self, project_root: Path, relative_path: Path, content: str) -> Path:
        """Write a generated file under the project root."""
        target = self._safe_path(project_root, relative_path)
        clean_content = strip_markdown_fences(content).rstrip() + "\n"
        if self.file_tool is not None:
            try:
                call_flexible(self.file_tool, self._WRITE_CANDIDATES, str(target), clean_content)
                return target
            except (AttributeError, TypeError):
                pass
        write_text_file(target, clean_content)
        return target

    def read_file(self, project_root: Path, relative_path: Path) -> str:
        """Read a generated file."""
        return self._safe_path(project_root, relative_path).read_text(encoding="utf-8")

    def _safe_path(self, project_root: Path, relative_path: Path) -> Path:
        root = project_root.resolve()
        target = (root / relative_path).resolve()
        if root != target and root not in target.parents:
            raise ValueError(f"Generated path escapes project root: {relative_path}")
        return target
