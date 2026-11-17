"""Tests for reading the settings file."""

import pytest

from common.config import get_rung_config, load_config

SETTINGS = """
[encoder]
preset = "medium"

[[rungs]]
rung_id = "480p"
height = 480
target_bitrate_kbps = 600
"""


def test_load_config_reads_toml(tmp_path):
    path = tmp_path / "config.file"
    path.write_text(SETTINGS)
    config = load_config(path)
    assert config["encoder"]["preset"] == "medium"


def test_load_config_missing_file_gives_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nope.file")


def test_get_rung_config_finds_and_rejects(tmp_path):
    path = tmp_path / "config.file"
    path.write_text(SETTINGS)
    config = load_config(path)
    assert get_rung_config(config, "480p")["height"] == 480
    with pytest.raises(KeyError):
        get_rung_config(config, "1080p")
