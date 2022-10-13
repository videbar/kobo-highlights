"""Tests for the functionality in `functions.py`:

* test_query_bookmarks_from_ereader: Tests the querying of bookmarks from the erader
sqlite database.

* test_add_bookmark_to_md_new: Tests adding a bookmark to a new markdown file.

* test_add_bookmark_to_md_existing: Tests adding a bookmark to an existing markdown
file.

* test_query_bookmark_ids_from_json_correct: Test that the bookmark ids are properly
queried from the JSON file.

* test_query_bookmark_ids_from_json_no_file: Test that an empty list is returned when
no JSON file exists and that a JSON file is created.

* test_query_bookmark_ids_from_json_wrong_json: Test that, when the JSON file
doesn't have a valid structure and the user agrees, an empty list is returned and a new
empty file is created.

* test_query_bookmark_ids_from_json_no_dict: Test that, when the JSON file
does have a valid structure but it doesn't represent a dictionary and the user agrees,
an empty list is returned and a new empty file is created.

* test_query_bookmark_ids_from_json_wrong_key: Test that, when the JSON file
does have a valid structure, it does represent a dictionary, but the dictionary doesn't
use the key `imported_bookmark_ids` and the user agrees, an empty list is returned and
a new empty file is created.

* test_query_bookmark_ids_from_json_wrong_value: Test that, when the JSON file
does have a valid structure, it does represent a dictionary, the dictionary does
use the key `imported_bookmark_ids`, but the value is not a list, and the user agrees,
an empty list is returned and a new empty file is created.

* test_setup_missing_config: Tests the that a proper `Config` object is created when a
config file doesn't exists.
"""

# Imports:
from pathlib import Path
import json
from unittest import mock
from unittest.mock import patch, mock_open

from rich.prompt import Confirm

from .references import (
    BOOKMARKS_TO_ADD,
    REFERENCE_MARKDOWN,
    JSON_CONTENTS,
    WRONG_JSON_CONTENTS,
    EMPTY_JSON_CONTENTS,
    JSON_CONTENTS_NO_DICT,
    JSON_CONTENTS_WRONG_KEY,
    JSON_CONTENTS_WRONG_VALUE,
    BOOKMARK_IDS_FROM_JSON,
    EXPECTED_BOOKMARKS_SQLITE,
)
from kobo_highlights.functions import (
    setup_missing_config,
    query_bookmarks_from_ereader,
    query_bookmark_ids_from_json,
    write_bookmark_id_to_json,
    add_bookmark_to_md,
)
from kobo_highlights.console import console, error_console
from kobo_highlights.config import Config


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
    assert sqlite_filepath.is_file()

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


def test_query_bookmark_ids_from_json_correct(tmp_path):
    """Test that the bookmark ids are properly queried from the JSON file. The contents
    of the JSON file are stored in `JSON_CONTENTS` and the corresponding list of ids
    is `BOOKMARK_IDS_FROM_JSON`.
    """

    json_filepath: Path = tmp_path / ".imported_bookmarks.json"
    json_filepath.write_text(JSON_CONTENTS)

    assert json_filepath.is_file()
    import json

    json.loads(json_filepath.read_text())

    queried_ids: list = query_bookmark_ids_from_json(json_filepath)

    assert queried_ids == BOOKMARK_IDS_FROM_JSON


def test_query_bookmark_ids_from_json_no_file(tmp_path):
    """Test that an empty list is returned when no JSON file exists and that a JSON
    file is created. The json file path `tmp_path/.imported_bookmarks.json` should
    not be a file before the function is run. After executing the function, it should
    be a JSON file with the contents from `EMPTY_JSON_CONTENTS`.
    """
    json_filepath: Path = tmp_path / ".imported_bookmarks.json"

    assert not json_filepath.is_file()
    queried_ids: list = query_bookmark_ids_from_json(json_filepath)

    assert queried_ids == []
    assert json_filepath.is_file()
    assert json_filepath.read_text() == EMPTY_JSON_CONTENTS


