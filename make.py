#!/usr/bin/env python3
"""
Build script to simplify running:

* Tests
* Code quality checks
* Documentation builds

For help, see the following:

* CONTRIBUTING.md
* The output of python make.py --help
"""
from __future__ import annotations

import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from shutil import rmtree, which
from typing import Generator, Union

PathLike = Union[Path, str, bytes]


def _resolve(p: PathLike, strict: bool = False) -> Path:
    return Path(p).expanduser().resolve(strict=strict)


PROJECT_ROOT = _resolve(Path(__file__).parent, strict=True)


# General sphinx state / options
SPHINX_OPTS = []
SPHINX_BUILD = "sphinx-build"
SPHINX_AUTOBUILD = "sphinx-autobuild"
PAPER_SIZE = None
DOC_DIR = "doc"
BUILD_DIR = "build"


# Used for user output; relative to project root
FULL_DOC_DIR = PROJECT_ROOT / DOC_DIR
# FULL_BUILD_PREFIX = f"{DOCDIR}/{BUILDDIR}"
FULL_BUILD_DIR = PROJECT_ROOT / BUILD_DIR


# Linting
RUFF = "ruff"
RUFFOPTS = ["check"]
RUFFOPTS_ISORT = ["check", "--select", "I"]
RUFFOPTS_PACKAGE = "arcade"
MYPY = "mypy"
MYPYOPTS = ["arcade"]
PYRIGHT = "pyright"
PYRIGHTOPTS = []
BLACK = "black"
BLACKOPTS = ["arcade"]
ISORTOPTS = ["check", "--select", "I"]

# Testing
PYTEST = "pytest"
TESTDIR = "tests"
UNITTESTS = TESTDIR + "/unit"

# Internal variables.
PAPER_SIZE_OPTS = {}
PAPER_SIZE_OPTS[None] = []
PAPER_SIZE_OPTS["a4"] = ["-D", "latex_paper_size=a4"]
PAPER_SIZE_OPTS["letter"] = ["-D", "latex_paper_size=letter"]
ALLSPHINXOPTS = ["-d", f"{BUILD_DIR}/doctrees", *PAPER_SIZE_OPTS[PAPER_SIZE], *SPHINX_OPTS, DOC_DIR]
SPHINXAUTOBUILDOPTS = ["--watch", "../arcade", "--ignore", "./example_code/how_to_examples/thumbs"]

# Important: the i18n builder cannot share the environment and doctrees with the others
# This allows for internationalization / localization of doc.
I18NSPHINXOPTS = [*PAPER_SIZE_OPTS[PAPER_SIZE], *SPHINX_OPTS, "."]


# User-friendly check for dependencies and binaries
binaries = ["sphinx-build", "sphinx-autobuild"]
libraries = ["typer"]
for binary in binaries:
    not_found = [binary for binary in binaries if which(binary) is None]
    if not_found:
        print("Command-line tools not found: " + ", ".join(not_found))
        print(
            "Did you forget to install them with `pip`?  See CONTRIBUTING.md file for instructions."
        )
        exit(1)
for library in libraries:

    def find(library):
        try:
            __import__(library)
            return True
        except:
            pass

    not_found = [library for library in libraries if not find(library)]
    if not_found:
        print("Python dependencies not found: " + ", ".join(not_found))
        print(
            "Did you forget to install them with `pip`?  See CONTRIBUTING.md file for instructions."
        )
        exit(1)


import typer

app = typer.Typer()


@contextmanager
def cd_context(directory: PathLike) -> Generator[Path, None, None]:
    """
    Temporarily move into a directory and back after, regardless of exceptions

    Yields the current directory if successful. If `directory` is not found,
    a FileNotFoundError will be raised. If the path exists but is a file,
    a ValueError will be raised.

    Args:
        directory: The directory to cd into.
    """

    # Raise FileNotFoundError if path doesn't exist
    new_dir = _resolve(directory, strict=True)

    if not new_dir.is_dir():
        raise ValueError("Path must be a directory, not a file")

    _original_dir = _resolve(Path.cwd())

    # Change into the directory and yield the name
    try:
        os.chdir(new_dir)
        yield new_dir

    # Restore the old directory in an exception-resistant manner
    finally:
        os.chdir(_original_dir)


def run(args: str | list[str], cd: PathLike | None = None) -> None:
    """
    Try to run `args` with subprocess, switching into & out of `cd` if provided.

    Switching back out should occur regardless of any exceptions, unless the
    interpreter crashes.

    Args:
        args: the command to run.
        cd: a directory to switch into beforehand, if any.
    """
    if cd is not None:
        with cd_context(_resolve(cd, strict=True)):
            result = subprocess.run(args)
    else:
        result = subprocess.run(args)

    if result.returncode != 0:
        exit(result.returncode)


