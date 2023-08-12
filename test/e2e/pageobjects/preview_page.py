import logging
from test.e2e.pageobjects.base_page import BasePage
from playwright.sync_api import Page, expect

log = logging.getLogger(__name__)


class PreviewPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page, page.locator("pre"), "Preview Page")
        self.page = page

    # Expectations
    def should_have_content(self, content):
        expect(
            self.page_locator,
            f"Content of {self.page_name} was incorrect",
        ).to_have_text(content)
