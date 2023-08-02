from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.error_page import ErrorPage
from test.e2e.pageobjects.view_paste_page import ViewPastePage

import pytest
from playwright.sync_api import Page, Playwright


@pytest.mark.e2e
def test_delete_single_paste(
    page: Page, playwright: Playwright, create_paste_page: CreatePastePage
):
    create_paste_page.paste_random_text()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    paste_url = view_paste_page.current_url()
    view_paste_page.click_remove_now_button()
    create_paste_page.should_be_opened()
    create_paste_page.should_have_no_value_in_paste_input()

    error_page = ErrorPage(page)
    error_page.open(paste_url)
    error_page.should_be_opened()
    error_page.should_have_title("error")
    error_page.should_have_error_text("404", "That page does not exist")
