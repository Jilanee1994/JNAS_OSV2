from playwright.sync_api import sync_playwright
from core.config import BrowserConfig


class BrowserManager:
    """
    Central Browser Manager for JNAS AI Builder

    Responsibilities:
    - Start Browser
    - Create Browser Context
    - Create Pages
    - Close Browser
    """

    def __init__(self, config=None):
        self.config = config or BrowserConfig()

        self.playwright = None
        self.browser = None
        self.context = None

    def start(self):
        """Start Playwright and Browser"""

        self.playwright = sync_playwright().start()

        # Select browser engine
        if self.config.browser.lower() == "chromium":
            browser_engine = self.playwright.chromium

        elif self.config.browser.lower() == "firefox":
            browser_engine = self.playwright.firefox

        elif self.config.browser.lower() == "webkit":
            browser_engine = self.playwright.webkit

        else:
            raise ValueError(
                f"Unsupported browser: {self.config.browser}"
            )

        self.browser = browser_engine.launch(
            headless=self.config.headless,
            channel="chromium" if self.config.browser == "chromium" else None,
            slow_mo=self.config.slow_mo,
            args=[
                "--start-maximized",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

        self.context = self.browser.new_context(
            no_viewport=True,
            accept_downloads=True,
        )

        self.context.set_default_timeout(
            self.config.timeout
        )

        return self.context

    def new_page(self):
        """Create a new browser tab"""

        if self.context is None:
            raise RuntimeError(
                "Browser has not been started."
            )

        return self.context.new_page()

    def pages(self):
        """Return all open pages"""

        if self.context is None:
            return []

        return self.context.pages

    def close_page(self, page):
        """Close a page"""

        if page:
            page.close()

    def close_context(self):
        """Close browser context"""

        if self.context:
            self.context.close()
            self.context = None

    def stop(self):
        """Close everything"""

        try:
            if self.context:
                self.context.close()

            if self.browser:
                self.browser.close()

        finally:
            if self.playwright:
                self.playwright.stop()

        self.context = None
        self.browser = None
        self.playwright = None
