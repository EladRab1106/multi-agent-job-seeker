from playwright.sync_api import sync_playwright


class BrowserSession:
    def __init__(self, browser, context, page):
        self.browser = browser
        self.context = context
        self.page = page


def start_session(headless: bool = False) -> BrowserSession:
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()

    return BrowserSession(browser, context, page)
