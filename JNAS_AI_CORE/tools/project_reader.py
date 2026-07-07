from pathlib import Path


class ProjectReader:

    def read(self, filename):

        path = Path(filename)

        if not path.exists():
            return None

        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )


    def read_project(self, folder="."):

        project = {}

        for file in Path(folder).rglob("*.py"):

            try:
                project[str(file)] = file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

            except Exception:
                pass

        return project
