"""Tests for the `Config` class in `config.py`.

* test_from_file_correct(): Test the `from_file()` method with a valid config file.

* test_from_file_extra_fields(): Test the `from_file()` method with a config file with
extra fields.

* test_from_file_missing_fields(): Test the `from_file()` method with a config file with
missing fields.

* test_from_file_no_file():  Test the `from_file()` method when there's no config file
at all.

* test_save_file(): Test the `save_file()` method.
"""

# Imports
from pathlib import Path

import pytest
import toml

from kobo_highlights.config import Config, ConfigError
from .references import (
    CONFIG_FILE_CORRECT,
    CONFIG_FILE_CORRECT_PATHS,
    CONFIG_FILE_EXTRA_FIELDS,
    CONFIG_FILE_MISSING_FIELDS,
)


# Tests
def test_from_file_correct(tmp_path):
    """Test the `from_file()` method with a valid config file. This is done using the
    text in `CONFIC_FILE_CORRECT`, that should result in a `Config` object with the
    attributes from `CONFIG_FILE_CORRECT_PATHS`.
    """

    config_filepath: Path = tmp_path / "config.toml"
    config_filepath.write_text(CONFIG_FILE_CORRECT, encoding="utf-8")

    target_dir = Path(CONFIG_FILE_CORRECT_PATHS["target_dir"])
    ereader_dir = Path(CONFIG_FILE_CORRECT_PATHS["ereader_dir"])

    read_config = Config.from_file(config_path=config_filepath)

    assert config_filepath.is_file()
    assert read_config.target_dir == target_dir
    assert read_config.ereader_dir == ereader_dir


def test_from_file_extra_fields(tmp_path):
    """Test the `from_file()` method with a config file with extra fields. When a config
    file with extra field is used, `from_file()` should raise a `ConfigError`.
    """

    config_filepath: Path = tmp_path / "config.toml"
    config_filepath.write_text(CONFIG_FILE_EXTRA_FIELDS, encoding="utf-8")

    assert config_filepath.is_file()
    with pytest.raises(ConfigError):
        read_config = Config.from_file(config_path=config_filepath)


def test_from_file_missing_fields(tmp_path):
    """Test the `from_file()` method with a config file with missing fields. When a
    config file with missing field is used, `from_file()` should raise a `ConfigError`.
    """

    config_filepath: Path = tmp_path / "config.toml"
    config_filepath.write_text(CONFIG_FILE_MISSING_FIELDS, encoding="utf-8")

    assert config_filepath.is_file()
    with pytest.raises(ConfigError):
        read_config = Config.from_file(config_path=config_filepath)


def test_from_file_no_file(tmp_path):
    """Test the `from_file()` method when there's no config file at all. If the path
    passed to `from_file()` does not contain a file, it should raise a `ConfigError`.
    """

    config_filepath: Path = tmp_path / "config.toml"

    assert not config_filepath.is_file()
    with pytest.raises(ConfigError):
        read_config = Config.from_file(config_path=config_filepath)


def test_save_file(tmp_path):
    """Test the `save_file()` method. This is done using the paths in
    `CONFIG_FILE_CORRECT_PATHS`, that should correspond to a config file with the text
    in `CONFIC_FILE_CORRECT`.
    """

    target_dir: Path = Path(CONFIG_FILE_CORRECT_PATHS["target_dir"])
    ereader_dir: Path = Path(CONFIG_FILE_CORRECT_PATHS["ereader_dir"])

    test_config: Config = Config(target_dir=target_dir, ereader_dir=ereader_dir)
    config_filepath: Path = tmp_path / "config.toml"

    test_config.save_file(config_filepath=config_filepath)
    assert toml.load(config_filepath) == CONFIG_FILE_CORRECT_PATHS
