import os

from toml import load


def load_props():
    config_path = os.path.join("test", "e2e", "pinnwand.toml")
    return load(config_path)
