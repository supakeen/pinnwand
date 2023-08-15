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
        self.raw_button = page.get_by_role("link", name="raw")
        self.hex_button = page.get_by_role("link", name="hex")
        self.download_file_button = self.page_locator.get_by_role(
            "link", name="download"
        )
        self.download_archive_button = self.page.locator(
            ".paste-meta"
        ).get_by_role("link", name="download")
        self.repaste_button = page.get_by_role("link", name="Repaste")
        self.remove_now_button = page.get_by_role("link", name="Remove now")

    def click_remove_now_button(self):
        log.info("Clicking Remove Now Button")
        self.remove_now_button.click()

    def click_copy_button(self, related_paste_number=0):
        log.info("Clicking Copy Button")
        self.copy_button.nth(related_paste_number).click()

    def click_raw_button(self):
        log.info("Clicking Raw Button")
        self.raw_button.click()

    def click_hex_button(self):
        log.info("Clicking Hex Button")
        self.hex_button.click()

    def click_download_file_button(self, paste_number=0):
        log.info("Clicking Download File Button")
        self.download_file_button.nth(paste_number).click()

    def click_download_archive_button(self):
        log.info("Clicking Download Archive Button")
        self.download_archive_button.click()

    def download_file(self, paste_number=0):
        log.info("Clicking Download File Button")
        with self.page.expect_download() as downloaded_info:
            self.click_download_file_button(paste_number)
        return downloaded_info.value

    def download_archive(self):
        log.info("Clicking Download Archive Button")
        with self.page.expect_download() as downloaded_info:
            self.click_download_archive_button()
        return downloaded_info.value

    def click_repaste_button(self):
        log.info("Clicking Repaste Button")
        self.repaste_button.click()

    # Expectations
    def should_have_pasted_text(self, text, paste_number=0):
        expect(
            self.source.nth(paste_number),
            f"Pasted text was incorrect on {self.page_name}",
        ).to_have_text(text)
