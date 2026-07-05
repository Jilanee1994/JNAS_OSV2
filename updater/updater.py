# ==========================================================
# updater/updater.py
# V2 - PART 1/6
# ==========================================================

import sys
import hashlib
from pathlib import Path

from parser import ReleaseParser
from writer import FileWriter
from backup import BackupManager
from validator import Validator
from logger import Logger


class Updater:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parent.parent

        self.logger = Logger()

        self.parser = ReleaseParser()

        self.writer = FileWriter()

        self.validator = Validator()

        self.backup = BackupManager(self.project_root)

    def run(self, release_path):

        release_path = Path(release_path)

        if not release_path.exists():

            self.logger.error(
                f"Release not found : {release_path}"
            )

            return False

        self.logger.info("=" * 70)
        self.logger.info("JNAS UPDATER V2")
        self.logger.info("=" * 70)

        release = self.parser.parse(release_path)

        if not self.validator.validate_release(release):

            self.logger.error("Invalid Release")

            return False

        self.logger.info(
            f"Project : {release.project}"
        )

        self.logger.info(
            f"Version : {release.version}"
        )

        self.logger.info(
            f"Files : {len(release.files)}"
        )

        self.backup.create_backup(release.files)

        self.process_files(release)

        self.logger.info("")
        self.logger.info("Finished")

        return True

    def process_files(self, release):

        total = len(release.files)

        index = 1

        for file in release.files:

            self.logger.info("")

            self.logger.info(
                f"[{index}/{total}] {file.path}"
            )

            self.update_file(file)

            index += 1


# ==========================================================
# updater/updater.py
# V2 - PART 2/6
# ==========================================================

    def update_file(self, file):

        destination = self.project_root / file.path

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if destination.exists():

            old_hash = self.file_hash(destination)

            new_hash = self.string_hash(file.content)

            if old_hash == new_hash:

                self.logger.info(
                    "No Changes"
                )

                return

            self.logger.info(
                "Updating..."
            )

        else:

            self.logger.info(
                "Creating..."
            )

        self.writer.write(
            destination,
            file.content
        )

        self.logger.info(
            "Done"
        )

    def file_hash(self, filename):

        sha = hashlib.sha256()

        with open(filename, "rb") as f:

            while True:

                chunk = f.read(8192)

                if not chunk:
                    break

                sha.update(chunk)

        return sha.hexdigest()

    def string_hash(self, text):

        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    def summary(self, release):

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("SUMMARY")
        self.logger.info("=" * 70)

        self.logger.info(
            f"Project : {release.project}"
        )

        self.logger.info(
            f"Version : {release.version}"
        )

        self.logger.info(
            f"Files : {len(release.files)}"
        )

        self.logger.info("=" * 70)

# ==========================================================
# updater/updater.py
# V2 - PART 3/6
# ==========================================================

    def verify(self, release):

        self.logger.info("")
        self.logger.info("Verifying Files...")

        success = True

        for file in release.files:

            destination = self.project_root / file.path

            if not destination.exists():

                self.logger.error(
                    f"Missing : {file.path}"
                )

                success = False

                continue

            self.logger.info(
                f"OK : {file.path}"
            )

        return success

    def rollback(self):

        latest = self.backup.latest_backup()

        if latest is None:

            self.logger.warning(
                "No Backup Found"
            )

            return

        self.logger.info(
            f"Rollback : {latest}"
        )

        self.backup.restore(latest)

    def install_requirements(self):

        req = self.project_root / "requirements.txt"

        if not req.exists():

            return

        self.logger.info(
            "requirements.txt detected"
        )

        self.logger.info(
            "Run manually:"
        )

        self.logger.info(
            "pip install -r requirements.txt"
        )

    def finish(self, release):

        self.summary(release)

        if self.verify(release):

            self.logger.info("")
            self.logger.info(
                "Release Applied Successfully"
            )

        else:

            self.logger.error("")
            self.logger.error(
                "Release Finished With Errors"
            )

        self.install_requirements()


# ==========================================================
# updater/updater.py
# V2 - PART 4/6
# ==========================================================

    def print_header(self):

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("JNAS PROJECT UPDATER")
        self.logger.info("=" * 70)

    def print_footer(self):

        self.logger.info("=" * 70)
        self.logger.info("UPDATE COMPLETE")
        self.logger.info("=" * 70)

    def delete_file(self, relative_path):

        path = self.project_root / relative_path

        if not path.exists():

            return

        path.unlink()

        self.logger.info(
            f"Deleted : {relative_path}"
        )

    def create_directory(self, relative_path):

        directory = self.project_root / relative_path

        directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.logger.info(
            f"Directory : {relative_path}"
        )

    def create_empty_file(self, relative_path):

        file = self.project_root / relative_path

        file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file.touch(
            exist_ok=True
        )

        self.logger.info(
            f"File : {relative_path}"
        )

    def file_exists(self, relative_path):

        return (
            self.project_root /
            relative_path
        ).exists()

    def directory_exists(self, relative_path):

        return (
            self.project_root /
            relative_path
        ).is_dir()


# updater/updater.py
# V2 - PART 5/6
# ==========================================================

    def run_post_tasks(self):

        self.logger.info("")
        self.logger.info("Post Tasks")

        gitignore = self.project_root / ".gitignore"

        if gitignore.exists():

            self.logger.info(".gitignore found")

        else:

            self.logger.warning(".gitignore not found")

    def report(self, release):

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("REPORT")
        self.logger.info("=" * 70)

        self.logger.info(
            f"Project : {release.project}"
        )

        self.logger.info(
            f"Version : {release.version}"
        )

        self.logger.info(
            f"Files : {len(release.files)}"
        )

        self.logger.info("=" * 70)

        for file in release.files:

            self.logger.info(
                file.path
            )

        self.logger.info("=" * 70)

    def execute(self, release):

        self.print_header()

        self.process_files(release)

        self.finish(release)

        self.run_post_tasks()

        self.report(release)

        self.print_footer()


# ==========================================================
# updater/updater.py
# V2 - PART 6/6 (FINAL)
# ==========================================================

def main():

    if len(sys.argv) != 2:

        print("")
        print("=" * 70)
        print("JNAS UPDATER V2")
        print("=" * 70)
        print("")
        print("Usage:")
        print("")
        print("python updater.py <release_file>")
        print("")
        print("Example:")
        print("")
        print("python updater.py ../releases/Release_v2.jnas")
        print("")
        sys.exit(1)

    release_file = sys.argv[1]

    updater = Updater()

    success = updater.run(release_file)

    if success:

        release = updater.parser.parse(
            Path(release_file)
        )

        updater.execute(release)

        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()

# ==========================================================
# END OF FILE
# ==========================================================
