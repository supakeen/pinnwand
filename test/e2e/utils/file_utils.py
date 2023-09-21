from test.e2e.utils.string_utils import random_string
import tempfile
import os
from contextlib import contextmanager
from pathlib import Path
from zipfile import ZipFile
import shutil
import re

config_path = os.path.join("test", "e2e", "pinnwand.toml")


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


def verify_downloaded_file_name(download, name_regex):
    def assert_file_name(file):
        assert (
            re.compile(name_regex).match(extract_filename(file.name)),
            f"Name of file {file.name} was not {name_regex}",
        )

    verify_downloaded_file(download, assert_file_name)


def verify_downloaded_file_contents(download, text):
    def assert_file_contents(file):
        file_content = file.read()
        assert (
            file_content == text,
            f"Contents of file was not equal to {text}",
        )

    verify_downloaded_file(download, assert_file_contents)


def verify_downloaded_file(download, assert_func):
    dir_path = tempfile.mkdtemp()
    file_path = download_path(dir_path, download)
    download.save_as(file_path)
    try:
        with open(file_path) as file:
            assert_func(file)
    finally:
        shutil.rmtree(dir_path)


def verify_downloaded_archive_contents(
    archive_download, *args, match_all_args=True
):
    def assert_file_contents(file):
        file_content = file.read().decode()
        assert (
            file_content in args
        ), f"Unexpected content of file in archive {file_content}"

    verify_downloaded_archive(
        archive_download,
        assert_file_contents,
        *args,
        match_all_args=match_all_args,
    )


def verify_downloaded_archive_filenames(
    archive_download, *args, match_all_args=True
):
    def assert_file_names(file):
        filename = extract_filename(file.name)
        assert any(
            re.compile(name_regex).match(extract_filename(file.name))
            for name_regex in args
        ), f"Unexpected name of file in archive {filename}"

    verify_downloaded_archive(
        archive_download,
        assert_file_names,
        *args,
        match_all_args=match_all_args,
    )


def verify_downloaded_archive(
    archive_download, assert_func, *args, match_all_args=True
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
                    assert_func(file)
    finally:
        shutil.rmtree(dir_path)


def download_path(download_dir_path, download):
    return os.path.join(download_dir_path, download.suggested_filename)


def extract_filename(filename):
    return Path(filename).stem
