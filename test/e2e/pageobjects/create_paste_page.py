import logging
from test.e2e.env_config import BASE_URL
from test.e2e.pageobjects.base_page import BasePage
from test.e2e.utils.file_utils import extract_file_name
from test.e2e.utils.string_utils import random_string
from playwright.sync_api import Page, expect

log = logging.getLogger(__name__)


class CreatePastePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(
            page, page.locator(".page-create"), "Create Paste Page"
        )
        self.page = page
        self.url = BASE_URL
        self.paste_input = page.locator(".file-part textarea")
        self.submit_button = page.locator(".paste-submit button[type=submit]")
        self.add_another_paste_button = page.locator("button.add")
        self.file_input = page.locator("#file-input")
        self.file_drop_section = "#file-drop"
        self.remove_file_button = page.locator("button.remove")

    def open(self):
        log.info(f"Opening Pinnwand at {self.url}")
        self.page.goto(self.url)

    def type_paste(self, text, paste_number=0):
        log.info(f"Typing {text} in Paste Input")
        self.paste_input.nth(paste_number).type(text)

    def click_submit(self):
        log.info("Clicking Submit Button")
        self.submit_button.click()

    def click_add_another_file_button(self):
        log.info("Clicking Add Another Paste Button")
        self.add_another_paste_button.click()

    def add_file_to_file_input(self, file_paths):
        log.info("Adding file for uploading")
        self.file_input.set_input_files(file_paths)

    def drag_and_drop_file(self, *files):
        log.info("Dragging files to the Drag-And-Drop section")

        def get_file_contents(file):
            file.seek(0)
            return {
                "file_name": extract_file_name(file.name),
                "file_content": file.read().decode(),
            }

        file_contents = list(map(get_file_contents, files))

        self.page.evaluate(
            """([files, dropAreaSelector]) => {
            var dataTransfer = new DataTransfer();
            files.forEach(file => dataTransfer.items.add(new File([file.file_content.toString('hex')], file.file_name, { type: 'text/plain' })));
            var event = new DragEvent("drop", { dataTransfer: dataTransfer });
            document.querySelector(dropAreaSelector).dispatchEvent(event);
        }""",
            [file_contents, self.file_drop_section],
        )

    def reload(self):
        log.info("Reloading %s", self.page_name)
        self.page.reload()

    def click_remove_file_button(self, paste_number=0):
        log.info("Clicking Remove File button")
        self.remove_file_button.nth(paste_number).click()

    # Step sequences
    def paste_random_text(self, paste_number=0):
        paste_text = random_string()
        self.type_paste(paste_text, paste_number)
        self.should_have_value_in_paste_input(paste_text, paste_number)
        return paste_text

    def repaste_by_adding_random_text(self, paste_number=0):
        pasted_text = self.paste_input.nth(paste_number).text_content()
        added_text = random_string(100)
        repasted_text = added_text + pasted_text
        self.type_paste(added_text, paste_number)
        self.should_have_value_in_paste_input(repasted_text, paste_number)
        return repasted_text

    # Expectations
    def should_have_value_in_paste_input(self, value, paste_number=0):
        expect(
            self.paste_input.nth(paste_number),
            f"Paste Input had incorrect value on {self.page_name}",
        ).to_have_value(value)

    def should_not_have_value_in_paste_input(self, pasted_text):
        assert pasted_text not in map(
            lambda locator: locator.get_attribute("value"),
            self.paste_input.all(),
        ), f"Value was displayed in Paste input on {self.page_name}"

    def should_have_no_value_in_paste_input(self):
        expect(
            self.paste_input,
            f"Paste Input was not empty on {self.page_name}",
        ).to_be_empty()

    def should_not_have_remove_file_button(self):
        expect(
            self.remove_file_button,
            f"Remove This File button was present on {self.page_name}",
        ).not_to_be_attached()
