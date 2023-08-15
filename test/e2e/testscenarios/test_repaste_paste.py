from test.e2e.conftest import create_paste_page
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
import pytest
from playwright.sync_api import Page


@pytest.mark.e2e
def test_repaste_single_paste(page: Page, create_paste_page: CreatePastePage):
    pasted_text = create_paste_page.paste_random_text()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    view_paste_page.click_repaste_button()
    create_paste_page.should_be_opened()
    create_paste_page.should_have_value_in_paste_input(pasted_text)

    repasted_text = create_paste_page.repaste_by_adding_random_text()
    create_paste_page.click_submit()
    view_paste_page.should_be_opened()

    view_paste_page.should_have_pasted_text(repasted_text)


@pytest.mark.e2e
def test_repaste_multiple_pastes(
    page: Page, create_paste_page: CreatePastePage
):
    first_pasted_text = create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.click_add_another_file_button()

    second_pasted_text = create_paste_page.paste_random_text(paste_number=1)
    create_paste_page.click_add_another_file_button()

    third_pasted_text = create_paste_page.paste_random_text(paste_number=2)
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    view_paste_page.click_repaste_button()
    create_paste_page.should_be_opened()
    create_paste_page.should_have_value_in_paste_input(
        first_pasted_text, paste_number=0
    )
    create_paste_page.should_have_value_in_paste_input(
        second_pasted_text, paste_number=1
    )
    create_paste_page.should_have_value_in_paste_input(
        third_pasted_text, paste_number=2
    )

    first_repasted_text = create_paste_page.repaste_by_adding_random_text(
        paste_number=0
    )
    second_repasted_text = create_paste_page.repaste_by_adding_random_text(
        paste_number=1
    )
    third_repasted_text = create_paste_page.repaste_by_adding_random_text(
        paste_number=2
    )
    create_paste_page.click_submit()
    view_paste_page.should_be_opened()

    view_paste_page.should_have_pasted_text(first_repasted_text, paste_number=0)
    view_paste_page.should_have_pasted_text(
        second_repasted_text, paste_number=1
    )
    view_paste_page.should_have_pasted_text(third_repasted_text, paste_number=2)
