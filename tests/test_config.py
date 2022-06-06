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


def test_from_file_correct(tmp_path):

    config_filepath: Path = tmp_path / "config.toml"
    config_filepath.write_text(CONFIG_FILE_CORRECT)

    target_dir = Path(CONFIG_FILE_CORRECT_PATHS["target_dir"])
    ereader_dir = Path(CONFIG_FILE_CORRECT_PATHS["ereader_dir"])

    read_config = Config.from_file(config_path=config_filepath)

    assert config_filepath.is_file()
    assert read_config.target_dir == target_dir
    assert read_config.ereader_dir == ereader_dir


def test_from_file_extra_fields(tmp_path):

    config_filepath: Path = tmp_path / "config.toml"
    config_filepath.write_text(CONFIG_FILE_EXTRA_FIELDS)

    assert config_filepath.is_file()
    with pytest.raises(ConfigError):
        read_config = Config.from_file(config_path=config_filepath)


def test_from_file_missing_fields(tmp_path):

    config_filepath: Path = tmp_path / "config.toml"
    config_filepath.write_text(CONFIG_FILE_MISSING_FIELDS)

    assert config_filepath.is_file()
    with pytest.raises(ConfigError):
        read_config = Config.from_file(config_path=config_filepath)


def test_from_file_no_file(tmp_path):

    config_filepath: Path = tmp_path / "config.toml"

    assert not config_filepath.is_file()
    with pytest.raises(ConfigError):
        read_config = Config.from_file(config_path=config_filepath)


def test_save_file(tmp_path):

    target_dir: Path = Path(CONFIG_FILE_CORRECT_PATHS["target_dir"])
    ereader_dir: Path = Path(CONFIG_FILE_CORRECT_PATHS["ereader_dir"])

    test_config: Config = Config(target_dir=target_dir, ereader_dir=ereader_dir)
    config_filepath: Path = tmp_path / "config.toml"

    test_config.save_file(config_filepath=config_filepath)
    assert toml.load(config_filepath) == CONFIG_FILE_CORRECT_PATHS
