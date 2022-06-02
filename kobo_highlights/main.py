# Imports:
from pathlib import Path

import typer
from rich.panel import Panel
from rich.table import Table
from rich import box

from .config import Config
from .console import console, error_console
from .functions import (
    setup_config,
    query_bookmarks_from_ereader,
    query_bookmarks_from_markdown,
    add_bookmark_text_to_md,
)

# Type alias:
Bookmark = dict[str, str]

# Initial setup:
APP_NAME: str = "kobo_highlights"
APP_PATH: Path = Path(typer.get_app_dir(APP_NAME))
CONFIG_PATH: Path = APP_PATH / "config.toml"

app = typer.Typer()
config: Config = setup_config(CONFIG_PATH)
SQLITE_PATH: Path = config.ereader_dir / ".kobo/KoboReader.sqlite"


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
def list_highlights(new: bool = typer.Option(False, help="Show only new bookmarks")):
    """This command prints a table with the bookmarks stored in the ereader. By default
    it prints all bookmarks, if the --new option is used, it will only show the
    bookmarks that are not already imported to the markdown database.

    Options:
        --new: Show only new bookmarks, instead of all of them.
    """

    bookmarks_to_print: list[Bookmark] = query_bookmarks_from_ereader(
        SQLITE_PATH, APP_PATH
    )

    if new:
        md_bookmarks: list[Bookmark] = query_bookmarks_from_markdown(config.target_dir)
        # Filter the bookmark to print to include only those that are in the ereader
        # (er_bm) but not on the markdown files (md_bm).
        bookmarks_to_print = [
            bm_er
            for bm_er in bookmarks_to_print
            if not any(md_bm.items() <= bm_er.items() for md_bm in md_bookmarks)
        ]

        # Used for the table printed to the terminal.
        title_str: str = "New bookmarks in your ereader"
    else:
        title_str: str = "All bookmarks in your ereader"

    bm_table: Table = Table(title=title_str, box=box.ROUNDED, show_lines=True)

    bm_table.add_column("ID", justify="center", style="green")
    bm_table.add_column("Book title", justify="center", style="cyan")
    bm_table.add_column("Book author", justify="center", style="cyan")
    bm_table.add_column("Highlighted text", justify="center", style="cyan")
    bm_table.add_column("Annotation", justify="center", style="cyan")

    for bookmark in bookmarks_to_print:
        bm_table.add_row(
            bookmark["id"],
            bookmark["title"],
            bookmark["author"],
            bookmark["text"],
            bookmark["annotation"],
        )

    console.print(bm_table)


@app.command("import")
def import_highlights(filename: str):
    # import id, title, author, new, all
    ...
