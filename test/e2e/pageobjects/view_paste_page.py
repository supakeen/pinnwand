from playwright.sync_api import Page, expect
from test.e2e.pageobjects.base_page import BasePage
import logging

log = logging.getLogger(__name__)


class ViewPastePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page, page.locator(".files"), "View Paste Page")
        self.page = page
        self.source = page.locator(".source")

    def click_remove_now_button(self):
        log.info("Clicking Remove Now Button")
        self.page.get_by_role("link", name="Remove now").click()

    # Expectations
    def should_have_pasted_text(self, text, paste_number=0):
        expect(
            self.source.nth(paste_number),
            f"Pasted text was incorrect on {self.page_name}",
        ).to_have_text(text)
