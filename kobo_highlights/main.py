import code
from .config import Config, ConfigError
from .console import console, error_console
import typer
from rich.prompt import Confirm
from rich.panel import Panel
from pathlib import Path

app = typer.Typer()
APP_NAME = "kobo_highlights"
CONFIG_PATH = Path(typer.get_app_dir(APP_NAME)) / "config.toml"

try:
    config = Config.from_file(CONFIG_PATH)

# If the config file can't be read, ask to create one interactively.
except ConfigError:
    console.print("[bold]No valid configuration file was found")
    if Confirm("would you like to create one?"):
        config = Config.create_interactively().save_file(CONFIG_PATH)
        console.print(
            "[green]Configuration file created successfully:",
            Panel(config, expand=False),
            f"It has been saved in {CONFIG_PATH}",
        )

    else:
        console.print("Kobo highlights can not work without a valid configuration file")
        raise typer.Abort()


@app.command("config")
def config_command(option: str = typer.Option("show", help="Config action to execute")):
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


@app.command("import")
def import_highlights(filename: str):
    typer.echo("test 2")


@app.command()
def add_all():
    typer.echo("test 3")
