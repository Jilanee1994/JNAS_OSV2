# ==========================================================
# updater/parser.py
# V2 - PART 1/4
# ==========================================================

from dataclasses import dataclass, field
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

    files: list = field(default_factory=list)


class ReleaseParser:

    def parse(self, filename):

        filename = Path(filename)

        if not filename.exists():

            return None

        release = Release()

        current_file = None

        buffer = []

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

            lines = f.readlines()

        for line in lines:

            line = line.rstrip("\n")

            if not line:

                continue

            if line.startswith("VERSION="):

                release.version = line.split(
                    "=",
                    1
                )[1].strip()

                continue

            if line.startswith("PROJECT="):

                release.project = line.split(
                    "=",
                    1
                )[1].strip()

                continue

            if line.startswith("AUTHOR="):

                release.author = line.split(
                    "=",
                    1
                )[1].strip()

                continue

# ==========================================================
# updater/parser.py
# V2 - PART 2/4
# ==========================================================

            if line.startswith("FILE:"):

                if current_file is not None:

                    release.files.append(

                        ReleaseFile(

                            path=current_file,

                            content="\n".join(buffer)

                        )

                    )

                current_file = line.replace(

                    "FILE:",

                    ""

                ).strip()

                buffer = []

                continue

            if current_file is not None:

                buffer.append(line)

        if current_file is not None:

            release.files.append(

                ReleaseFile(

                    path=current_file,

                    content="\n".join(buffer)

                )

            )

        return release



# ==========================================================
# updater/parser.py
# V2 - PART 3/4
# ==========================================================

    def get_file(self, release, filename):

        for file in release.files:

            if file.path == filename:

                return file

        return None

    def has_file(self, release, filename):

        return self.get_file(
            release,
            filename
        ) is not None

    def file_count(self, release):

        return len(release.files)

    def list_files(self, release):

        return [

            file.path

            for file in release.files

        ]

    def summary(self, release):

        print("")

        print("=" * 60)

        print("RELEASE SUMMARY")

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
# V2 - PART 4/4 (FINAL)
# ==========================================================

    def validate(self, release):

        if release is None:
            return False

        if not release.project:
            return False

        if not release.version:
            return False

        if len(release.files) == 0:
            return False

        return True

    def __repr__(self):

        return "<ReleaseParser V2>"


# ==========================================================
# END OF FILE
# ==========================================================
