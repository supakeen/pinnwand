from test.e2e.conftest import create_paste_page
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage

import pytest
from playwright.sync_api import Page, Playwright


@pytest.mark.e2e
def test_create_single_paste(
    page: Page, playwright: Playwright, create_paste_page: CreatePastePage
):
    first_pasted_text = create_paste_page.paste_random_text()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    first_paste_url = view_paste_page.current_url()

    view_paste_page.click_new_paste_button()
    create_paste_page.should_be_opened()

    second_pasted_text = create_paste_page.paste_random_text()
    create_paste_page.click_submit()
    second_paste_url = view_paste_page.current_url()
    assert first_paste_url != second_paste_url

    view_paste_page.open(first_paste_url)
    view_paste_page.should_have_pasted_text(first_pasted_text)

    view_paste_page.open(second_paste_url)
    view_paste_page.should_have_pasted_text(second_pasted_text)
