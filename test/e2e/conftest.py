import logging
from pathlib import Path
import subprocess
import sys
import pytest
import tomllib
from threading import Thread

import tomli_w
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
            str(database[0]),
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
def database(tmp_path_factory):
    log.info("Setting up temp database")
    temp_dir = tmp_path_factory.mktemp("pinnwand-e2e")
    temp_config = temp_dir / "pinnwand.toml"
    database_url = f"sqlite:///{temp_dir / 'pinnwand.db'}"
    props = tomllib.loads(Path(config_path).read_text())
    props["database_uri"] = database_url
    props["expiries"] = {
        "1hour": 4,
        "1day": 4,
    }  # It expires in 4 seconds instead of an hour
    with temp_config.open("wb") as config_file:
        tomli_w.dump(props, config_file)
    yield temp_config, database_url
    log.info("Tearing down temp database")
    close_all_sessions()


@pytest.fixture
def clear_db(database):
    log.info("Clearing temp database")
    TestDb(database[1]).clear_tables("paste", "file")
