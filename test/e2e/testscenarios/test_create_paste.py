from playwright.sync_api import Page, Playwright
import pytest
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
from test.e2e.playwright.browser_manager import BrowserManager
from test.e2e.conftest import create_paste_page


@pytest.mark.e2e
def test_create_single_paste(
    page: Page, playwright: Playwright, create_paste_page: CreatePastePage
):
    create_paste_page.should_have_title("Create new paste")

    pasted_text = create_paste_page.paste_random_text()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(pasted_text)

    paste_url = view_paste_page.current_url()
    reopen_created_paste(playwright, paste_url)


@pytest.mark.e2e
def test_create_multi_paste(
    page: Page, playwright: Playwright, create_paste_page: CreatePastePage
):
    first_pasted_text = create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.click_add_another_file_button()

    second_pasted_text = create_paste_page.paste_random_text(paste_number=1)
    create_paste_page.click_add_another_file_button()

    third_pasted_text = create_paste_page.paste_random_text(paste_number=2)

    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(first_pasted_text, paste_number=0)
    view_paste_page.should_have_pasted_text(second_pasted_text, paste_number=1)
    view_paste_page.should_have_pasted_text(third_pasted_text, paste_number=2)

    paste_url = view_paste_page.current_url()
    reopen_created_paste(playwright, paste_url)


def reopen_created_paste(playwright, paste_url):
    new_page = BrowserManager(playwright).create_new_context()
    new_view_paste_page = ViewPastePage(new_page)
    new_view_paste_page.open(paste_url)
    new_view_paste_page.should_be_opened()
