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

# Installation

This project was developed using [Poetry](https://python-poetry.org/) and there are
multiple ways of installing it:

* Simply download it from pypi: `pip install kobo-highlights`.

* Install it with Poetry by cloning this repo and running `poetry install` inside it.
Note that you must have poetry installed.

* Install it from the repo using pip by cloning the repo and, inside it, running
`pip install .`

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
