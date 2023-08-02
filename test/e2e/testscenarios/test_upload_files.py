from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
from test.e2e.utils.file_utils import create_random_file
import pytest
from playwright.sync_api import Page


@pytest.mark.e2e
def test_upload_single_file(page: Page, create_paste_page: CreatePastePage):
    with create_random_file() as temp:
        file_content = temp.read().decode()
        create_paste_page.add_file_to_file_input(temp.name)
        create_paste_page.should_have_value_in_paste_input(file_content)
        create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(file_content)


@pytest.mark.e2e
def test_upload_multiple_files(page: Page, create_paste_page: CreatePastePage):
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
        create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(first_file_content, paste_number=0)
    view_paste_page.should_have_pasted_text(second_file_content, paste_number=1)
