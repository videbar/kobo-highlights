import typer
from pathlib import Path

app = typer.Typer()
APP_NAME = "kobo_highlights"

@app.command()
def add(filename: str):
    typer.echo("test 2")

@app.command()
def add_all():
    typer.echo("test 3")


def read_config(app_name) -> dict:
    """_summary_

    Args:
        app_name (_type_): _description_

    Returns:
        dict: _description_
    """

    config_dir: Path = Path(typer.get_app_dir(app_name)).resolve()
    with open(config_dir/"config.toml", "r") as config_file:
        config: dict = toml.load(config_file)

    return config