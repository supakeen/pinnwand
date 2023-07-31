import logging
import subprocess
import sys
from test.e2e.env_config import PORT
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from typing import Generator

import pytest
from playwright.sync_api import Page

log = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def application() -> Generator[None, None, None]:
    # Before All
    log.info(f"Starting Pinnwand application on port {PORT}")
    proc = subprocess.Popen(
        [sys.executable, "-m", "pinnwand", "http", "--port", str(PORT)]
    )
    yield
    # After All
    log.info("Terminating Pinnwand application")
    proc.terminate()


@pytest.fixture
def create_paste_page(page: Page) -> CreatePastePage:
    create_paste_page = CreatePastePage(page)
    create_paste_page.open()
    create_paste_page.should_be_opened()
    return create_paste_page
