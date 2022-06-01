# Imports:
from pathlib import Path

import typer
from rich.prompt import Confirm
from rich.panel import Panel

from .config import Config, ConfigError
from .console import console, error_console
from .functions import setup_config

# Constants:
APP_NAME = "kobo_highlights"
CONFIG_PATH = Path(typer.get_app_dir(APP_NAME)) / "config.toml"

# Initial setup:
app = typer.Typer()
config = setup_config(CONFIG_PATH)


@app.command("config")
def config_command(
    option: str = typer.Option("show", help="Config action to execute (show, new)")
):
    """_summary_

    Args:
        command (str, optional): _description_. Defaults to typer.Option("show").

        help (str, optional): _description_. Defaults to "Config command to execute".
    """

    global config
    match option:
        case "show":
            console.print(Panel(config, expand=False, title=str(CONFIG_PATH)))

        case "new":
            config = Config.create_interactively().save_file(CONFIG_PATH)
            console.print("[green]Configuration file created successfully")

        case _:
            error_console.print(f"Unknown option: {option}")
            raise typer.Exit(1)

    pass


@app.command("ls")
def list_highlights(filename: str):
    typer.echo("test 2")


@app.command("import")
def import_highlights(filename: str):
    # import id, title, author, new, all
    ...
