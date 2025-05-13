"""This module contains some logic that is require by the application but is not
directly related to the CLI. This includes:

* setup_missing_config(): Called at the beginning of the program when a valid config
file is not found

* query_bookmarks_from_ereader(): Query the ereader database to get a list of all the
bookmarks.

* query_bookmark_ids_from_json(): Read the IDs of the bookmarks that have been already
imported from the JSON file.

* write_bookmark_id_to_json(): Add a new ID to the JSON file if it's not already there.
"""

# Imports:
from pathlib import Path
from shutil import copy
import sqlite3
import json

import typer
from rich.prompt import Confirm
from rich.panel import Panel

from kobo_highlights.config import Config
from kobo_highlights.console import console, error_console


# Type alias:
Bookmark = dict[str, str | None]
Bookmark_id = str | None


# Functions:
def setup_missing_config(config_path: Path) -> Config:
    """This function called at the beginning of the program when a valid configuration
    file cannot be found. It asks the user to create a new `Config` object interactively
    and, if an object is created, it is used to create a new config file.

    Args:
        config_path (Path): Path where the config file will be created.

    Raises:
        typer.Abort: If the user doesn't want to create a `Config` object, or if the
        resulting configuration can't be saved as a config file, a `typer.Abort`
        exception is raised to stop the program.
    """

    error_console.print("[bold]No valid configuration file was found")
    if Confirm.ask("would you like to create one?"):
        try:
            config = Config.create_interactively().save_file(config_path)
            console.print(
                "[green]Configuration file created successfully:",
                Panel(config, expand=False),
                f"It has been saved in {config_path}",
            )
            return config

        except FileNotFoundError:
            error_console.print(
                "An error occurred and the configuration file could not be saved"
            )
            raise typer.Abort()

    else:
        error_console.print(
            "Kobo highlights can not work without a valid configuration file"
        )
        raise typer.Abort()


def query_bookmarks_from_ereader(
    sqlite_filepath: Path, copy_dir: Path
) -> list[Bookmark]:
    """Query the sqlite database from the ereader and produce a list of all the
    bookmarks. The list contains, for each bookmark, the universal unique identifier
    (UUID) of the bookmark, the book title and author, the highlighted text, and the
    annotations made.

    The function will only query the bookmarks with text. It is possible to have
    bookmarks without text, which correspond to pages which have been marked. This
    function ignores those.

    The function doesn't operate directly on the sqlite file, rather it creates a local
    copy and reads from the copy. This way the program doesn't need to directly interact
    with the ereaderer database.

    Args:
        sqlite_filepath (Path): Path to the ereader sqlite database.

        copy_dir (Path): Directory where the local copy of the database is created.

    Returns:
        list[dict[str, str | None]]: List of bookmarks.
    """

    try:
        local_sqlite: Path = Path(copy(sqlite_filepath, copy_dir))

    except FileNotFoundError:
        error_console.print(
            "Error: It was not possible to connect to the erader"
            " database. Make sure that is is connected and that your configuration is"
            " correct (run kh config show)."
        )
        raise typer.Abort()

    connection: sqlite3.Connection = sqlite3.connect(local_sqlite)
    # Two cursors are require since two tables of the same database will be queried
    # alternatively in a for loop.
    cursor_bookmark: sqlite3.Cursor = connection.cursor()
    cursor_content: sqlite3.Cursor = connection.cursor()

    # Query string used on the "Bookmark" table.
    BM_QUERY: str = (
        "SELECT UUID, Text, Annotation, VolumeID FROM Bookmark"
        " WHERE Text IS NOT NULL;"
    )
    all_bookmarks: list[Bookmark] = []

    for bookmark_data in cursor_bookmark.execute(BM_QUERY):
        current_bookmark: dict = {
            "id": bookmark_data[0],
            "text": bookmark_data[1].strip(),
            "annotation": bookmark_data[2],
        }

        # The author and title information are obtained from the "VolumeID", which is
        # simply the path to the .epub files.
        #
        # To obtain the book title and author, the "content" table of the database is
        # queried. This table has a "BookID" column that matches the "VolumeID" from the
        # "Bookmark" table. It also has a ContentType column that divides the entries
        # in the table in two, contentType = 6 and contentType = 9. For each book in
        # the ereader there's an entry in the content table with contentType = 6 which
        # contains the book title as "Title" and the author(s) as "Attribution".
        #
        # Before the author information is added, the " - " sub-strings are removed,
        # since they would conflict with the convention used by the program for
        # filenames. They are substituted by the string "-" (the spaces are removed).
        volume_id: str = bookmark_data[3]

        # Query string used on the "content" table.
        CONTENT_QUERY: str = (
            "SELECT Title, Attribution FROM content WHERE ContentID = ?"
            " AND ContentType = '6' LIMIT 1;"
        )

        # The same book can appear multiple times on the "content" table, but in order
        # to retrieve the data there's no need to query more than one result.
        content_query_result: tuple = cursor_content.execute(
            CONTENT_QUERY, (volume_id,)
        ).fetchone()

        current_bookmark["title"] = content_query_result[0]

        if queried_author := content_query_result[1]:
            current_bookmark["author"] = queried_author.replace(" - ", "-")
        else:
            current_bookmark["author"] = "Unknown author"

        all_bookmarks.append(current_bookmark)

    connection.close()
    # Delete local copy of the database.
    local_sqlite.unlink()
    return all_bookmarks


