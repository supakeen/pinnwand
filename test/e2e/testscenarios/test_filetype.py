import pytest
from playwright.sync_api import Page
from test.e2e.constants import Filetype
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage


@pytest.mark.e2e
def test_default_filetype(page: Page, create_paste_page: CreatePastePage):
    create_paste_page.should_have_selected_filetype(
        Filetype.TEXT.value["label"]
    )
    create_paste_page.paste_random_text()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_paste_formatting(Filetype.TEXT.value["value"])


@pytest.mark.e2e
def test_set_filetype(page: Page, create_paste_page: CreatePastePage):
    create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.set_filetype(Filetype.PYTHON.value["value"])
    create_paste_page.click_add_another_file_button()

    create_paste_page.paste_random_text(paste_number=1)
    create_paste_page.set_filetype(Filetype.JAVA.value["value"])
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    view_paste_page.should_have_paste_formatting(
        Filetype.PYTHON.value["value"], paste_number=0
    )
    view_paste_page.should_have_paste_formatting(
        Filetype.JAVA.value["value"], paste_number=1
    )


@pytest.mark.e2e
def test_reset_filetype(page: Page, create_paste_page: CreatePastePage):
    create_paste_page.paste_random_text()
    create_paste_page.set_filetype(Filetype.JAVASCRIPT.value["value"])
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    view_paste_page.click_repaste_button()
    create_paste_page.should_be_opened()
    create_paste_page.should_have_selected_filetype(
        Filetype.JAVASCRIPT.value["value"]
    )
    create_paste_page.set_filetype(Filetype.JSON.value["value"])
    create_paste_page.click_submit()

    view_paste_page.should_be_opened()
    view_paste_page.should_have_paste_formatting(Filetype.JSON.value["value"])
