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
    add_bookmark_to_md,
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
    config_subcomand: str = typer.Argument(
        "show", help="Config action to execute (show, new)"
    )
):
    """This command is used to manage the program configuration. In supports two
    commands, "show" to see the current configuration and "new" to create a new
    configuration interactively.

    Args:
        command (str, optional): _description_. Defaults to typer.Option("show").
    """

    global config
    match config_subcomand:
        case "show":
            console.print(Panel(config, expand=False, title=str(CONFIG_PATH)))

        case "new":
            config = Config.create_interactively().save_file(CONFIG_PATH)
            console.print("[green]Configuration file created successfully")

        case _:
            error_console.print(f"Unknown option: {config_subcomand}")
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
def import_highlights(
    bookmark_selection: str = typer.Argument(
        "new",
        help="Selection of bookmarks to import, to see all valid options use --help",
    )
):
    """This command imports the bookmarks from the ereader to the markdown database. It
    can import all bookmarks, only the new bookmarks (default), or a subset of the
    bookmarks selected based on the bookmark id, the book title or the book author.

    Args:
        bookmark_selection: Bookmarks to be imported. Valid values are "all", "new",
        a bookmark ID, a list of bookmark IDs separated by spaces, a book title and
        a book author. Default is "new".
    """
    ereader_bookmarks: list[Bookmark] = query_bookmarks_from_ereader(
        SQLITE_PATH, APP_PATH
    )

    match bookmark_selection:

        case "new":

            md_bookmarks: list[Bookmark] = query_bookmarks_from_markdown(
                config.target_dir
            )

            # Filter the bookmark to print to include only those that are in the ereader
            # (er_bm) but not on the markdown files (md_bm).
            bookmarks_to_save = [
                bm_er
                for bm_er in ereader_bookmarks
                if not any(md_bm.items() <= bm_er.items() for md_bm in md_bookmarks)
            ]

            for bookmark in bookmarks_to_save:
                add_bookmark_to_md(bookmark, config.target_dir)

        case "all":
            for bookmark in ereader_bookmarks:
                add_bookmark_to_md(bookmark, config.target_dir)

        case _:

            # If the value is neither all nor new, the program checks in order if it is
            # a id, or a list of ids, a book title or a book author.

            all_ids, all_titles, all_authors = [], [], []

            for bookmark in ereader_bookmarks:
                all_ids.append(bookmark["id"])
                all_titles.append(bookmark["title"])
                all_authors.append(bookmark["author"])

            # Check first if it is a list of ids:
            selected_ids: list = bookmark_selection.split()
            if all(id in all_ids for id in selected_ids):

                for bookmark in ereader_bookmarks:
                    if bookmark["id"] in selected_ids:
                        add_bookmark_to_md(bookmark, config.target_dir)

            # Then check if it a book title:
            elif bookmark_selection in all_titles:
                for bookmark in ereader_bookmarks:
                    if bookmark["title"] == bookmark_selection:
                        add_bookmark_to_md(bookmark, config.target_dir)

            # Finally check if it is an author name:
            elif bookmark_selection in all_authors:
                for bookmark in ereader_bookmarks:
                    if bookmark["author"] == bookmark_selection:
                        add_bookmark_to_md(bookmark, config.target_dir)

            else:
                error_console.print(
                    f"Error: {bookmark_selection} does not identify a bookmark, try"
                    " using --help to see the valid values."
                )
