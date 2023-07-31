from playwright.sync_api import Page, expect
from test.e2e.env_config import BASE_URL
from test.e2e.pageobjects.base_page import BasePage
import logging
import string

log = logging.getLogger(__name__)


class CreatePastePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(
            page, page.locator(".file-part textarea"), "Create Paste Page"
        )
        self.page = page
        self.url = BASE_URL
        self.paste_input = page.locator(".file-part textarea")
        self.submit_button = page.locator(".paste-submit button[type=submit]")
        self.add_another_paste_button = page.locator("button.add")

    def open(self):
        log.info(f"Opening Pinnwand at {self.url}")
        self.page.goto(self.url)

    def type_paste(self, text, paste_number=0):
        log.info(f"Typing {text} in Paste Input")
        self.paste_input.nth(paste_number).type(text)

    def click_submit(self):
        log.info("Clicking Submit Button")
        self.submit_button.click()

    def click_add_another_file_button(self):
        log.info("Clicking Add Another Paste Button")
        self.add_another_paste_button.click()

    # Step sequences
    def paste_random_text(self, paste_number=0):
        paste_text = string.ascii_letters + string.digits
        self.type_paste(paste_text, paste_number)
        self.should_have_value_in_paste_input(paste_text, paste_number)
        return paste_text

    # Expectations
    def should_have_value_in_paste_input(self, value, paste_number=0):
        expect(
            self.paste_input.nth(paste_number),
            f"Paste Input had incorrect value on {self.page_name}",
        ).to_have_value(value)

    def should_have_no_value_in_paste_input(self):
        expect(
            self.paste_input,
            f"Paste Input was not empty on {self.page_name}",
        ).to_be_empty()
