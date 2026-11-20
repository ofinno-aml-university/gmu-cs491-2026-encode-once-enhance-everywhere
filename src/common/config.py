"""Read the project settings file."""

import tomllib
from pathlib import Path


def load_config(path):
    """Read the settings file TOML and return it as a dict"""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("rb") as config_file:
        return tomllib.load(config_file)


def get_rung_config(config, rung_id):
    """Return the settings for one rung or stop with a clear error"""
    for rung in config.get("rungs", []):
        if rung["rung_id"] == rung_id:
            return rung
    known = [rung["rung_id"] for rung in config.get("rungs", [])]
    raise KeyError(f"Rung {rung_id!r} is not in the config. Known rungs: {known}")
