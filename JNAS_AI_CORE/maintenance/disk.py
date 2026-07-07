"""Disk analysis utilities."""

from __future__ import annotations

import shutil
from pathlib import Path


class DiskAnalyzer:
    """Analyze disk usage for repository paths."""

    def usage(self, path: Path = Path(".")) -> dict[str, int]:
        """Return total, used, and free disk bytes."""
        total, used, free = shutil.disk_usage(path)
        return {"total": total, "used": used, "free": free}
