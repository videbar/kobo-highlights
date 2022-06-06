# Imports:
from __future__ import annotations
from pathlib import Path

from pydantic import BaseModel, Extra, ValidationError, validate_arguments
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
import toml

from kobo_highlights.console import console


class Config(BaseModel, extra=Extra.forbid):
    target_dir: Path
    ereader_dir: Path

    @classmethod
    def from_file(cls, config_path: Path) -> Config:
        try:
            return cls.parse_obj(toml.load(config_path))

        except FileNotFoundError:
            raise ConfigError(f"No config file was found in: {config_path}")

        except (toml.TomlDecodeError, TypeError):
            raise ConfigError(f"The config file {config_path} is not a valid toml file")

        except ValidationError:
            raise ConfigError(
                f"The config file {config_path} is not a valid configuration file"
            )

    @classmethod
    def create_interactively(cls) -> Config:
        while True:
            ereader_input: str = Prompt.ask(
                "Please enter the absolute path where your [bold]ereader[/] is"
                " mounted",
                console=console,
            )

            target_input: str = Prompt.ask(
                "Please enter the absolute path to the [bold]target directory[/]"
                " where the highlights will be exported",
                console=console,
            )

            try:
                ereader_dir, target_dir = Path(ereader_input), Path(target_input)

            except TypeError:  # User input cannot be converted into path
                console.print("[prompt.invalid]The inputs entered are not paths")

            else:
                if ereader_dir.is_absolute() and target_dir.is_absolute():
                    config = cls(
                        target_dir=Path(target_input),
                        ereader_dir=Path(ereader_dir),
                    )

                    return config

                else:
                    console.print("[prompt.invalid]The paths entered are not absolute")

    def save_file(self, config_filepath: Path) -> Config:
        # Convert the path attributes to strings:
        toml_representation: dict[str, str] = {
            field: str(path) for field, path in self.dict().items()
        }

        with open(config_filepath, "w") as config_file:
            toml.dump(toml_representation, config_file)

        return self

    def __rich__(self) -> Table:
        """Required for rendering the config objects using Rich:
        https://rich.readthedocs.io/en/stable/protocol.html#console-customization
        """
        config_table = Table(box=None, show_header=False)

        config_table.add_row(
            "target_dir:",
            f"[cyan]{str(self.target_dir)}",
            "[bright_black]# Directory where your highlights will be exported ",
        )

        config_table.add_row(
            "ereader_dir:",
            f"[cyan]{str(self.ereader_dir)}",
            "[bright_black]# Directory where your ereader is mounted ",
        )
        return config_table


class ConfigError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
