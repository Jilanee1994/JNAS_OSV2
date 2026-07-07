"""Metrics storage."""

from __future__ import annotations

from pathlib import Path


class MetricsStorage:
    """Store metrics reports as JSON files."""

    def save_report(self, path: Path, content: str) -> Path:
        """Save report content to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path
