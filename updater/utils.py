# ==========================================================
# updater/utils.py
# COMPLETE FILE
# ==========================================================

import hashlib
from pathlib import Path
import os


class Utils:

    @staticmethod
    def sha256(filename):

        filename = Path(filename)

        if not filename.exists():
            return None

        sha = hashlib.sha256()

        with open(filename, "rb") as f:

            while True:

                data = f.read(8192)

                if not data:
                    break

                sha.update(data)

        return sha.hexdigest()

    @staticmethod
    def ensure_dir(directory):

        Path(directory).mkdir(
            parents=True,
            exist_ok=True
        )

    @staticmethod
    def file_size(filename):

        filename = Path(filename)

        if not filename.exists():
            return 0

        return filename.stat().st_size

    @staticmethod
    def exists(path):

        return Path(path).exists()

    @staticmethod
    def read(filename):

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read()

    @staticmethod
    def write(filename, content):

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

    @staticmethod
    def normalize(path):

        return os.path.normpath(path)

    @staticmethod
    def extension(filename):

        return Path(filename).suffix

    @staticmethod
    def filename(path):

        return Path(path).name


# ==========================================================
# END OF FILE
# ==========================================================
