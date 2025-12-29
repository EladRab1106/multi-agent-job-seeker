# execution/greenhouse/greenhouse_executor.py

from playwright.sync_api import sync_playwright, Page


class GreenhouseExecutor:
    def __init__(self, job_url: str, headless: bool = True):
        self.job_url = job_url
        self.headless = headless

        self.playwright = None
        self.browser = None
        self.context = None
        self.page: Page | None = None

        self._start()

    def _start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless
        )
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        # open job page
        self.page.goto(self.job_url, wait_until="domcontentloaded")

    def get_page(self) -> Page:
        if self.page is None:
            raise RuntimeError("Executor page not initialized")
        return self.page

    def close(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
