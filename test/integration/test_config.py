from pinnwand.configuration import Configuration
import tempfile
import toml


def test_load_environment_config(monkeypatch):
    monkeypatch.setenv("PINNWAND_SPAMSCORE", "29")
    config = Configuration()
    config.load_environment()
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

