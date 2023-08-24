import pytest
from playwright.sync_api import Page
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
from test.e2e.pageobjects.preview_page import PreviewPage
from test.e2e.utils.string_utils import convert_new_lines


@pytest.mark.e2e
def test_raw_format(page: Page, create_paste_page: CreatePastePage):
    pasted_text = create_paste_page.paste_random_text()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.click_raw_button()

    preview_page = PreviewPage(page)
    preview_page.should_be_opened()
    preview_page.should_have_content(pasted_text)


@pytest.mark.e2e
def test_hex_format(page: Page, create_paste_page: CreatePastePage):
    pasted_text = create_paste_page.paste_random_text()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.click_hex_button()

    preview_page = PreviewPage(page)
    preview_page.should_be_opened()

    hex_text = convert_new_lines(pasted_text).encode("utf-8").hex()
    preview_page.should_have_content(hex_text)
