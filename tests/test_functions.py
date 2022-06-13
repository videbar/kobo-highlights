"""Tests for the functionality in `functions.py`:

* test_query_bookmarks_from_ereader: Tests the querying of bookmarks from the erader
sqlite database.

* test_add_bookmark_to_md_new: Tests adding a bookmark to a new markdown file.

* test_add_bookmark_to_md_existing: Tests adding a bookmark to an existing markdown
file.

* test_query_bookmarks_from_markdown: Tests querying the bookmarks from markdown files.

* test_query_bookmarks_from_markdown_ignore: Tests that markdown files without a proper
name are ignored when querying the bookmarks.

* test_setup_missing_config: Tests the that a proper `Config` object is created when a
config file doesn't exists.
"""

# Imports:
from pathlib import Path
from unittest import mock
from unittest.mock import patch, mock_open

from rich.prompt import Confirm

from .references import (
    BOOKMARKS_TO_ADD,
    REFERENCE_MARKDOWN,
    BOOKMARKS_QUERIED_FROM_MD,
    EXPECTED_BOOKMARKS_SQLITE,
)
from kobo_highlights.functions import (
    setup_missing_config,
    query_bookmarks_from_ereader,
    query_bookmarks_from_markdown,
    add_bookmark_to_md,
)
from kobo_highlights.console import console
from kobo_highlights.config import Config, ConfigError


def test_query_bookmarks_from_ereader(tmp_path):
    """Tests the querying of bookmarks from the erader sqlite database. To do so, a
    pre-defined sqlite file is shipped with the tests (`KoboReader.sqlite`) as well as
    what the result of the querying should look like (`EXPECTED_BOOKMARKS_SQLITE`).
    """

    test_root: Path = Path(__file__).parent
    # fake ereader directory:
    sqlite_filepath: Path = test_root / "KoboReader.sqlite"

    # fake local dir for the copy of the database:
    local_dir: Path = tmp_path

    assert not (local_dir / "KoboReader.sqlite").is_file()

    queried_bookmarks: list[dict] = query_bookmarks_from_ereader(
        sqlite_filepath, local_dir
    )

    assert queried_bookmarks == EXPECTED_BOOKMARKS_SQLITE
    assert not (local_dir / "KoboReader.sqlite").is_file()


def test_add_bookmark_to_md_new(tmp_path):
    """Tests adding a bookmark to a new markdown file. This test uses the first bookmark
    contained in`bookmarks_to_add`. The resulting markdown text should be the first
    string from `REFERENCE_MARKDOWN`.
    """

    # Name of the markdown file from the bookmark characteristics.
    filename: str = (
        f"{BOOKMARKS_TO_ADD[0]['title']} - {BOOKMARKS_TO_ADD[0]['author']}.md"
    )
    filepath: Path = tmp_path / filename

    # When the markdown file doesn't previously exist, add_bookmark_to_md() uses the
    # method Path.write_text().
    with (
        patch.object(Path, "write_text") as mock_write_text,
        patch.object(Path, "is_file", return_value=False),
    ):

        assert not filepath.is_file()
        add_bookmark_to_md(BOOKMARKS_TO_ADD[0], tmp_path)
        mock_write_text.assert_called_once_with(REFERENCE_MARKDOWN[0])


def test_add_bookmark_to_md_existing(tmp_path):
    """Tests adding a bookmark to an existing markdown This test uses the second
    bookmark contained in`BOOKMARKS_TO_ADD`. The resulting markdown text should be the
    second string from `REFERENCE_MARKDOWN`.
    """

    filename: str = (
        f"{BOOKMARKS_TO_ADD[1]['title']} - {BOOKMARKS_TO_ADD[1]['author']}.md"
    )
    filepath: Path = tmp_path / filename
    # When the markdown file does already exist, add_bookmark_to_md() uses the method
    # Path.open() to open the file and then the write method from the file object.
    with (
        patch.object(Path, "open", mock_open()) as mocked_path_open,
        patch.object(Path, "is_file", return_value=True),
    ):

        assert filepath.is_file()
        add_bookmark_to_md(BOOKMARKS_TO_ADD[1], tmp_path)

        mocked_path_open.assert_called_once_with("a")
        mocked_path_open().write.assert_called_once_with(REFERENCE_MARKDOWN[1])


def test_query_bookmarks_from_markdown(tmp_path):
    """Tests querying the bookmarks from markdown files. This test uses the contents
    from `REFERENCE_MARKDOWN`, which should result in the bookmarks in
    `BOOKMARKS_QUERIED_FROM_MD`.
    """

    complete_markdown: str = REFERENCE_MARKDOWN[0] + REFERENCE_MARKDOWN[1]

    title: str = BOOKMARKS_QUERIED_FROM_MD[0]["title"]
    author: str = BOOKMARKS_QUERIED_FROM_MD[0]["author"]

    # According to convention.
    md_filename: str = f"{title} - {author}.md"
    md_filepath: Path = tmp_path / md_filename
    md_filepath.write_text(complete_markdown)

    queried_bookmarks = query_bookmarks_from_markdown(tmp_path)
    assert queried_bookmarks == BOOKMARKS_QUERIED_FROM_MD


def test_query_bookmarks_from_markdown_ignore(tmp_path):
    """Tests that markdown files without a proper name are ignored when querying the
    bookmarks. To do so three markdown files are created with slightly wrong names
    (according to the convention). The files contain proper bookmarks
    (from REFERENCE_MARKDOWN), but because of the filename they should be ignored by
    `query_bookmarks_from_markdown()`.
    """

    complete_markdown: str = REFERENCE_MARKDOWN[0] + REFERENCE_MARKDOWN[1]
    md_filenames: list[str] = [
        "title- author.md",
        "title -author.md",
        "title-author.md",
    ]

    for filename in md_filenames:
        md_filepath: Path = tmp_path / filename
        md_filepath.write_text(complete_markdown)

    queried_bookmarks = query_bookmarks_from_markdown(tmp_path)
    assert queried_bookmarks == []


def test_setup_missing_config(tmp_path):
    """Tests the that a proper `Config` object is created when a config file doesn't
    exists. Notably, this test doesn't test the inner logic from the `Config` class,
    that is done in `test_config.py`, here the entire functionality of `Config` is
    mocked.
    """

    ereader_dir: Path = tmp_path / "ereader"
    target_dir: Path = tmp_path / "target"
    config_filpath: Path = tmp_path / "config.toml"

    reference_config = Config(ereader_dir=ereader_dir, target_dir=target_dir)

    with (
        patch.object(Confirm, "ask", return_value=True) as mock_ask,
        patch.object(console, "print") as mock_print,
        patch.object(
            Config, "create_interactively", return_value=reference_config
        ) as mock_create_interactively,
    ):

        return_config = setup_missing_config(config_filpath)

        assert reference_config == return_config

        mock_ask.assert_called_once()
        mock_create_interactively.assert_called()
        mock_print.assert_called_once()
