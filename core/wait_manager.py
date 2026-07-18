from playwright.sync_api import Page


class WaitManager:
    """Handles all waiting operations."""

    @staticmethod
    def seconds(page: Page, seconds: int):
        page.wait_for_timeout(seconds * 1000)

    @staticmethod
    def load(page: Page):
        page.wait_for_load_state("load")

    @staticmethod
    def network(page: Page):
        page.wait_for_load_state("networkidle")

    @staticmethod
    def visible(page: Page, selector: str):
        page.wait_for_selector(selector, state="visible")

    @staticmethod
    def hidden(page: Page, selector: str):
        page.wait_for_selector(selector, state="hidden")
