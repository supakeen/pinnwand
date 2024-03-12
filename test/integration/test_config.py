import os

from pinnwand.configuration import Configuration
import tempfile
import toml
import pytest


@pytest.fixture(scope="function")
def temp_dotenv_file():

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as file:
        path = file.name

    yield path
    os.remove(path)


def test_load_environment_config(temp_dotenv_file, monkeypatch):
    monkeypatch.setenv("PINNWAND_SPAMSCORE", "29")
    with open(temp_dotenv_file, "w+") as file:
        file.write("PINNWAND_PASTE_SIZE=524288")
    config = Configuration()
    config.load_environment(dotenv_file_path=temp_dotenv_file)
    assert config.spamscore == 29
    assert config.paste_size == 524288


def test_env_variables_precedence(monkeypatch, temp_dotenv_file):
    monkeypatch.setenv("PINNWAND_SPAMSCORE", "29")
    with open(temp_dotenv_file, "w+") as file:
        file.write("PINNWAND_SPAMSCORE=31")

    config = Configuration()
    config.load_environment(dotenv_file_path=temp_dotenv_file)
    assert config.spamscore == 29


def test_load_file_config():
    with tempfile.NamedTemporaryFile(suffix="", delete=False) as temp:

        props = toml.load(temp.name)
        url = "sqlite:///database.db"
        props["database_uri"] = url

        with open(temp.name, "w") as config_file:
            toml.dump(props, config_file)
            config: Configuration = Configuration()

        config.load_config_file(temp.name)
        assert config.database_uri == url

