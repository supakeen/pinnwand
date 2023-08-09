import logging
import string
from test.e2e.env_config import BASE_URL
from test.e2e.pageobjects.base_page import BasePage
from test.e2e.utils.file_utils import extract_file_name
from test.e2e.constants import Theme

from playwright.sync_api import Page, expect

log = logging.getLogger(__name__)


class CreatePastePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(
            page, page.locator(".file-part textarea"), "Create Paste Page"
        )
        self.page = page
        self.url = BASE_URL
        self.paste_input = page.locator(".file-part textarea")
        self.submit_button = page.locator(".paste-submit button[type=submit]")
        self.add_another_paste_button = page.locator("button.add")
        self.file_input = page.locator("#file-input")
        self.file_drop_section = "#file-drop"
        self.root = page.locator("html")
        self.theme_toggle = page.locator("#toggle-color-scheme")

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

    def click_toggle_theme(self):
        log.info("Clicking Toggle Theme button")
        self.theme_toggle.click()

    def reload(self):
        log.info("Reloading %s", self.page_name)
        self.page.reload()

    # Step sequences
    def paste_random_text(self, paste_number=0):
        paste_text = string.ascii_letters + string.digits
        self.type_paste(paste_text, paste_number)
        self.should_have_value_in_paste_input(paste_text, paste_number)
        return paste_text

    # Expectations
    def should_have_value_in_paste_input(self, value, paste_number=0):
        expect(
            self.paste_input.nth(paste_number),
            f"Paste Input had incorrect value on {self.page_name}",
        ).to_have_value(value)

    def should_have_no_value_in_paste_input(self):
        expect(
            self.paste_input,
            f"Paste Input was not empty on {self.page_name}",
        ).to_be_empty()

    def should_have_theme(self, theme):
        expect(
            self.root, f"{self.page_name} didn't have theme {theme.name}"
        ).to_have_class(theme.value["class"])
        expect(
            self.root,
            f"{self.page_name} had incorrect font color for theme {theme.name}",
        ).to_have_css("color", theme.value["font"])
        expect(
            self.root,
            f"{self.page_name} had incorrect background color for theme {theme.name}",
        ).to_have_css("background-color", theme.value["background"])
