import pytest
from playwright.sync_api import Page
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
from test.e2e.utils.file_utils import create_random_file


@pytest.mark.e2e
def test_remove_file(page: Page, create_paste_page: CreatePastePage):
    first_pasted_text = create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.click_add_another_file_button()

    second_pasted_text = create_paste_page.paste_random_text(paste_number=1)
    create_paste_page.click_add_another_file_button()

    third_pasted_text = create_paste_page.paste_random_text(paste_number=2)

    create_paste_page.click_remove_file_button(paste_number=1)
    create_paste_page.removal_confirmation_modal.confirm()

    create_paste_page.should_have_value_in_paste_input(
        first_pasted_text, paste_number=0
    )
    create_paste_page.should_have_value_in_paste_input(
        third_pasted_text, paste_number=1
    )
    create_paste_page.should_not_have_value_in_paste_input(third_pasted_text)
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    view_paste_page.should_have_pasted_text(first_pasted_text, paste_number=0)
    view_paste_page.should_have_pasted_text(third_pasted_text, paste_number=1)
    view_paste_page.should_not_have_pasted_text(second_pasted_text)


@pytest.mark.e2e
def test_remove_file_while_repasting(
    page: Page, create_paste_page: CreatePastePage
):
    with create_random_file() as first_temp, create_random_file() as second_temp, create_random_file() as third_temp:
        first_file_content = first_temp.read().decode()
        second_file_content = second_temp.read().decode()
        third_file_content = third_temp.read().decode()
        create_paste_page.add_file_to_file_input(
            [first_temp.name, second_temp.name, third_temp.name]
        )
        create_paste_page.should_have_value_in_paste_input(
            first_file_content, paste_number=0
        )
        create_paste_page.should_have_value_in_paste_input(
            second_file_content, paste_number=1
        )
        create_paste_page.should_have_value_in_paste_input(
            third_file_content, paste_number=2
        )
        create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.click_repaste_button()

    create_paste_page.should_be_opened()

    create_paste_page.click_remove_file_button(paste_number=2)
    create_paste_page.removal_confirmation_modal.confirm()

    create_paste_page.should_not_have_value_in_paste_input(third_file_content)
    create_paste_page.click_submit()

    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(first_file_content, paste_number=0)
    view_paste_page.should_have_pasted_text(second_file_content, paste_number=1)
    view_paste_page.should_not_have_pasted_text(third_file_content)


@pytest.mark.e2e
def test_remove_first_file(page: Page, create_paste_page: CreatePastePage):
    with create_random_file() as first_temp, create_random_file() as second_temp:
        first_file_content = first_temp.read().decode()
        second_file_content = second_temp.read().decode()
        create_paste_page.add_file_to_file_input(
            [first_temp.name, second_temp.name]
        )
        create_paste_page.should_have_value_in_paste_input(
            first_file_content, paste_number=0
        )
        create_paste_page.should_have_value_in_paste_input(
            second_file_content, paste_number=1
        )

    create_paste_page.click_remove_file_button(paste_number=0)
    create_paste_page.removal_confirmation_modal.confirm()

    create_paste_page.should_have_value_in_paste_input(
        second_file_content, paste_number=0
    )
    create_paste_page.should_not_have_value_in_paste_input(first_file_content)
    create_paste_page.should_have_value_in_paste_input(
        second_file_content, paste_number=0
    )
    create_paste_page.should_not_have_remove_file_button()

    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(second_file_content, paste_number=0)


@pytest.mark.e2e
def test_remove_first_file_while_repasting(
    page: Page, create_paste_page: CreatePastePage
):
    first_pasted_text = create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.click_add_another_file_button()

    second_pasted_text = create_paste_page.paste_random_text(paste_number=1)
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(first_pasted_text, paste_number=0)
    view_paste_page.should_have_pasted_text(second_pasted_text, paste_number=1)
    view_paste_page.click_repaste_button()

    create_paste_page.should_be_opened()

    create_paste_page.click_remove_file_button(paste_number=0)
    create_paste_page.removal_confirmation_modal.confirm()
    create_paste_page.should_not_have_value_in_paste_input(first_pasted_text)
    create_paste_page.should_have_value_in_paste_input(
        second_pasted_text, paste_number=0
    )
    create_paste_page.should_not_have_remove_file_button()

    create_paste_page.click_submit()
    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(second_pasted_text, paste_number=0)
