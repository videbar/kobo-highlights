"""This module contains some logic that is require by the application but is not
directly related to the CLI. This includes:

* setup_config(): Called at the beginning of the program to ensure there's a proper
Config instance.

* query_bookmarks_from_ereader(): Query the ereader database to get a list of all the
bookmarks.

* query_bookmarks_from_markdown(): Simple function that looks for bookmarks on the
markdown whose filename matches the convention use by the program.
"""

# Imports:
from pathlib import Path
from shutil import copy
import sqlite3

import typer
from rich.prompt import Confirm
from rich.panel import Panel
from marko.ext.gfm import gfm
from bs4 import BeautifulSoup

from .config import Config, ConfigError
from .console import console, error_console


# Type alias:
Bookmark = dict[str, str]


# Functions:
def setup_config(config_path: Path) -> Config:
    """This function is used to set up the configuration object that is used by the
    program. It tries to find a valid configuration file and use to it to create
    the config object. If it fails to find a file, or if the file is not valid,
    it prompts the user to create a new config object interactively and it saves it
    as a config file.

    The function returns a config variable of the Config type. This variable is used
    as a singleton, although this behavior is not "enforced".

    Args:
        config_path (Path): Path to the config file.

    Raises:
        typer.Abort: In case the function finds an error that cannot be solved, it
        raises a typer.Abort to stop the program.
    """

    try:
        return Config.from_file(config_path)

    # If the config file can't be read, ask to create one interactively.
    except ConfigError:

        error_console.print("[bold]No valid configuration file was found")
        if Confirm("would you like to create one?"):

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

    The functions doesn't operate directly on the sqlite file, rather it creates a local
    copy and read from the copy. This way the program doesn't need to directly interact
    with the ereaderer database.

    Args:
        sqlite_filepath (Path): Path to the ereader sqlite database.

        copy_dir (Path): Directory where database is copied to.

    Returns:
        list[dict[str, str]]: List of bookmarks.
    """

    local_sqlite: Path = Path(copy(sqlite_filepath, copy_dir))

    connection: sqlite3.Connection = sqlite3.connect(local_sqlite)
    cursor: sqlite3.Cursor = connection.cursor()

    # Query string used on the "Bookmark" table.
    BM_QUERY: str = "SELECT UUID, Text, Annotation, VolumeID FROM 'Bookmark';"
    all_bookmarks: list[dict[str, str]] = []

    for bookmark_data in cursor.execute(BM_QUERY):

        current_bookmark: dict = {
            "id": bookmark_data[0],
            "text": bookmark_data[1],
            "annotation": bookmark_data[2],
        }

        # The author and title information are obtained from the "VolumeID", which is
        # simply the path to the .epub files. The author name can be obtained directly,
        # since it is the name of the parent folder of the .epub files.
        #
        # To obtain the book title in a proper format, the "content" table of the
        # database is queried. This table has a "BookID" column that matches the
        # "VolumeID" from the "Bookmark" table. It also has a column named "BookTitle"
        # that contains the title of the book.

        # The structure of the volume id is: file:///internal/path/author_name/book.epub
        volume_id: str = bookmark_data[3]
        current_bookmark["author"] = volume_id.rsplit("/", 2)[1]

        # Query string used on the "content" table.
        CONTENT_QUERY: str = (
            f"SELECT BookTitle FROM 'content' WHERE BookID = {volume_id} LIMIT 1;"
        )

        # The same book can appear multiple times on the "content" table, but in order
        # to retrieve the title there's no need to query more than one result.
        current_bookmark["title"] = cursor.execute(CONTENT_QUERY).fetchone()[0]

        all_bookmarks.append(current_bookmark)

    connection.close()
    # Delete local copy of the database.
    local_sqlite.unlink()
    return all_bookmarks


def query_bookmarks_from_markdown(dir_md_files: Path) -> list[Bookmark]:
    """This function reads all the markdown files in a given directory and extract
    bookmarks that were already exported. It first parses the markdown into html and
    then it uses beautiful soup to scrap the bookmarks.

    This is non-exhaustive basic parser, it only looks for markdown files with names
    that match the ones created by the program and extract all blockquotes from this.
    The bookmarks are consider to be the plaintext (no html tags) inside the
    blockquotes.

    This simple behaviour is enough for two reasons. First, this parser will only be
    used to check if the bookmarks queried from the ereader database are already stored
    as markdown, so false positives are not a problem. Second, the fact that when
    bookmarks are extracted from blockquotes only the plaintext is consider make it
    possible for users to, for example, emphasis the text in the bookmark without the
    parser noticing.

    Args:
        dir_md_files (Path): Directory containing the markdown files.

    Returns:
        list[dict[str, str]]: List of the bookmarks found.
    """

    all_bookmarks: list[dict[str, str]] = []

    # The regex used in glob() matches filenames corresponding to bookmark markdown
    # files.
    for md_filepath in dir_md_files.glob("* - *.md"):

        current_filename: str = md_filepath.stem

        # Used .rsplit(" - ", 1) instead of simply .split() in case a book title
        # contains the string " - ".
        current_title, current_author = current_filename.rsplit(" - ", 1)

        html_text: str = gfm(md_filepath.read_text())
        soup = BeautifulSoup(html_text)

        for blockquote in soup("blockquote"):
            current_bookmark = {
                "author": current_author,
                "title": current_title,
                # BeautifulSoup adds leading and trailing "\n" which need to be striped.
                "text": blockquote.text.strip("\n"),
            }

            all_bookmarks.append(current_bookmark)

    return all_bookmarks


# def add_bookmark_to_md_file(
# bookmark: Bookmark, md_dir: Path, reload_annotations: bool = False
# ):
#     """This function adds a bookmark queried from the ereader database to a markdown
#     file. The filename of the file follows the convention
#     `<book title> - <book author(s)>.md`. The text of the bookmark is added as a block
#     quote and the annotation is added as paragraphs underneath.

#     Args:
#         bookmark (dict[str, str]): The bookmark to be added. It has the keys `id`,
#         `text`, `annotation`, and `author`.

#         md_dir (Path): The path to the directory where the markdown files will be
#         stored.
#     """
#     file_name: str = f"{bookmark['title']} - {bookmark['author']}.md"

#     match bookmark:

#         case {"text": str() as text, "annotation": None}:
#             bm_text_to_md(bookmark, )

#         case {"text": str() as text, "annotation": str() as annotation}:
#             ...

#         case {"text": None, "annotation": None}:
#             pass

#         case _:
#             ...


# Format the text as a markdown blockquote.
# md_blockquote: str = f"> {bookmark['text']}".replace("\n", "\n> ")


def add_bookmark_text_to_md(bookmark: Bookmark, md_dir: Path):
    """This function adds a bookmark queried from the ereader database to a markdown
    file. The filename of the file follows the convention
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
    text_new_file: str = f"{md_blockquote}\n" "\n" f"{bookmark['annotation']}"

    text_existing_file: str = (
        "\n" "\n" "***\n" "\n" f"{md_blockquote}\n" "\n" f"{bookmark['annotation']}"
    )

    if md_filepath.is_file():

        with md_filepath.open("a") as md_file:
            md_file.write(text_existing_file)
    else:
        md_filepath.write_text(text_new_file)