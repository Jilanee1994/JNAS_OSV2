from dataclasses import dataclass


@dataclass
class BrowserConfig:
    browser: str = "chromium"
    headless: bool = False
    timeout: int = 30000
    slow_mo: int = 0
