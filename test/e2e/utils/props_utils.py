import os
from pathlib import Path

from tomllib import loads


def load_props():
    config_path = os.path.join("test", "e2e", "pinnwand.toml")
    return loads(Path(config_path).read_text())
