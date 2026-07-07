# ==========================================================
# updater/writer.py
# V2 - PART 1/3
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

    def read(self, filename):

        with open(

            filename,

            "r",

            encoding="utf-8"

        ) as f:

            return f.read()


# ==========================================================
# updater/writer.py
# V2 - PART 2/3
# ==========================================================

    def exists(self, filename):

        return Path(filename).exists()

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

        filename = Path(filename)

        filename.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        filename.touch(

            exist_ok=True

        )

    def copy(self, source, destination):

        source = Path(source)

        destination = Path(destination)

        destination.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        destination.write_bytes(

            source.read_bytes()

        )

    def overwrite(self, filename, content):

        self.write(

            filename,

            content

        )

# ==========================================================
# updater/writer.py
# V2 - PART 3/3 (FINAL)
# ==========================================================

    def write_bytes(self, filename, data):

        filename = Path(filename)

        filename.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        filename.write_bytes(data)

    def read_bytes(self, filename):

        filename = Path(filename)

        return filename.read_bytes()

    def rename(self, source, destination):

        source = Path(source)
        destination = Path(destination)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        source.rename(destination)

    def move(self, source, destination):

        self.rename(
            source,
            destination
        )

    def size(self, filename):

        filename = Path(filename)

        if not filename.exists():

            return 0

        return filename.stat().st_size

    def is_file(self, filename):

        return Path(filename).is_file()

    def is_directory(self, directory):

        return Path(directory).is_dir()


# ==========================================================
# END OF FILE
# ==========================================================
