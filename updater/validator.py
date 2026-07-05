# ==========================================================
# updater/validator.py
# COMPLETE FILE
# ==========================================================

from pathlib import Path


class Validator:

    def __init__(self):
        pass

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

    def validate_file(self, release_file):

        if release_file is None:
            return False

        if not release_file.path.strip():
            return False

        return True

    def validate_path(self, path):

        if not path:
            return False

        path = Path(path)

        forbidden = [
            ".git",
            "__pycache__",
            ".venv",
            "venv"
        ]

        for item in forbidden:

            if item in path.parts:
                return False

        return True

    def validate_content(self, content):

        if content is None:
            return False

        return True

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


# ==========================================================
# END OF FILE
# ==========================================================
