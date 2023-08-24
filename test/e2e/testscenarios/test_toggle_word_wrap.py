import pytest
from playwright.sync_api import Page
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from test.e2e.pageobjects.view_paste_page import ViewPastePage


@pytest.mark.e2e
def test_toggle_word_wrap(page: Page, create_paste_page: CreatePastePage):
    first_pasted_text = create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.click_add_another_file_button()

    second_pasted_text = create_paste_page.paste_random_text(paste_number=1)
    create_paste_page.click_submit()

    view_paste_page = ViewPastePage(page)
    view_paste_page.should_be_opened()
    view_paste_page.should_have_pasted_text(first_pasted_text, paste_number=0)
    view_paste_page.should_have_pasted_text(second_pasted_text, paste_number=1)

    view_paste_page.should_have_wrapped_words(paste_number=0)
    view_paste_page.should_have_wrapped_words(paste_number=1)

    view_paste_page.click_toggle_word_wrap_button()

    view_paste_page.should_not_have_wrapped_words(paste_number=0)
    view_paste_page.should_not_have_wrapped_words(paste_number=1)
