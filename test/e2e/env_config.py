import logging
import socket
import sys

log = logging.getLogger(__name__)


def is_headless():
    if "--headed" in sys.argv:
        return False
    else:
        return True


def select_port():
    sock = socket.socket()
    sock.bind(("", 0))
    return sock.getsockname()[1]


PORT = str(select_port())
BASE_URL = f"http://localhost:{PORT}/"
