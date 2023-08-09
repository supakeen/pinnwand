import pytest
from playwright.sync_api import Page, Playwright
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
from test.e2e.utils.clipboard_utils import verify_clipboard_contents
from test.e2e.playwright.browser_manager import BrowserManager


@pytest.mark.e2e
def test_copy_paste(playwright: Playwright):
    # This test needs to be run in a headed mode for the clipboard to work correctly
    page = BrowserManager(playwright).create_new_context(headless=False)
    create_paste_page = CreatePastePage(page)
    create_paste_page.open()
    first_pasted_text = create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.click_add_another_file_button()
    second_pasted_text = create_paste_page.paste_random_text(paste_number=1)
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    view_paste_page.click_copy_button(related_paste_number=0)
    verify_clipboard_contents(first_pasted_text)

    view_paste_page.click_copy_button(related_paste_number=1)
    verify_clipboard_contents(second_pasted_text)
