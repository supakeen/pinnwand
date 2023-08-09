import logging
from test.e2e.env_config import is_headless

from playwright.sync_api import Page, Playwright

log = logging.getLogger(__name__)


class BrowserManager:
    def __init__(self, playwright: Playwright) -> None:
        self.playwright = playwright

    def create_new_context(self, headless=is_headless()) -> Page:
        log.info("creating new browser context")
        browser = self.playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        return context.new_page()
