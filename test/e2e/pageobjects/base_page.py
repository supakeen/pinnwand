from playwright.sync_api import Page, Locator, expect
import logging

log = logging.getLogger(__name__)


class BasePage:
    def __init__(self, page: Page, locator: Locator, name) -> None:
        self.page = page
        self.page_locator = locator
        self.page_name = name

    def open(self, paste_url):
        log.info(f"Opening page at {paste_url}")
        self.page.goto(paste_url)

    def current_url(self):
        return self.page.url

    # Expectations
    def should_be_opened(self):
        expect(
            self.page_locator, f"{self.page_name} was not opened"
        ).to_be_visible()

    def should_have_title(self, title):
        expect(
            self.page, f"{self.page_name} had incorrect title"
        ).to_have_title(title)
