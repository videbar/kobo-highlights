**DISCLAIMER:** This is an unofficial project that I developed independently from Kobo
and without any contact with them.

# Kobo highlights 

Kobo highlights is a simple CLI application to manage bookmarks from a Kobo erader. It
can import them into a markdown database where they can be easily accessed.

Kobo Highlights was developed in Python using [Typer](https://typer.tiangolo.com/) for
the CLI functionality and [Rich](https://github.com/Textualize/rich) for writing nice
text to the terminal.

Kobo highlights was develop as a personal project and it's design is based on how my
particular ereader handles bookmarks, so there are no guarantees that it will work on
other models.

# Requirements

Kobo highlights was developed and tested in [Fedora](https://getfedora.org/) and the
automatic tests are run in Ubuntu as macOS. I expect it to work properly on most
Linux distributions and on macOS. It has not been testes on Windows, but you can try
it.

Kobo highlights requires Python 3.10.

# Installation

This project was developed using [Poetry](https://python-poetry.org/) and there are
multiple ways of installing it:

* The recommended installation method is [downloading it from pypi](
    https://pypi.org/project/kobo-highlights/): `pip install kobo-highlights`.

* If you want to install Kobo Highlights directly from this repo note that development
takes place in the main branch, so make sure to install it from the commit corresponding
to the last release.
In this case you cant install it with Poetry (run `poetry install` inside the repo) or
with pip (run `pip install .` inside the repo).

# Quick guide

Once Kobo Highlights has been installed, it can be accessed running the `kh` command.
If you run `kh --help` you should see something like this:

From that message, you can see that the available options from Kobo Highlights are:

* `kh config` to manage your configuration.

* `kh ls` to list your bookmarks. By default is prints only new bookmarks, you can use
the `--all` option to print all bookmarks instead.

* `kh import` to import your bookmarks. It can be called with `all`, `new` (default),
a bookmark ID, a list of bookmarks IDs, a book title or a book author. Use
`kh import --help` for more information.

You can run any of these commands with the `--help` option to find out more on how to
use them.

The first time you run Kobo Highlights you will be probably told that you need to create
a configuration file before doing anything else. You can just follow the instructions
to create a valid configuration file. In the next section the program configuration is
explained in more detail.

# Configuration

Kobo Highlights uses a [toml](https://github.com/toml-lang/toml) configuration file that
is stored in the default directory 
[designated by Typer](https://typer.tiangolo.com/tutorial/app-dir/). In most Linux
systems this is in `~/.config/kobo_highlights`. The configuration file contains two
fields:

* `ereader_dir`: Is the absolute path to the directory where your erader is mounter.
Notably, your ereader doesn't need to be mounted when you create the config file,
but you should specify the directory where you expect it to be mounted when you manage
your bookmarks.

* `target_dir`: Is the absolute path to the directory where you want your markdown
database to be created. This database will contain one markdown file per book with
the highlighted text stored in block quotes.

Evert time you run Kobo Highlights it will try to find a configuration file, if it
fails, it will ask you if you want to create one interactively and save it. If you
don't want to create a configuration file, Kobo Highlights will stop.

You can manage your configuration file with the `kh config` command. In particular
you cant use `config show` to show your current configuration and `config new` to
create and save a new configuration.

# The markdown database

The main goal of Kobo highlights is to read the bookmarks from the ereader and format
them in a way in which they are easy to work with. I choose to do this by creating
a markdown database of the bookmarks. This database is located in the directory
specified in the configuration and will have a markdown file per book. The names
of these files follow the convention `<book title> - <book author(s)>.md`.

The markdown files will contain, for each bookmark in that book, a
[markdown block quote](https://spec.commonmark.org/0.30/#block-quotes) that contains
the text highlighted in the ereader potentially followed by a set of paragraphs
containing the possible annotations that were made about the highlighted text.

Note that Kobo highlights by default only imports new bookmarks to the markdown
database. To determine if a bookmark is already in the database, Kobo highlights creates
a hidden JSON file inside the markdown directory. Inside this hidden file Kobo
Highlights stores the IDs of the bookmarks that have already been imported. This means
that even if you modify the markdown files (or even delete the completely), Kobo
Highlights will  remember that bookmarks that you had imported and they will not be
considered new.