from playwright.sync_api import Locator, expect


class BasePage:
    def __init__(self, locator: Locator, name) -> None:
        self.page_locator = locator
        self.page_name = name

    # Expectations
    def should_be_opened(self):
        expect(
            self.page_locator, f"{self.page_name} was not opened"
        ).to_be_visible()
