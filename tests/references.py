"""This simple module contains some reference variables used in the tests:

* CONFIG_FILE_CORRECT (str): Contents of a valid configuration file.

* CONFIG_FILE_CORRECT_PATHS (dict[str, str]): dictionary that contains a string
representation of the paths from `CONFIG_FILE_CORRECT`.

* CONFIG_FILE_EXTRA_FIELDS (str): Contents of a configuration file with extra extra
arguments.

* CONFIG_FILE_MISSING_FIELDS (str): Contents of a configuration file with missing
arguments.

* BOOKMARKS_TO_ADD (list[dict]): A list of bookmarks that, when imported to markdown,
would result in the REFERENCE_MARKDOWN document.

* REFERENCE_MARKDOWN (list): A list of reference markdown text that results from
importing the bookmarks in `BOOKMARKS_TO_ADD`. The list contains two markdown documents,
one corresponds to the first bookmark in `BOOKMARKS_TO_ADD` being imported and the
second one corresponds to the second bookmark in `BOOKMARKS_TO_ADD` being imported to a
file that already exists.

* BOOKMARKS_QUERIED_FROM_MD (list[dict]):  A list of how the two bookmarks in
`REFERENCE_MARKDOWN` should look when queried.

* EXPECTED_BOOKMARKS_SQLITE (list[dict]): A list of the bookmarks contained in the
sqlite file that ships with the tests (`KoboReader.sqlite`).
"""

CONFIG_FILE_CORRECT: str = (
    'ereader_dir = "/absolute/path/to/ereader"\n'
    'target_dir = "/absolute/path/to/markdown/dir"'
)
CONFIG_FILE_CORRECT_PATHS: dict[str, str] = {
    "ereader_dir": "/absolute/path/to/ereader",
    "target_dir": "/absolute/path/to/markdown/dir",
}
CONFIG_FILE_EXTRA_FIELDS: str = (
    'kobo_ereader_path = "/absolute/path/to/ereader"\n'
    'kobo_target_folder = "/absolute/path/to/markdown/dir"\n'
    'kobo_extra_path = "/this/path/should/not/exist"'
)
CONFIG_FILE_MISSING_FIELDS: str = 'kobo_ereader_path = "/absolute/path/to/ereader"'


BOOKMARKS_TO_ADD: list[dict] = [
    {
        "id": "11111111-111111111-11111111111111111",
        "text": "I am a bookmark with multiple lines.\nI continue here",
        "annotation": None,
        "author": "Author name with a -in the middle (no spaces)",
        "title": "Book title with a - in the middle",
    },
    {
        "id": "11111111-111111111-11111111111111111",
        "text": "I am a bookmark",
        "annotation": (
            "I am an annotation with multiple lines\n"
            "and multiple paragraphs:\n"
            "\n"
            "I continue here"
        ),
        "author": "Author name with a -in the middle (no spaces)",
        "title": "Book title with a - in the middle",
    },
]


REFERENCE_MARKDOWN = [
    "\n> I am a bookmark with multiple lines.\n> I continue here",
    (
        "\n"
        "\n"
        "***\n"
        "\n"
        "> I am a bookmark\n"
        "\n"
        "I am an annotation with multiple lines\n"
        "and multiple paragraphs:\n"
        "\n"
        "I continue here"
    ),
]


BOOKMARKS_QUERIED_FROM_MD: list[dict] = [
    {
        "text": "I am a bookmark with multiple lines.\nI continue here",
        "author": "Author name with a -in the middle (no spaces)",
        "title": "Book title with a - in the middle",
    },
    {
        "text": "I am a bookmark",
        "author": "Author name with a -in the middle (no spaces)",
        "title": "Book title with a - in the middle",
    },
]


# This list contains the bookmarks that are inside the reference sqlite file that is
# shipped with the tests and is used to test the sqlite query function.
EXPECTED_BOOKMARKS_SQLITE: list[dict] = [
    {
        "id": "709644b4-03cb-448c-8b55-06c63cc26308",
        "text": "normales",
        "annotation": None,
        "author": "Le Guin, Ursula K",
        "title": "La mano izquierda de la oscuridad",
    },
    {
        "id": "614009e0-8f62-4d25-9cef-6b3bc7224b6f",
        "text": "Tienes que llegar a creer que es inútil para poder practicarla.\n",
        "annotation": None,
        "author": "Le Guin, Ursula K",
        "title": "La mano izquierda de la oscuridad",
    },
    {
        "id": "b2c73ce6-4144-40d4-b924-9683db85c7c7",
        "text": (
            "Statements are instructions that perform some action and do not"
            " return a value. Expressions evaluate to a resulting value"
        ),
        "annotation": None,
        "author": "Klabnik, Steve & Nichols, Carol",
        "title": "The Rust Programming Language",
    },
    {
        "id": "464d0e9d-61cb-4a99-9399-34c586120124",
        "text": (
            "Rust’s enums are most similar to algebraic data types in functional"
            " languages, such as F#, OCaml, and Haskell."
        ),
        "annotation": None,
        "author": "Klabnik, Steve & Nichols, Carol",
        "title": "The Rust Programming Language",
    },
    {
        "id": "b570ddcf-7f70-4502-b340-b1e4c02d204c",
        "text": (
            "All programs have to manage the way they use a computer’s memory"
            " while running. Some languages have garbage collection that"
            " constantly looks for no longer used memory as the program runs;"
            " in other languages, the programmer must explicitly allocate and"
            " free the memory. "
        ),
        "annotation": None,
        "author": "Klabnik, Steve & Nichols, Carol",
        "title": "The Rust Programming Language",
    },
    {
        "id": "8b0e0173-6b3b-4bea-8361-175e259311df",
        "text": "numeral.",
        "annotation": "numeral",
        "author": "Lameres, Brock J",
        "title": "Introduction to Logic Circuits & Logic Design With Verilog",
    },
    {
        "id": "9abdd7f9-2bf3-46d5-b075-2a1867d0b3e9",
        "text": "nibble.",
        "annotation": "nibble",
        "author": "Lameres, Brock J",
        "title": "Introduction to Logic Circuits & Logic Design With Verilog",
    },
    {
        "id": "23547bce-8c37-44a6-a586-ae431b8f4def",
        "text": (
            "The leftmost bit in a binary number is called the Most Significant"
            " Bit (MSB). The rightmost bit in a binary number is called the Least"
            " Significant Bit (LSB)\n"
        ),
        "annotation": None,
        "author": "Lameres, Brock J",
        "title": "Introduction to Logic Circuits & Logic Design With Verilog",
    },
]
