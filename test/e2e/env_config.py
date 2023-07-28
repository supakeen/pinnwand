from typing import Generator
import pytest
import subprocess
import sys
import logging
import socket

log = logging.getLogger(__name__)


def select_port():
    sock = socket.socket()
    sock.bind(("", 0))
    return sock.getsockname()[1]


PORT = str(select_port())
BASE_URL = f"http://localhost:{PORT}/"


@pytest.mark.e2e
@pytest.fixture(scope="session", autouse=True)
def application() -> Generator[None, None, None]:
    # Before All
    log.info(f"Starting Pinnwand application on port {PORT}")
    proc = subprocess.Popen(
        [sys.executable, "-m", "pinnwand", "http", "--port", PORT]
    )
    yield
    # After All
    log.info("Terminating Pinnwand application")
    proc.terminate()
