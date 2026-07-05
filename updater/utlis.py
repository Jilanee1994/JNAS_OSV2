# ==========================================================
# updater/utils.py
# V2 - COMPLETE FILE
# ==========================================================

import hashlib
import os
from pathlib import Path


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
    def sha256_text(text):

        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def ensure_directory(directory):

        Path(directory).mkdir(
            parents=True,
            exist_ok=True
        )

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
    def filename(path):

        return Path(path).name

    @staticmethod
    def extension(path):

        return Path(path).suffix

    @staticmethod
    def filesize(path):

        path = Path(path)

        if not path.exists():

            return 0

        return path.stat().st_size

    @staticmethod
    def is_file(path):

        return Path(path).is_file()

    @staticmethod
    def is_directory(path):

        return Path(path).is_dir()

    @staticmethod
    def delete(path):

        path = Path(path)

        if path.exists():

            path.unlink()

    @staticmethod
    def touch(path):

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        path.touch(exist_ok=True)


# ==========================================================
# END OF FILE
# ==========================================================
