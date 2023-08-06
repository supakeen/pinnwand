from test.e2e.utils.string_utils import random_string
import tempfile
import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def create_random_file():
    temp = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
    temp.write(random_string().encode())
    temp.seek(0)
    try:
        yield temp
    finally:
        temp.close()
        os.remove(temp.name)


def extract_file_name(file_path):
    return Path(file_path).name
