import pytest
from playwright.sync_api import Page
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
from test.e2e.conftest import clear_db


@pytest.mark.e2e
def test_use_longer_uri(page: Page, create_paste_page: CreatePastePage):
    create_paste_page.paste_random_text()
    create_paste_page.check_use_longer_uri()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    # Maximum length of the slug is 26 chars
    view_paste_page.should_have_paste_slug_length(26)


@pytest.mark.e2e
def test_use_shorter_uri(
    page: Page, create_paste_page: CreatePastePage, clear_db
):
    create_paste_page.paste_random_text()
    create_paste_page.uncheck_use_longer_uri()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    # Minimum length of the slug is 2 chars
    view_paste_page.should_have_paste_slug_length(2)
