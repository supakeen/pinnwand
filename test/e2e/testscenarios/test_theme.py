import pytest
from playwright.sync_api import Page
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
from test.e2e.constants import Theme


@pytest.mark.e2e
def test_toggle_theme(page: Page, create_paste_page: CreatePastePage):
    create_paste_page.should_have_theme(Theme.DEFAULT)

    create_paste_page.click_toggle_theme()
    create_paste_page.should_have_theme(Theme.DARK)

    create_paste_page.reload()
    create_paste_page.should_have_theme(Theme.DARK)
    create_paste_page.paste_random_text()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_theme(Theme.DARK)

    view_paste_page.click_toggle_theme()
    view_paste_page.should_have_theme(Theme.DEFAULT)

    view_paste_page.click_repaste_button()
    create_paste_page.should_be_opened()
    view_paste_page.should_have_theme(Theme.DEFAULT)
