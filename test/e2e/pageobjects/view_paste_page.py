import logging
from test.e2e.pageobjects.base_page import BasePage
from playwright.sync_api import Page, expect

log = logging.getLogger(__name__)


class ViewPastePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page, page.locator(".files"), "View Paste Page")
        self.page = page
        self.source = page.locator(".source")
        self.copy_button = page.locator(".copy-button")

    def click_remove_now_button(self):
        log.info("Clicking Remove Now Button")
        self.page.get_by_role("link", name="Remove now").click()

    def click_copy_button(self, related_paste_number=0):
        log.info("Clicking Copy Button")
        self.copy_button.nth(related_paste_number).click()

    # Expectations
    def should_have_pasted_text(self, text, paste_number=0):
        expect(
            self.source.nth(paste_number),
            f"Pasted text was incorrect on {self.page_name}",
        ).to_have_text(text)
