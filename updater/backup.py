# ==========================================================
# updater/backup.py
# V2 - PART 1/3
# ==========================================================

import shutil
import datetime
from pathlib import Path


class BackupManager:

    def __init__(self, project_root):

        self.project_root = Path(project_root)

        self.backup_root = self.project_root / "backups"

        self.backup_root.mkdir(
            parents=True,
            exist_ok=True
        )

    def create_backup(self, files):

        timestamp = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_folder = self.backup_root / timestamp

        backup_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        for file in files:

            source = self.project_root / file.path

            if not source.exists():

                continue

            destination = backup_folder / file.path

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(
                source,
                destination
            )

        return backup_folder


# ==========================================================
# updater/backup.py
# V2 - PART 2/3
# ==========================================================

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

            destination = (
                self.project_root / relative
            )

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

        if not self.backup_root.exists():

            return backups

        for folder in sorted(
            self.backup_root.iterdir()
        ):

            if folder.is_dir():

                backups.append(folder)

        return backups

    def latest_backup(self):

        backups = self.list_backups()

        if len(backups) == 0:

            return None

        return backups[-1]


# ==========================================================
# updater/backup.py
# V2 - PART 3/3 (FINAL)
# ==========================================================

    def delete_backup(self, backup_folder):

        backup_folder = Path(backup_folder)

        if backup_folder.exists():

            shutil.rmtree(backup_folder)

            return True

        return False

    def backup_exists(self, backup_folder):

        return Path(backup_folder).exists()

    def backup_count(self):

        return len(self.list_backups())

    def clear_all(self):

        if self.backup_root.exists():

            shutil.rmtree(self.backup_root)

        self.backup_root.mkdir(
            parents=True,
            exist_ok=True
        )


# ==========================================================
# END OF FILE
# ==========================================================
