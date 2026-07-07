"""Backup management utilities."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path


class BackupManager:
    """Create timestamped repository backups."""

    def backup_directory(self, source: Path, destination_root: Path = Path("JNAS_AI_CORE/workspace/backups")) -> Path:
        """Copy a directory into a timestamped backup folder."""
        destination_root.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        target = destination_root / f"{source.name}_{stamp}"
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"))
        return target
