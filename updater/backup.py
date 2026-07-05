# ==========================================================
# updater/backup.py
# COMPLETE FILE
# ==========================================================

import shutil
import datetime
from pathlib import Path


class BackupManager:

    def __init__(self):

        self.root = Path.cwd()
        self.backup_root = self.root / "backups"

        self.backup_root.mkdir(
            parents=True,
            exist_ok=True
        )

    def create_backup(self, files):

        timestamp = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_dir = self.backup_root / timestamp

        backup_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        for file in files:

            source = self.root / file.path

            if not source.exists():
                continue

            destination = backup_dir / file.path

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(
                source,
                destination
            )

    def restore(self, backup_folder):

        backup_folder = Path(backup_folder)

        if not backup_folder.exists():
            return False

        for item in backup_folder.rglob("*"):

            if item.is_dir():
                continue

            relative = item.relative_to(
                backup_folder
            )

            destination = self.root / relative

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(
                item,
                destination
            )

        return True

    def list_backups(self):

        backups = []

        for folder in sorted(
            self.backup_root.iterdir()
        ):

            if folder.is_dir():
                backups.append(folder)

        return backups

    def latest_backup(self):

        backups = self.list_backups()

        if not backups:
            return None

        return backups[-1]


# ==========================================================
# END OF FILE
# ==========================================================
