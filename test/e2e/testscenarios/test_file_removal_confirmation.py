import pytest
from test.e2e.pageobjects.create_paste_page import CreatePastePage


@pytest.mark.e2e
def test_confirm_removal(create_paste_page: CreatePastePage):
    create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.click_add_another_file_button()

    second_pasted_text = create_paste_page.paste_random_text(paste_number=1)

    create_paste_page.click_remove_file_button(paste_number=0)
    create_paste_page.removal_confirmation_modal.should_be_displayed()

    create_paste_page.removal_confirmation_modal.confirm()
    create_paste_page.removal_confirmation_modal.should_not_be_displayed()
    create_paste_page.should_have_paste_inputs(1)
    create_paste_page.should_have_value_in_paste_input(
        second_pasted_text, paste_number=0
    )


@pytest.mark.e2e
def test_cancel_removal(create_paste_page: CreatePastePage):
    first_pasted_text = create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.click_add_another_file_button()
    second_pasted_text = create_paste_page.paste_random_text(paste_number=1)

    create_paste_page.click_remove_file_button(paste_number=0)
    create_paste_page.removal_confirmation_modal.should_be_displayed()

    create_paste_page.removal_confirmation_modal.cancel()
    create_paste_page.removal_confirmation_modal.should_not_be_displayed()
    create_paste_page.should_have_paste_inputs(2)
    create_paste_page.should_have_value_in_paste_input(
        first_pasted_text, paste_number=0
    )
    create_paste_page.should_have_value_in_paste_input(
        second_pasted_text, paste_number=1
    )


@pytest.mark.e2e
def test_removal_of_empty_paste(create_paste_page: CreatePastePage):
    first_pasted_text = create_paste_page.paste_random_text(paste_number=0)
    create_paste_page.click_add_another_file_button()

    create_paste_page.click_remove_file_button(paste_number=1)
    create_paste_page.removal_confirmation_modal.should_not_be_displayed()

    create_paste_page.should_have_paste_inputs(1)
    create_paste_page.should_have_value_in_paste_input(
        first_pasted_text, paste_number=0
    )
