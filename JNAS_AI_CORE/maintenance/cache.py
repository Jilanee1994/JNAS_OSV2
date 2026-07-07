"""Cache cleanup utilities."""

from __future__ import annotations

from pathlib import Path


class CacheCleaner:
    """Clean generated Python cache directories."""

    def clean_pycache(self, root: Path = Path(".")) -> list[Path]:
        """Remove `__pycache__` directories under root."""
        removed = []
        for path in root.rglob("__pycache__"):
            if path.is_dir():
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        file_path.unlink(missing_ok=True)
                path.rmdir()
                removed.append(path)
        return removed
