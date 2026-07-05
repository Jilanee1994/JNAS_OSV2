# ==========================================================
# updater/writer.py
# COMPLETE FILE
# ==========================================================

from pathlib import Path


class FileWriter:

    def __init__(self):
        pass

    def write(self, filename, content):

        filename = Path(filename)

        filename.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(content)

    def append(self, filename, content):

        filename = Path(filename)

        filename.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            filename,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(content)

    def exists(self, filename):

        return Path(filename).exists()

    def read(self, filename):

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read()

    def delete(self, filename):

        filename = Path(filename)

        if filename.exists():
            filename.unlink()

    def mkdir(self, directory):

        Path(directory).mkdir(
            parents=True,
            exist_ok=True
        )

    def touch(self, filename):

        Path(filename).touch(
            exist_ok=True
        )


# ==========================================================
# END OF FILE
# ==========================================================
