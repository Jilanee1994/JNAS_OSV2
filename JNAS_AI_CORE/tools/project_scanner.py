from pathlib import Path


class ProjectScanner:

    def scan(self, folder="."):

        project = []

        for file in Path(folder).rglob("*"):

            if file.is_file():

                project.append(
                    {
                        "name": file.name,
                        "path": str(file),
                        "size": file.stat().st_size
                    }
                )

        return project
