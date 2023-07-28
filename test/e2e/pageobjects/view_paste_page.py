from playwright.sync_api import Page, expect
from test.e2e.pageobjects.base_page import BasePage
import logging

log = logging.getLogger(__name__)


class ViewPastePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page.locator(".files"), "View Paste Page")
        self.page = page
        self.source = page.locator(".source")

    # Expectations
    def should_have_pasted_text(self, text):
        expect(
            self.source, f"Pasted text was incorrect on {self.page_name}"
        ).to_have_text(text)
