import logging
import os
import subprocess
import sys
import tempfile
import time
import pytest
import toml
from threading import Thread
from toml import load
from test.e2e.utils.database_utils import TestDb
from test.e2e.env_config import PORT
from test.e2e.pageobjects.create_paste_page import CreatePastePage
from typing import Generator
from playwright.sync_api import Page
from queue import Queue
from sqlalchemy.orm import close_all_sessions

from test.e2e.utils.file_utils import config_path

log = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def application(database) -> Generator[None, None, None]:
    # Before All
    log.info(f"Starting Pinnwand application on port {PORT}")
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "pinnwand",
            "--configuration-path",
            "test/e2e/pinnwand.toml",
            "http",
            "--port",
            str(PORT),
        ]
    )
    yield
    # After All
    log.info("Terminating Pinnwand application")
    proc.terminate()
    proc.wait()


def collect_proc_out(stdout):
    def enqueue_output(out, queue):
        for line in iter(out.readline):
            queue.put(line)
        queue.close()

    log_queue = Queue()
    thread = Thread(target=enqueue_output, args=(stdout, log_queue))
    thread.daemon = True
    thread.start()
    return log_queue


@pytest.fixture
def create_paste_page(page: Page) -> CreatePastePage:
    create_paste_page = CreatePastePage(page)
    create_paste_page.open()
    create_paste_page.should_be_opened()
    return create_paste_page


@pytest.fixture(scope="session")
def database() -> Generator[None, None, None]:
    log.info("Setting up temp db")
    with tempfile.NamedTemporaryFile(suffix="", delete=False) as temp:
        props = load(config_path)
        props["database_uri"] = f"sqlite:///{temp.name}"
        with open(config_path, "w") as config_file:
            toml.dump(props, config_file)
    yield
    log.info("Tearing down temp db")
    close_all_sessions()
    # Waiting for the connections to be closed
    time.sleep(1)
    os.remove(temp.name)


@pytest.fixture
def clear_db():
    log.info("Clearing temp db")
    TestDb(load(config_path)["database_uri"]).clear_tables("paste", "file")
