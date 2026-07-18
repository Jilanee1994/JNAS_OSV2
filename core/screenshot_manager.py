from pathlib import Path


class ScreenshotManager:

    def __init__(self):
        Path("screenshots").mkdir(exist_ok=True)

    def page(self, page, name):
        page.screenshot(path=f"screenshots/{name}.png")

    def full(self, page, name):
        page.screenshot(
            path=f"screenshots/{name}.png",
            full_page=True
        )
