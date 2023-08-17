import logging

from playwright.sync_api import Locator, Page, expect

log = logging.getLogger(__name__)


class BasePage:
    def __init__(self, page: Page, locator: Locator, name) -> None:
        self.page = page
        self.page_locator = locator
        self.page_name = name
        self.root = page.locator("html")
        self.theme_toggle = page.locator("#toggle-color-scheme")

    def open(self, paste_url):
        log.info(f"Opening page at {paste_url}")
        self.page.goto(paste_url)

    def current_url(self):
        return self.page.url

    def click_toggle_theme(self):
        log.info("Clicking Toggle Theme button")
        self.theme_toggle.click()

    # Expectations
    def should_be_opened(self):
        expect(
            self.page_locator, f"{self.page_name} was not opened"
        ).to_be_visible()

    def should_have_title(self, title):
        expect(
            self.page, f"{self.page_name} had incorrect title"
        ).to_have_title(title)

    def should_have_theme(self, theme):
        expect(
            self.root, f"{self.page_name} didn't have theme {theme.name}"
        ).to_have_class(theme.value["class"])
        expect(
            self.root,
            f"{self.page_name} had incorrect font color for theme {theme.name}",
        ).to_have_css("color", theme.value["font"])
        expect(
            self.root,
            f"{self.page_name} had incorrect background color for theme {theme.name}",
        ).to_have_css("background-color", theme.value["background"])
