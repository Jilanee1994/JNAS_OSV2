from playwright.sync_api import BrowserContext


class TabManager:

    def __init__(self, context: BrowserContext):
        self.context = context

    def new(self):
        return self.context.new_page()

    def pages(self):
        return self.context.pages

    def close(self, page):
        page.close()

    def close_all(self):
        for page in self.context.pages:
            page.close()
