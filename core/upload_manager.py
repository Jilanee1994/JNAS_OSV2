class UploadManager:

    @staticmethod
    def upload(page, selector, file_path):
        page.set_input_files(selector, file_path)
