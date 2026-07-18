import json


class CookieManager:

    def save(self, context, file_path):
        cookies = context.cookies()

        with open(file_path, "w") as f:
            json.dump(cookies, f, indent=4)

    def load(self, context, file_path):
        with open(file_path, "r") as f:
            cookies = json.load(f)

        context.add_cookies(cookies)

    def clear(self, context):
        context.clear_cookies()
