# ==========================================================
# updater/updater.py
# PART 1 / 8
# ==========================================================

import os
import sys
import shutil
import hashlib
import datetime
from pathlib import Path

from parser import ReleaseParser
from writer import FileWriter
from backup import BackupManager
from validator import Validator
from logger import Logger


class Updater:

    def __init__(self):

        self.project_root = Path.cwd()

        self.logger = Logger()

        self.validator = Validator()

        self.writer = FileWriter()

        self.backup = BackupManager()

    def run(self, release_file):

        self.logger.info("=" * 60)
        self.logger.info("JNAS UPDATER")
        self.logger.info("=" * 60)

        release_path = Path(release_file)

        if not release_path.exists():

            self.logger.error(
                f"Release file not found: {release_file}"
            )

            return

        parser = ReleaseParser(release_path)

        release = parser.parse()

        if release is None:

            self.logger.error("Unable to parse release.")

            return

        self.logger.info(
            f"Version : {release.version}"
        )

        self.logger.info(
            f"Project : {release.project}"
        )

        self.logger.info(
            f"Files   : {len(release.files)}"
        )

        self.backup.create_backup(
            release.files
        )

        self.update_files(release)

        self.logger.info("")
        self.logger.info("Update Finished Successfully")

    def update_files(self, release):

        for file in release.files:

            self.update_single_file(file)

    def update_single_file(self, file):

        path = self.project_root / file.path

        parent = path.parent

        if not parent.exists():

            parent.mkdir(
                parents=True,
                exist_ok=True
            )

        if path.exists():

            self.logger.info(
                f"Updating : {file.path}"
            )

        else:

            self.logger.info(
                f"Creating : {file.path}"
            )

        self.writer.write(
            path,
            file.content
        )
# ==========================================================
# updater/updater.py
# PART 2 / 8
# ==========================================================

    def print_summary(self, release):

        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("SUMMARY")
        self.logger.info("=" * 60)

        self.logger.info(
            f"Project : {release.project}"
        )

        self.logger.info(
            f"Version : {release.version}"
        )

        self.logger.info(
            f"Files Updated : {len(release.files)}"
        )

        self.logger.info("=" * 60)

    def calculate_hash(self, filename):

        sha = hashlib.sha256()

        with open(filename, "rb") as f:

            while True:

                data = f.read(8192)

                if not data:
                    break

                sha.update(data)

        return sha.hexdigest()

    def verify_files(self, release):

        self.logger.info("")
        self.logger.info("Verifying files...")

        ok = True

        for file in release.files:

            path = self.project_root / file.path

            if not path.exists():

                self.logger.error(
                    f"Missing : {file.path}"
                )

                ok = False

                continue

            size = path.stat().st_size

            self.logger.info(
                f"{file.path} ({size} bytes)"
            )

        return ok

    def finish(self, release):

        self.print_summary(release)

        if self.verify_files(release):

            self.logger.info("")
            self.logger.info("Release Applied Successfully")

        else:

            self.logger.error("")
            self.logger.error("Release Finished With Errors")


# ==========================================================
# updater/updater.py
# PART 3 / 8
# ==========================================================

def main():

    if len(sys.argv) != 2:

        print("")
        print("JNAS Updater")
        print("")
        print("Usage:")
        print("")
        print("python updater.py <release_file>")
        print("")
        print("Example:")
        print("")
        print("python updater.py ../releases/Release_v1.jnas")
        print("")
        return

    release_file = sys.argv[1]

    updater = Updater()

    updater.run(release_file)


if __name__ == "__main__":
    main()
