from playwright.sync_api import Page, expect
from test.e2e.env_config import BASE_URL
from test.e2e.pageobjects.base_page import BasePage
import logging

log = logging.getLogger(__name__)


class CreatePastePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(
            page.locator(".file-part textarea"), "Create Paste Page"
        )
        self.page = page
        self.url = BASE_URL
        self.paste_input = page.locator(".file-part textarea")
        self.submit_button = page.locator(".paste-submit button[type=submit]")

    def open(self):
        log.info(f"Opening Pinnwand at {self.url}")
        self.page.goto(self.url)

    def type_paste(self, text):
        log.info(f"Typing {text} in Paste Input")
        self.paste_input.type(text)

    def click_submit(self):
        log.info("Clicking Submit Button")
        self.submit_button.click()

    # Expectations
    def should_have_title(self, title):
        expect(
            self.page, f"{self.page_name} had incorrect title"
        ).to_have_title(title)

    def should_have_value_in_paste_input(self, value):
        expect(
            self.paste_input,
            f"Paste Input had incorrect value on {self.page_name}",
        ).to_have_value(value)
