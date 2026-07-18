from pathlib import Path


class DownloadManager:

    def __init__(self, download_folder="downloads"):
        self.folder = Path(download_folder)
        self.folder.mkdir(exist_ok=True)

    def save(self, download):
        path = self.folder / download.suggested_filename
        download.save_as(path)
        return path
