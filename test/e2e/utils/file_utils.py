from test.e2e.utils.string_utils import random_string
import tempfile
import os
from contextlib import contextmanager
from pathlib import Path
from zipfile import ZipFile
import shutil


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


def verify_downloaded_file_contents(download, text):
    dir_path = tempfile.mkdtemp()
    file_path = download_path(dir_path, download)
    download.save_as(file_path)
    try:
        with open(file_path) as file:
            assert file.read() == text
    finally:
        shutil.rmtree(dir_path)


def verify_downloaded_archive_contents(
    archive_download, *args, match_all_args=True
):
    dir_path = tempfile.mkdtemp()
    file_path = download_path(dir_path, archive_download)
    archive_download.save_as(file_path)
    try:
        with ZipFile(file_path) as zip_file:
            file_names = zip_file.namelist()
            if match_all_args:
                assert len(file_names) == len(
                    args
                ), "Number of files in downloaded archive was incorrect"
            for file_name in file_names:
                with zip_file.open(file_name) as file:
                    file_content = file.read().decode()
                    assert (
                        file_content in args
                    ), f"Unexpected content of file in archive {file_content}"
    finally:
        shutil.rmtree(dir_path)


def download_path(download_dir_path, download):
    return os.path.join(download_dir_path, download.suggested_filename)
