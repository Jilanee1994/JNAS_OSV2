# ==========================================================
# updater/validator.py
# V2 - PART 1/2
# ==========================================================

from pathlib import Path


class Validator:

    def validate_release(self, release):

        if release is None:
            return False

        if not release.project:
            return False

        if not release.version:
            return False

        if len(release.files) == 0:
            return False

        return True

    def validate_file(self, file):

        if file is None:
            return False

        if not file.path:
            return False

        return True

    def validate_path(self, path):

        path = Path(path)

        blocked = [
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            ".idea"
        ]

        for part in path.parts:

            if part in blocked:

                return False

        return True

    def validate_content(self, content):

        return content is not None




# ==========================================================
# updater/validator.py
# V2 - PART 2/2 (FINAL)
# ==========================================================

    def validate_all(self, release):

        if not self.validate_release(release):

            return False

        for file in release.files:

            if not self.validate_file(file):

                return False

            if not self.validate_path(file.path):

                return False

            if not self.validate_content(file.content):

                return False

        return True

    def file_exists(self, filename):

        return Path(filename).exists()

    def directory_exists(self, directory):

        return Path(directory).is_dir()

    def __repr__(self):

        return "<Validator V2>"


# ==========================================================
# END OF FILE
# ==========================================================
