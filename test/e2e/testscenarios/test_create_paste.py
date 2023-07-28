from playwright.sync_api import Page
import string
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
import pytest
from test.e2e.env_config import application


@pytest.mark.e2e
def test_create_paste(page: Page):
    create_paste_page = CreatePastePage(page)
    create_paste_page.open()
    create_paste_page.should_be_opened()
    create_paste_page.should_have_title("Create new paste")

    paste_text = string.ascii_letters + string.digits
    create_paste_page.type_paste(paste_text)
    create_paste_page.should_have_value_in_paste_input(paste_text)
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(paste_text)
