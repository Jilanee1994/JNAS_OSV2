from core.browser_manager import BrowserManager


def main():
    browser = BrowserManager()

    browser.start()

    page = browser.new_page()

    print("Opening Google...")

    page.goto("https://google.com")

    print("Current Title:", page.title())

    input("\nPress ENTER to close browser...")

    browser.stop()


if __name__ == "__main__":
    main()
