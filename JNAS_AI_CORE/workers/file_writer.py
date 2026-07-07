"""Generated code extraction and safe file writing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GeneratedFile:
    """A generated file extracted from an LLM response."""

    relative_path: Path
    content: str


class GeneratedFileWriter:
    """Extract marked files and write them under a target root."""

    FILE_PATTERN = re.compile(
        r"===FILE:(?P<path>.*?)===\s*(?P<content>.*?)\s*===END===",
        re.DOTALL,
    )
    FENCE_PATTERN = re.compile(r"```(?:python|py)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)

    def extract_files(self, response: str) -> list[GeneratedFile]:
        """Extract generated files from filename markers."""
        files = []
        for match in self.FILE_PATTERN.finditer(response):
            raw_path = match.group("path").strip().replace("\\", "/")
            content = self._strip_markdown_fences(match.group("content").strip())
            if raw_path:
                files.append(GeneratedFile(Path(raw_path), content + "\n"))
        if not files:
            raise ValueError("No generated files were found in the LLM response.")
        return files

    def write_files(self, files: list[GeneratedFile], target_root: Path) -> list[Path]:
        """Create directories and write generated files as UTF-8."""
        target_root = target_root.resolve()
        target_root.mkdir(parents=True, exist_ok=True)
        written = []
        for generated_file in files:
            target = self._safe_target(target_root, generated_file.relative_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(generated_file.content, encoding="utf-8")
            written.append(target)
        return written

    def _safe_target(self, target_root: Path, relative_path: Path) -> Path:
        target = (target_root / relative_path).resolve()
        if target_root != target and target_root not in target.parents:
            raise ValueError(f"Generated path escapes target root: {relative_path}")
        return target

    def _strip_markdown_fences(self, content: str) -> str:
        match = self.FENCE_PATTERN.fullmatch(content.strip())
        if match:
            return match.group(1).strip()
        return content
