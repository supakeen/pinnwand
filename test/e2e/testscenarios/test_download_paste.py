from test.e2e.conftest import create_paste_page
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
from test.e2e.utils.file_utils import (
    verify_downloaded_file_contents,
    verify_downloaded_archive_contents,
)
from test.e2e.utils.string_utils import convert_new_lines
import pytest
from playwright.sync_api import Page


@pytest.mark.e2e
def test_download_files(page: Page, create_paste_page: CreatePastePage):
    first_pasted_text = create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.click_add_another_file_button()

    second_pasted_text = create_paste_page.paste_random_text(paste_number=1)
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    first_download = view_paste_page.download_file(paste_number=0)
    verify_downloaded_file_contents(first_download, first_pasted_text)

    second_download = view_paste_page.download_file(paste_number=1)
    verify_downloaded_file_contents(second_download, second_pasted_text)


@pytest.mark.e2e
def test_download_archive(page: Page, create_paste_page: CreatePastePage):
    first_pasted_text = create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.click_add_another_file_button()

    second_pasted_text = create_paste_page.paste_random_text(paste_number=1)
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    zip_download = view_paste_page.download_archive()
    verify_downloaded_archive_contents(
        zip_download,
        convert_new_lines(first_pasted_text),
        convert_new_lines(second_pasted_text),
    )