def query_bookmark_ids_from_json(json_filepath: Path) -> list[Bookmark_id]:
    """Read the IDs of the bookmarks that have been already imported from the JSON file.
    It tries to load the JSON file, and it checks the structure. If no JSON file is
    found, it will silently create one and it will return an empty list. If a JSON file
    is found but the structure is incorrect (invalid JSON structure or it doesn't
    contain a list of ids), it will ask the user if they want to create a new empty
    JSON file.

    Args:
        json_filepath (Path): Path to the JSON file.

    Raises:
        typer.Abort: If the structure of the JSON file is invalid an the user doesn't
        want to create a new one, this exception is raised to stop the program.

    Returns:
        list[Bookmark_id]: List of bookamrk IDs.
    """
    try:
        json_content: dict[str, list[Bookmark_id]] = json.loads(
            json_filepath.read_text(encoding="utf-8")
        )

        # The JSON file should correspond to a dictionary with the key
        # imported_bookmark_ids that contains a list. If the dictionary doesn't contain
        # the right key, a KeyError will be raised. If the key doesn't correspond to a
        # list, a TypeError will be raised. Both of this exceptions are catched bellow.
        if not isinstance(json_content["imported_bookmark_ids"], list):
            raise TypeError()

    # If no JSON file exists, create one.
    except FileNotFoundError:
        json_content: dict[str, list[Bookmark_id]] = {"imported_bookmark_ids": []}
        json_filepath.write_text(json.dumps(json_content), encoding="utf-8")

    # If there is a JSON file but the structure is wrong, the user will be asked if
    # they want to create a new one.
    except (json.decoder.JSONDecodeError, KeyError, TypeError):
        error_console.print(
            "The JSON file that tracks of the imported bookmarks doesn't have a valid"
            f" JSON structure:\n{json_filepath}"
        )

        if Confirm.ask(
            "Do you want to overwrite it (Kobo Highlights will forget which bookmarks"
            " you have already imported, but the content of the makdown files will not"
            " be deleted)",
            console=error_console,
        ):
            json_content: dict[str, list[Bookmark_id]] = {"imported_bookmark_ids": []}
            json_filepath.write_text(json.dumps(json_content), encoding="utf-8")

        else:
            raise typer.Abort()

    return json_content["imported_bookmark_ids"]


def write_bookmark_id_to_json(json_filepath: Path, id: Bookmark_id):
    """Add a new ID to the JSON file if it's not already there.

    Args:
        json_filepath (Path): Path to the JSON file.

        id (Bookmark_id): Bookmark ID to be added.
    """

    stored_ids: list[Bookmark_id] = query_bookmark_ids_from_json(json_filepath)
    if id not in stored_ids:
        stored_ids.append(id)

    json_filepath.write_text(
        json.dumps({"imported_bookmark_ids": stored_ids}), encoding="utf-8"
    )


def add_bookmark_to_md(bookmark: Bookmark, md_dir: Path):
    """This function adds a bookmark queried from the ereader database to a markdown
    file. The filename of the markdown file follows the convention
    `<book title> - <book author(s)>.md`.

    The bookmark is assumed to have a `text` key with a string value that represents the
    bookmarked text and an `annotation` key that possibly holds the annotation text.
    If there's no annotation text, it is assumed that the value of `annotation` is
    `None`.

    The text of the bookmark is added as a block quote and the annotation is added as
    paragraphs underneath.

    Args:
        bookmark (dict[str, str]): The bookmark to be added. It has the keys `id`,
        `text`, `annotation`, and `author`.

        md_dir (Path): The path to the directory where the markdown files will be
        stored.
    """

    md_filename: str = f"{bookmark['title']} - {bookmark['author']}.md"
    md_filepath: Path = md_dir / md_filename

    # Format the text as a markdown blockquote.
    md_blockquote: str = f"> {bookmark['text']}".replace("\n", "\n> ")

    # The format of the markdown text is a bit different depending on if it is creating
    # a new file or of it is appending the bookmarks to an already existing file.
    if annotation := bookmark["annotation"]:
        text_new_file: str = f"\n{md_blockquote}\n\n{annotation}"
        text_existing_file: str = f"\n\n***\n\n{md_blockquote}\n\n{annotation}"

    else:
        text_new_file: str = f"\n{md_blockquote}"
        text_existing_file: str = f"\n\n***\n\n{md_blockquote}"

    if md_filepath.is_file():
        with md_filepath.open("a", encoding="utf-8") as md_file:
            md_file.write(text_existing_file)

    else:
        md_filepath.write_text(text_new_file, encoding="utf-8")
