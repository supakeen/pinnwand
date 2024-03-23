import contextlib
import logging
from test.e2e.env_config import is_headless
from typing import Optional
from playwright.sync_api import BrowserContext, Page, Playwright

log = logging.getLogger(__name__)


class BrowserManager:

    @classmethod
    @contextlib.contextmanager
    def new_context(cls, playwright: Playwright, headless: Optional[bool] = None) -> BrowserContext:
        log.info("creating new browser context")
        headless = headless if headless is not None else is_headless()
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        try:
            yield context
        except Exception as e:
            log.exception(e)
        finally:
            context.close()

    @classmethod
    @contextlib.contextmanager
    def new_page(cls, playwright: Playwright, headless: Optional[bool] = None) -> Page:
        headless = headless if headless is not None else is_headless()
        with cls.new_context(playwright=playwright, headless=headless) as context:
            page = context.new_page()
            try:
                yield page
            except Exception as e:
                log.exception(e)
            finally:
                page.close()

