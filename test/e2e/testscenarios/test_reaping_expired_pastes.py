from test.e2e.conftest import create_paste_page
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
from test.e2e.pageobjects.error_page import ErrorPage
from urllib3.util.url import parse_url

import pytest
from playwright.sync_api import Page, Playwright


@pytest.mark.e2e
def test_view_expired_paste(
    page: Page, playwright: Playwright, create_paste_page: CreatePastePage
):
    create_paste_page.should_have_title("Create new paste")

    pasted_text = create_paste_page.paste_random_text()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(pasted_text)

    page.wait_for_timeout(5000)
    view_paste_page.refresh()
    error_page = ErrorPage(page)
    error_page.should_be_opened()
    error_page.should_have_error_text("404", "That page does not exist")


@pytest.mark.e2e
def test_view_expired_paste_on_redirect(
    page: Page, playwright: Playwright, create_paste_page: CreatePastePage
):
    create_paste_page.should_have_title("Create new paste")

    pasted_text = create_paste_page.paste_random_text()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(pasted_text)

    paste_url = view_paste_page.current_url()
    parsed_url = parse_url(paste_url)
    parsed_url = parsed_url._replace(path=f"/show{parsed_url.path}")

    show_url = parsed_url.url
    page.wait_for_timeout(5000)
    page.goto(show_url)

    error_page = ErrorPage(page)
    error_page.should_be_opened()
    error_page.should_have_error_text("404", "That page does not exist")
