import ast
import os
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # lie to mypy, see https://github.com/python/mypy/issues/1153
    import tomllib as toml
else:
    try:
        import tomllib as toml
    except ImportError:
        import tomli as toml


class Configuration:
    """A class that holds all pinnwand's configuration."""

    def __init__(self):
        self._database_uri = "sqlite:///:memory:"
        self._paste_size = 256 * 1024  # in bytes
        self._footer = 'View <a href="//github.com/supakeen/pinnwand" target="_BLANK">source code</a>, the <a href="/removal">removal</a> or <a href="/expiry">expiry</a> stories, or read the <a href="/about">about</a> page.'
        self._paste_help = "<p>Welcome to pinnwand, this site is a pastebin. It allows you to share code with others. If you write code in the text area below and press the paste button you will be given a link you can share with others so they can view your code as well.</p><p>People with the link can view your pasted code, only you can remove your paste and it expires automatically. Note that anyone could guess the URI to your paste so don't rely on it being private.</p>"
        self._page_path = None
        self._page_list = ["about", "removal", "expiry"]
        self._default_selected_lexer = "text"
        self._preferred_lexers = []  # type: ignore
        self._logo_path = None
        self._report_email = None
        self._expiries = {"1day": 86400, "1week": 604800}
        self._reaping_periodicity = 1_800_800
        self._ratelimit = {
            "read": {
                "capacity": 100,
                "consume": 1,
                "refill": 2,
            },
            "create": {
                "capacity": 2,
                "consume": 2,
                "refill": 1,
            },
            "delete": {
                "capacity": 2,
                "consume": 2,
                "refill": 1,
            },
        }
        self._spamscore = 50

    # Define getters for each configuration parameter
    @property
    def database_uri(self):
        return self._database_uri

    @property
    def paste_size(self):
        return self._paste_size

    @property
    def footer(self):
        return self._footer

    @property
    def paste_help(self):
        return self._paste_help

    @property
    def page_path(self):
        return self._page_path

    @property
    def page_list(self):
        return self._page_list

    @property
    def default_selected_lexer(self):
        return self._default_selected_lexer

    @property
    def preferred_lexers(self):
        return self._preferred_lexers

    @property
    def logo_path(self):
        return self._logo_path

    @property
    def report_email(self):
        return self._report_email

    @property
    def expiries(self):
        return self._expiries

    @property
    def reaping_periodicity(self):
        return self._reaping_periodicity

    @property
    def ratelimit(self):
        return self._ratelimit

    @property
    def spamscore(self):
        return self._spamscore

    def load_config_file(self, path: Optional[str] = None) -> None:
        """Load configuration settings from a toml file."""

        with open(path, "rb") as file:
            loaded_configuration = toml.load(file)

            for key, value in loaded_configuration.items():
                setattr(self, f"_{key}", value)

    def load_environment(self):
        """Load configuration from the environment, if any."""
        for key, value in os.environ.items():
            if not key.startswith("PINNWAND_"):
                continue

            key = key.removeprefix("PINNWAND_")
            key = key.lower()

            try:
                value = ast.literal_eval(value)
                setattr(self, f"_{key}", value)
            except (ValueError, SyntaxError):
                # When `ast.literal_eval` can't parse the value into another
                # type we take it at string value
                pass


class ConfigurationProvider:
    """A class responsible for providing an instance of the configuration on demand."""

    _config: Configuration = None

    @classmethod
    def get_config(cls, load_env=False):
        """Return the loaded configuration."""
        if not cls._config:
            cls._config = Configuration()
            if load_env:
                cls._config.load_environment()

        return cls._config
