"""This module contains tests for the functionality in `functions.py`. It contains
the following tests:

* test_query_bookmarks_from_ereader: Tests the querying of bookmarks from the erader
sqlite database.

* test_add_bookmark_to_md_new: Tests adding a bookmark to a new markdown file.

* test_add_bookmark_to_md_existing: Tests adding a bookmark to an existing markdown
file.

* test_query_bookmarks_from_markdown: Tests querying the bookmarks from markdown files.

* test_query_bookmarks_from_markdown_ignore: Tests that markdown files without a proper
name are ignored when querying the bookmarks.

* test_setup_config_file_doesnt_exist: Tests the that a proper `Config` object is
created when a config file exists.

* test_setup_config_file_exist:Tests the that a proper `Config` object is created when a
config file doesn't exist.
"""

# Imports:
from pathlib import Path
from unittest.mock import patch, mock_open

from .references import (
    BOOKMARKS_TO_ADD,
    REFERENCE_MARKDOWN,
    BOOKMARKS_QUERIED_FROM_MD,
    EXPECTED_BOOKMARKS_SQLITE,
)
from kobo_highlights.functions import (
    setup_config,
    query_bookmarks_from_ereader,
    query_bookmarks_from_markdown,
    add_bookmark_to_md,
)
from kobo_highlights.config import Config, ConfigError


def test_query_bookmarks_from_ereader(tmp_path):
    """Use a pre-defined sqlite file shipped with the tests to check that the query
    functionality works as expected. The pytest temporary path `tmp_path` is used as
    the local directory in which the database is copied.
    """

    TEST_ROOT: Path = Path(__file__).parent
    # Fake ereader directory:
    SQLITE_FILEPATH: Path = TEST_ROOT / "KoboReader.sqlite"

    # Fake local dir for the copy of the database:
    LOCAL_DIR: Path = tmp_path

    assert not (LOCAL_DIR / "KoboReader.sqlite").is_file()

    queried_bookmarks: list[dict] = query_bookmarks_from_ereader(
        SQLITE_FILEPATH, LOCAL_DIR
    )

    assert queried_bookmarks == EXPECTED_BOOKMARKS_SQLITE
    assert not (LOCAL_DIR / "KoboReader.sqlite").is_file()


def test_add_bookmark_to_md_new(tmp_path):
    """Test adding bookmarks to a markdown file that doesn't previously exist. This test
    uses the first bookmark contained in`BOOKMARKS_TO_ADD`. The resulting markdown text
    should be the first string from `REFERENCE_MARKDOWN`.

    The function is called on a mocked file and then it is checked that the proper
    write methods were called with the markdown content from `REFERENCE_MARKDOWN`.
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
    """Test adding bookmarks to a markdown file that already exists. This test uses the
    second bookmark contained in`BOOKMARKS_TO_ADD`. The resulting markdown text
    should be the second string from `REFERENCE_MARKDOWN`.

    The function is called on a mocked file and then it is checked that the proper
    write methods were called with the markdown content from `REFERENCE_MARKDOWN`.
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
    """Test that bookmarks are properly queried from markdown documents. To do so,
    a markdown file is created under the temporal path `tmp_path` with the contents
    from `REFERENCE_MARKDOWN`.

    The function `query_bookmarks_from_markdown()` is then applied and the results are
    compared with the reference `BOOKMARKS_QUERIED_FROM_MD`.
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
    """Test that the function `query_bookmarks_from_markdown` ignores files without
    the right filename. To do so three markdown files are created under the temporal
    path `tmp_path` with slightly wrong names (according to the convention). The files
    contain proper bookmarks (from REFERENCE_MARKDOWN), but because of the filename
    they should be ignored by `query_bookmarks_from_markdown`.
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


def test_setup_config_file_doesnt_exist(tmp_path):
    """Test that the function `setup_config()` produces a proper config object when
    the config file doesn't exists. Notably, this test doesn't test the inner logic from
    the `Config` class, that is done in `test_config.py`, here the entire functionality
    of `Config` is mocked.
    """

    ereader_dir: Path = tmp_path / "ereader"
    target_dir: Path = tmp_path / "target"
    config_filpath: Path = tmp_path / "config.toml"

    return_config = Config(ereader_dir=ereader_dir, target_dir=target_dir)

    with (
        patch.object(Config, "from_file") as mock_config_from_file,
        patch.object(Config, "create_interactively", return_value=return_config),
    ):

        mock_config_from_file.side_effect = ConfigError("No config file")
        assert setup_config(config_filpath) == return_config
