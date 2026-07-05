# ==========================================================
# updater/parser.py
# COMPLETE FILE (1/3)
# ==========================================================

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ReleaseFile:
    path: str
    content: str


@dataclass
class Release:
    version: str = ""
    project: str = ""
    author: str = ""
    files: list = None

    def __post_init__(self):
        if self.files is None:
            self.files = []


class ReleaseParser:

    def __init__(self, release_file):

        self.release_file = Path(release_file)

    def parse(self):

        if not self.release_file.exists():
            return None

        lines = self.release_file.read_text(
            encoding="utf-8"
        ).splitlines()

        release = Release()

        current_file = None
        buffer = []
        inside_file = False

        for line in lines:

            if line.startswith("VERSION="):
                release.version = line.split("=", 1)[1].strip()
                continue

            if line.startswith("PROJECT="):
                release.project = line.split("=", 1)[1].strip()
                continue

            if line.startswith("AUTHOR="):
                release.author = line.split("=", 1)[1].strip()
                continue

            if line.startswith("FILE:"):

                if current_file is not None:

                    release.files.append(
                        ReleaseFile(
                            current_file,
                            "\n".join(buffer)
                        )
                    )

                current_file = line.replace(
                    "FILE:",
                    ""
                ).strip()

                buffer = []
                inside_file = True
                continue
# ==========================================================
# updater/parser.py
# PART 2 / 3
# ==========================================================

            if inside_file:

                if line.startswith("========================================"):
                    continue

                buffer.append(line)

        if current_file is not None:

            release.files.append(
                ReleaseFile(
                    current_file,
                    "\n".join(buffer)
                )
            )

        return release

    def print_summary(self, release):

        print("")
        print("=" * 60)
        print("Release Summary")
        print("=" * 60)

        print(f"Project : {release.project}")
        print(f"Version : {release.version}")
        print(f"Author  : {release.author}")
        print(f"Files   : {len(release.files)}")

        print("=" * 60)

        for file in release.files:

            print(file.path)

        print("=" * 60)


# ==========================================================
# updater/parser.py
# PART 3 / 3
# ==========================================================

    def get_file(self, release, filename):

        for file in release.files:

            if file.path == filename:
                return file

        return None

    def has_file(self, release, filename):

        return self.get_file(release, filename) is not None

    def file_count(self, release):

        return len(release.files)

    def list_files(self, release):

        return [file.path for file in release.files]


# ==========================================================
# END OF FILE
# ==========================================================
