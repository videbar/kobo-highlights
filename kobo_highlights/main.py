"""This module contains the typer app (the CLI app) and the definitions for all the
programs commands.
"""

# Imports:
from pathlib import Path

import typer
from rich.panel import Panel
from rich.table import Table
from rich import box

from kobo_highlights.config import Config, ConfigError
from kobo_highlights.console import console, error_console
from kobo_highlights.functions import (
    setup_missing_config,
    query_bookmarks_from_ereader,
    query_bookmark_ids_from_json,
    write_bookmark_id_to_json,
    add_bookmark_to_md,
)

# Type alias:
Bookmark = dict[str, str | None]
Bookmark_id = str | None

# Main typer app:
app = typer.Typer(
    help=(
        "Kobo Highlights is a CLI application to manage the bookmarks of your Kobo"
        " ereader. It can import them into a human-friendly markdown database."
    )
)
# config subcommands:
config_app = typer.Typer(help="Manage the program configuration.")
app.add_typer(config_app, name="config")


# Initial setup:
@app.callback()
def setup():
    # Global variables:
    global APP_PATH
    global CONFIG_PATH
    global config
    global SQLITE_PATH
    global JSON_PATH

    APP_NAME: str = "kobo_highlights"
    APP_PATH = Path(typer.get_app_dir(APP_NAME))
    CONFIG_PATH = APP_PATH / "config.toml"

    try:
        config = Config.from_file(CONFIG_PATH)

    # If the config file can't be read, ask to create one interactively.
    except ConfigError:
        config = setup_missing_config(CONFIG_PATH)
        raise typer.Exit()

    SQLITE_PATH = config.ereader_dir / ".kobo/KoboReader.sqlite"
    JSON_PATH = config.target_dir / ".imported_bookmarks.json"


@app.command("ls")
def list_highlights(all: bool = typer.Option(False, help="Show all bookmarks")):
    """Print the bookmarks stored in the erader.

    By default it prints only new bookmarks, if the --all option is used, it will show
    all the bookmarks in the erader instead.
    """

    bookmarks_to_print: list[Bookmark] = query_bookmarks_from_ereader(
        SQLITE_PATH, APP_PATH
    )

    if not all:
        # IDs of the bookmarks that have already been imported.
        md_bookmarks_ids: list[Bookmark_id] = query_bookmark_ids_from_json(JSON_PATH)

        # Filter the bookmark to print to include only those that are in the ereader
        # but not on the markdown files.
        bookmarks_to_print = [
            bm for bm in bookmarks_to_print if bm["id"] not in md_bookmarks_ids
        ]

        # Used for the table printed to the terminal.
        title_str: str = "New bookmarks in your ereader"

    else:
        title_str: str = "All bookmarks in your ereader"

    if not bookmarks_to_print:
        console.print(
            'No Bookmarks to show (you can use "kh ls --all" to print all bookmarks)'
        )

    else:
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
        help=(
            'Selection of bookmarks to import, it can be "new", "all", a bookmark id,'
            " a list of bookmarks ids, a book title or a book author."
        ),
    )
):
    """Import the bookmarks from the ereader to the markdown database.

    It is possible to import all bookmarks, only the new bookmarks (default), or a
    subset of the bookmarks selected based on the bookmark id, the book title or the
    book author.
    """
    ereader_bookmarks: list[Bookmark] = query_bookmarks_from_ereader(
        SQLITE_PATH, APP_PATH
    )

    match bookmark_selection:

        case "new":

            md_bookmarks_ids: list[Bookmark_id] = query_bookmark_ids_from_json(
                JSON_PATH
            )

            # Filter the bookmarks to import only those that are in the ereader but
            # not on the markdown files.
            bookmarks_to_save = [
                bm for bm in ereader_bookmarks if bm["id"] not in md_bookmarks_ids
            ]

            for bookmark in bookmarks_to_save:
                add_bookmark_to_md(bookmark, config.target_dir)
                write_bookmark_id_to_json(JSON_PATH, bookmark["id"])

            console.print("[green]All new Bookmarks have been imported")

        case "all":
            for bookmark in ereader_bookmarks:
                add_bookmark_to_md(bookmark, config.target_dir)
                write_bookmark_id_to_json(JSON_PATH, bookmark["id"])

            console.print("[cyan]All Bookmarks have been imported")

        case _:

            # If the value is neither all nor new, the program checks in order to see if
            # it is an id, a list of ids, a book title, or a book author.

            all_ids, all_titles, all_authors = [], [], []

            for bookmark in ereader_bookmarks:
                all_ids.append(bookmark["id"])
                all_titles.append(bookmark["title"])
                all_authors.append(bookmark["author"])

            # Check first if the input is composed of ids:
            selected_ids: list = bookmark_selection.split()
            if all(id in all_ids for id in selected_ids):

                for bookmark in ereader_bookmarks:
                    if bookmark["id"] in selected_ids:
                        add_bookmark_to_md(bookmark, config.target_dir)
                        write_bookmark_id_to_json(JSON_PATH, bookmark["id"])

                # To print to the console:
                id_list_to_print: str = "\n".join(selected_ids)
                console.print(
                    "[green]The following bookmarks have been imported:\n"
                    f"[yellow]{id_list_to_print}"
                )

            # Then check if it a book title:
            elif bookmark_selection in all_titles:
                for bookmark in ereader_bookmarks:
                    if bookmark["title"] == bookmark_selection:
                        add_bookmark_to_md(bookmark, config.target_dir)
                        write_bookmark_id_to_json(JSON_PATH, bookmark["id"])
                console.print(
                    f"[green]All bookmarks from the book {bookmark_selection} have"
                    " been imported"
                )

            # Finally check if it is an author name:
            elif bookmark_selection in all_authors:
                for bookmark in ereader_bookmarks:
                    if bookmark["author"] == bookmark_selection:
                        add_bookmark_to_md(bookmark, config.target_dir)
                        write_bookmark_id_to_json(JSON_PATH, bookmark["id"])
                console.print(
                    f"[green]All bookmarks from the Author {bookmark_selection} have"
                    " been imported"
                )

            else:
                error_console.print(
                    f"Error: {bookmark_selection} does not identify a bookmark, try"
                    " using --help to see the valid values."
                )


@config_app.command("show")
def show_config():
    """Show the current program configuration."""
    global config
    console.print(Panel(config, expand=False))


@config_app.command("new")
def new_config():
    """Create a new configuration interactively and save it."""
    global config
    global CONFIG_PATH
    config = Config.create_interactively().save_file(CONFIG_PATH)
    console.print("[green]Configuration file created successfully")
