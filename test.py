from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        channel="chromium",
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ],
    )

    page = browser.new_page()
    page.goto("https://www.google.com")

    print("Browser started. Keeping it open for 10 minutes...")

    time.sleep(600)   # 10 minutes

    browser.close()
