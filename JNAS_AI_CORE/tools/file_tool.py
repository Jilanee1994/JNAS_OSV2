from pathlib import Path


class FileTool:

    def read(self, filename):

        path = Path(filename)

        return path.read_text(encoding="utf-8")


    def write(self, filename, content):

        path = Path(filename)

        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding="utf-8")

        return str(path)


    def exists(self, filename):

        return Path(filename).exists()


    def list(self, folder="."):

        return [str(x) for x in Path(folder).iterdir()]