def run_doc(args: str | list[str]) -> None:
    run(args, cd=PROJECT_ROOT)


@app.command(rich_help_panel="Docs")
def clean():
    """
    Delete built website files.
    """
    if os.path.exists(FULL_BUILD_DIR):
        for item in Path(FULL_BUILD_DIR).glob("*"):
            os.remove(item) if os.path.isfile(item) else rmtree(item)


@app.command(rich_help_panel="Docs")
def html():
    """
    to make standalone HTML files
    """
    run_doc([SPHINX_BUILD, "-b", "html", *ALLSPHINXOPTS, f"{BUILD_DIR}/html"])
    print()
    print(f"Build finished. The HTML pages are in {FULL_BUILD_DIR}/html.")


@app.command(rich_help_panel="Docs")
def serve():
    """
    Build and serve standalone HTML files, with automatic rebuilds and live reload.
    """
    run_doc(
        [SPHINX_AUTOBUILD, *SPHINXAUTOBUILDOPTS, "-b", "html", *ALLSPHINXOPTS, f"{BUILD_DIR}/html"]
    )


@app.command(rich_help_panel="Additional Doc Formats")
def dirhtml():
    """
    to make HTML files named index.html in directories
    """
    run_doc([SPHINX_BUILD, "-b", "dirhtml", *ALLSPHINXOPTS, f"{BUILD_DIR}/dirhtml"])
    print()
    print(f"Build finished. The HTML pages are in {FULL_BUILD_DIR}/dirhtml.")


@app.command(rich_help_panel="Additional Doc Formats")
def singlehtml():
    """
    to make a single large HTML file
    """
    run_doc([SPHINX_BUILD, "-b", "singlehtml", *ALLSPHINXOPTS, f"{BUILD_DIR}/singlehtml"])
    print()
    print(f"Build finished. The HTML page is in {FULL_BUILD_DIR}/singlehtml.")


@app.command(rich_help_panel="Additional Doc Formats")
def pickle():
    """
    to make pickle files
    """
    run_doc([SPHINX_BUILD, "-b", "pickle", *ALLSPHINXOPTS, f"{BUILD_DIR}/pickle"])
    print()
    print("Build finished; now you can process the pickle files.")


@app.command(rich_help_panel="Additional Doc Formats")
def json():
    """
    to make JSON files
    """
    run_doc([SPHINX_BUILD, "-b", "json", *ALLSPHINXOPTS, f"{BUILD_DIR}/json"])
    print()
    print("Build finished; now you can process the JSON files.")


@app.command(rich_help_panel="Additional Doc Formats")
def htmlhelp():
    """
    to make HTML files and a HTML help project
    """
    run_doc([SPHINX_BUILD, "-b", "htmlhelp", *ALLSPHINXOPTS, f"{BUILD_DIR}/htmlhelp"])
    print()
    print(
        "Build finished; now you can run HTML Help Workshop with the"
        + f".hhp project file in {FULL_BUILD_DIR}/htmlhelp."
    )


@app.command(rich_help_panel="Additional Doc Formats")
def qthelp():
    """
    to make HTML files and a qthelp project
    """
    run_doc([SPHINX_BUILD, "-b", "qthelp", *ALLSPHINXOPTS, f"{BUILD_DIR}/qthelp"])
    print()
    print(
        'Build finished; now you can run "qcollectiongenerator" with the'
        + f".qhcp project file in {FULL_BUILD_DIR}/qthelp, like this:"
    )
    print(f"# qcollectiongenerator {FULL_BUILD_DIR}/qthelp/Arcade.qhcp")
    print("To view the help file:")
    print(f"# assistant -collectionFile {FULL_BUILD_DIR}/qthelp/Arcade.qhc")


@app.command(rich_help_panel="Additional Doc Formats")
def applehelp():
    """
    to make an Apple Help Book
    """
    run_doc([SPHINX_BUILD, "-b", "applehelp", *ALLSPHINXOPTS, f"{BUILD_DIR}/applehelp"])
    print()
    print(f"Build finished. The help book is in {FULL_BUILD_DIR}/applehelp.")
    print(
        "N.B. You won't be able to view it unless you put it in"
        + "~/Library/Documentation/Help or install it in your application"
        + "bundle."
    )