def test_query_bookmark_ids_from_json_wrong_json(tmp_path):
    """Test that, when the JSON file doesn't have a valid structure and the user agrees,
    an empty list is returned and a new empty file is created. This test patches the
    `Confirm.ask` method to mimick the user approval. When the approval is given, the
    effect should be similar to calling the funciton without a JSON file.
    """

    json_filepath: Path = tmp_path / ".imported_bookmarks.json"
    json_filepath.write_text(WRONG_JSON_CONTENTS)

    with (
        patch.object(Confirm, "ask", return_value=True) as mock_ask,
        patch.object(error_console, "print") as mock_print,
    ):
        queried_ids: list = query_bookmark_ids_from_json(json_filepath)

        mock_print.assert_called_once()
        mock_ask.assert_called_once()
        assert queried_ids == []
        assert json_filepath.read_text() == EMPTY_JSON_CONTENTS


def test_query_bookmark_ids_from_json_no_dict(tmp_path):
    """Test that, when the JSON file does have a valid structure but it doesn't
    represent a dictionary and the user agrees, an empty list is returned and a new
    empty file is created. This test patches the `Confirm.ask` method to mimick the user
    approval. When the approval is given, the effect should be similar to calling the
    funciton without a JSON file.
    """

    json_filepath: Path = tmp_path / ".imported_bookmarks.json"
    json_filepath.write_text(JSON_CONTENTS_NO_DICT)

    with (
        patch.object(Confirm, "ask", return_value=True) as mock_ask,
        patch.object(error_console, "print") as mock_print,
    ):
        queried_ids: list = query_bookmark_ids_from_json(json_filepath)

        mock_print.assert_called_once()
        mock_ask.assert_called_once()
        assert queried_ids == []
        assert json_filepath.read_text() == EMPTY_JSON_CONTENTS


def test_query_bookmark_ids_from_json_wrong_key(tmp_path):
    """Test that, when the JSON file does have a valid structure, it does represent a
    dictionary, but the dictionary doesn't use the key `imported_bookmark_ids` and the
    user agrees, an empty list is returned and a new empty file is created. This test
    patches the `Confirm.ask` method to mimick the user approval. When the approval is
    given, the effect should be similar to calling the funciton without a JSON file.
    """

    json_filepath: Path = tmp_path / ".imported_bookmarks.json"
    json_filepath.write_text(JSON_CONTENTS_WRONG_KEY)

    with (
        patch.object(Confirm, "ask", return_value=True) as mock_ask,
        patch.object(error_console, "print") as mock_print,
    ):
        queried_ids: list = query_bookmark_ids_from_json(json_filepath)

        mock_print.assert_called_once()
        mock_ask.assert_called_once()
        assert queried_ids == []
        assert json_filepath.read_text() == EMPTY_JSON_CONTENTS


def test_query_bookmark_ids_from_json_wrong_value(tmp_path):
    """Test that, when the JSON file
    does have a valid structure, it does represent a dictionary, the dictionary does
    use the key `imported_bookmark_ids`, but the value is not a list, and the user
    agrees, an empty list is returned and a new empty file is created. This test patches
    the `Confirm.ask` method to mimick the user approval. When the approval is given,
    the effect should be similar to calling the funciton without a JSON file.
    """

    json_filepath: Path = tmp_path / ".imported_bookmarks.json"
    json_filepath.write_text(JSON_CONTENTS_WRONG_KEY)

    with (
        patch.object(Confirm, "ask", return_value=True) as mock_ask,
        patch.object(error_console, "print") as mock_print,
    ):
        queried_ids: list = query_bookmark_ids_from_json(json_filepath)

        mock_print.assert_called_once()
        mock_ask.assert_called_once()
        assert queried_ids == []
        assert json_filepath.read_text() == EMPTY_JSON_CONTENTS


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
