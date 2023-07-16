from playwright.sync_api import Page, expect


def test_hello_world(page: Page):
    assert 1 == 1