@app.command(rich_help_panel="Additional Doc Formats")
def devhelp():
    """
    to make HTML files and a Devhelp project
    """
    home = Path.home().expanduser().resolve(strict=True)
    run_doc([SPHINX_BUILD, "-b", "devhelp", *ALLSPHINXOPTS, f"{BUILD_DIR}/devhelp"])
    print()
    print("Build finished.")
    print("To view the help file:")
    print(f"# mkdir -p {home}/.local/share/devhelp/Arcade")
    print(f"# ln -s {FULL_BUILD_DIR}/devhelp {home}/.local/share/devhelp/Arcade")
    print("# devhelp")


@app.command(rich_help_panel="Additional Doc Formats")
def epub():
    """
    to make an epub
    """
    run_doc([SPHINX_BUILD, "-b", "epub", *ALLSPHINXOPTS, f"{BUILD_DIR}/epub"])
    print()
    print(f"Build finished. The epub file is in {FULL_BUILD_DIR}/epub.")


@app.command(rich_help_panel="Additional Doc Formats")
def latex():
    """
    to make LaTeX files, you can set PAPER_SIZE=a4 or PAPER_SIZE=letter
    """
    run_doc([SPHINX_BUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILD_DIR}/latex"])
    print()
    print(f"Build finished; the LaTeX files are in {FULL_BUILD_DIR}/latex.")
    print(
        "Run `make' in that directory to run these through (pdf)latex"
        + "(use `make latexpdf' here to do that automatically)."
    )


@app.command(rich_help_panel="Additional Doc Formats")
def latexpdf():
    """
    to make LaTeX files and run them through pdflatex
    """
    run_doc([SPHINX_BUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILD_DIR}/latex"])
    print("Running LaTeX files through pdflatex...")
    run_doc(["make", "-C", f"{BUILD_DIR}/latex", "all-pdf"])
    print(f"pdflatex finished; the PDF files are in {FULL_BUILD_DIR}/latex.")


@app.command(rich_help_panel="Additional Doc Formats")
def latexpdfja():
    """
    to make LaTeX files and run them through platex/dvipdfmx
    """
    run_doc([SPHINX_BUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILD_DIR}/latex"])
    print("Running LaTeX files through platex and dvipdfmx...")
    run_doc(["make", "-C", f"{BUILD_DIR}/latex", "all-pdf-ja"])
    print(f"pdflatex finished; the PDF files are in {FULL_BUILD_DIR}/latex.")


@app.command(rich_help_panel="Additional Doc Formats")
def text():
    """
    to make text files
    """
    run_doc([SPHINX_BUILD, "-b", "text", *ALLSPHINXOPTS, f"{BUILD_DIR}/text"])
    print()
    print(f"Build finished. The text files are in {FULL_BUILD_DIR}/text.")


@app.command(rich_help_panel="Additional Doc Formats")
def man():
    """
    to make manual pages
    """
    run_doc([SPHINX_BUILD, "-b", "man", *ALLSPHINXOPTS, f"{BUILD_DIR}/man"])
    print()
    print(f"Build finished. The manual pages are in {FULL_BUILD_DIR}/man.")


@app.command(rich_help_panel="Additional Doc Formats")
def texinfo():
    """
    to make Texinfo files
    """
    run_doc([SPHINX_BUILD, "-b", "texinfo", *ALLSPHINXOPTS, f"{BUILD_DIR}/texinfo"])
    print()
    print(f"Build finished. The Texinfo files are in {FULL_BUILD_DIR}/texinfo.")
    print(
        "Run `make' in that directory to run these through makeinfo"
        + "(use `make info' here to do that automatically)."
    )


@app.command(rich_help_panel="Additional Doc Formats")
def info():
    """
    to make Texinfo files and run them through makeinfo
    """
    run_doc([SPHINX_BUILD, "-b", "texinfo", *ALLSPHINXOPTS, f"{BUILD_DIR}/texinfo"])
    print("Running Texinfo files through makeinfo...")
    run_doc(["make", "-C", f"{BUILD_DIR}/texinfo", "info"])
    print(f"makeinfo finished; the Info files are in {FULL_BUILD_DIR}/texinfo.")


@app.command(rich_help_panel="Additional Doc Formats")
def gettext():
    """
    to make PO message catalogs
    """
    run_doc([SPHINX_BUILD, "-b", "gettext", *I18NSPHINXOPTS, f"{BUILD_DIR}/locale"])
    print()
    print(f"Build finished. The message catalogs are in {FULL_BUILD_DIR}/locale.")


@app.command(rich_help_panel="Additional Doc Formats")
def changes():
    """
    to make an overview of all changed/added/deprecated items
    """
    run_doc([SPHINX_BUILD, "-b", "changes", *ALLSPHINXOPTS, f"{BUILD_DIR}/changes"])
    print()
    print(f"The overview file is in {FULL_BUILD_DIR}/changes.")


@app.command(rich_help_panel="Code Quality")
def linkcheck():
    """
    to check all external links for integrity
    """
    run_doc([SPHINX_BUILD, "-b", "linkcheck", *ALLSPHINXOPTS, f"{BUILD_DIR}/linkcheck"])
    print()
    print(
        "Link check complete; look for any errors in the above output "
        + f"or in {FULL_BUILD_DIR}/linkcheck/output.txt."
    )


@app.command(rich_help_panel="Additional Doc Formats")
def doctest():
    """
    to run all doctests embedded in the documentation (if enabled)
    """
    run_doc([SPHINX_BUILD, "-b", "doctest", *ALLSPHINXOPTS, f"{BUILD_DIR}/doctest"])
    print(
        "Testing of doctests in the sources finished, look at the "
        + f"results in {FULL_BUILD_DIR}/doctest/output.txt."
    )


@app.command(rich_help_panel="Additional Doc Formats")
def coverage():
    """
    to run coverage check of the documentation (if enabled)
    """
    run_doc([SPHINX_BUILD, "-b", "coverage", *ALLSPHINXOPTS, f"{BUILD_DIR}/coverage"])
    print(
        "Testing of coverage in the sources finished, look at the "
        + f"results in {FULL_BUILD_DIR}/coverage/python.txt."
    )


@app.command(rich_help_panel="Additional Doc Formats")
def xml():
    run_doc([SPHINX_BUILD, "-b", "xml", *ALLSPHINXOPTS, f"{BUILD_DIR}/xml"])
    print()
    print(f"Build finished. The XML files are in {FULL_BUILD_DIR}/xml.")


@app.command(rich_help_panel="Additional Doc Formats")
def pseudoxml():
    run_doc([SPHINX_BUILD, "-b", "pseudoxml", *ALLSPHINXOPTS, f"{BUILD_DIR}/pseudoxml"])
    print()
    print(f"Build finished. The pseudo-XML files are in {FULL_BUILD_DIR}/pseudoxml.")


@app.command(rich_help_panel="Code Quality")
def lint():
    """
    Run all linting tasks: ruff, mypy, and pyright (Run this before making a pull request!)
    """
    ruff()
    mypy()
    pyright()
    print("Linting Complete.")


@app.command(rich_help_panel="Code Quality")
def ruff():
    run([RUFF, *RUFFOPTS, RUFFOPTS_PACKAGE])
    print("Ruff Finished.")


@app.command(rich_help_panel="Code Quality")
def mypy():
    "Typecheck using mypy"
    run([MYPY, *MYPYOPTS])
    print("MyPy Finished.")


@app.command(rich_help_panel="Code Quality")
def pyright():
    "Typecheck using pyright"
    run([PYRIGHT, *PYRIGHTOPTS])
    print("Pyright Finished.")


@app.command(rich_help_panel="Code Quality")
def format(check: bool = False):
    "Format code using black"
    black(check)
    isort(check)
    print("Formatting Complete.")


@app.command(rich_help_panel="Code Quality")
def isort(check: bool = False):
    "Format code using isort(actually ruff)"
    if not check:
        RUFFOPTS_ISORT.append("--fix")
    run([RUFF, *RUFFOPTS_ISORT, RUFFOPTS_PACKAGE])


@app.command(rich_help_panel="Code Quality")
def black(check: bool = False):
    "Format code using black"
    if check:
        BLACKOPTS.append("--check")
    run([BLACK, *BLACKOPTS])
    print("Black Finished.")


@app.command(rich_help_panel="Code Quality")
def test_full():
    run([PYTEST, TESTDIR])


@app.command(rich_help_panel="Code Quality")
def test():
    """Run unit tests (Run this before making a pull request!)"""
    run([PYTEST, UNITTESTS])


SHELLS_WITH_AUTOCOMPLETE = ("bash", "zsh", "fish", "powershell", "powersh")


@app.command(rich_help_panel="Shell Completion")
def whichshell():
    """to find out which shell your system seems to be running"""

    shell_name = Path(os.environ.get("SHELL")).stem
    print(f"Your default shell appears to be: {shell_name}")

    if shell_name in SHELLS_WITH_AUTOCOMPLETE:
        print("This shell is known to support tab-completion!")
        print("See CONTRIBUTING.md for more information on how to enable it.")


if __name__ == "__main__":
    app()
