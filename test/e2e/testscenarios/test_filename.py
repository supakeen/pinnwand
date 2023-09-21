import pytest
from playwright.sync_api import Page
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage
from test.e2e.utils.file_utils import (
    verify_downloaded_file_name,
    verify_downloaded_archive_filenames,
)


@pytest.mark.e2e
def test_set_no_filename(page: Page, create_paste_page: CreatePastePage):
    create_paste_page.paste_random_text()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    paste_slug = view_paste_page.get_paste_slug()
    download = view_paste_page.download_file()
    verify_downloaded_file_name(download, paste_slug)


@pytest.mark.e2e
def test_set_filename(page: Page, create_paste_page: CreatePastePage):
    create_paste_page.paste_random_text(paste_number=0)
    first_filename = create_paste_page.set_random_filename(paste_number=0)
    first_filename_regex = f"{first_filename}-.*"
    create_paste_page.click_add_another_file_button()

    create_paste_page.paste_random_text(paste_number=1)
    second_filename = create_paste_page.set_random_filename(paste_number=1)
    second_filename_regex = f"{second_filename}-.*"
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    first_download = view_paste_page.download_file(paste_number=0)
    verify_downloaded_file_name(first_download, first_filename_regex)

    second_download = view_paste_page.download_file(paste_number=1)
    verify_downloaded_file_name(second_download, second_filename_regex)

    zip_download = view_paste_page.download_archive()
    verify_downloaded_archive_filenames(
        zip_download,
        first_filename_regex,
        second_filename_regex,
    )


@pytest.mark.e2e
def test_reset_filename(page: Page, create_paste_page: CreatePastePage):
    create_paste_page.paste_random_text()
    filename = create_paste_page.set_random_filename()
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()

    view_paste_page.click_repaste_button()
    create_paste_page.should_be_opened()
    create_paste_page.should_have_value_in_filename_input(filename)
    filename = create_paste_page.set_random_filename()
    filename_regex = f"{filename}-.*"
    create_paste_page.click_submit()
    view_paste_page.should_be_opened()

    download = view_paste_page.download_file()
    verify_downloaded_file_name(download, filename_regex)

    zip_download = view_paste_page.download_archive()
    verify_downloaded_archive_filenames(zip_download, filename_regex)
