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
        print("Did you forget to install them with `pip`?")
        print("See CONTRIBUTING.md file for instructions.")
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
        print("Did you forget to install them with `pip`?")
        print("See CONTRIBUTING.md file for instructions.")
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
    cmd = " ".join(args)
    print(">> Running command:", cmd)
    if cd is not None:
        with cd_context(_resolve(cd, strict=True)):
            result = subprocess.run(args)
    else:
        result = subprocess.run(args)

    print(">> Command finished:", cmd, "\n")

    # TODO: Should we exit here? Or continue to let other commands run also?
    if result.returncode != 0:
        exit(result.returncode)


def run_doc(args: str | list[str]) -> None:
    run(args, cd=PROJECT_ROOT)


@app.command(rich_help_panel="Docs")
def clean():
    """
    Clean / Delete the documentation build directory
    """
    if os.path.exists(FULL_BUILD_DIR):
        for item in Path(FULL_BUILD_DIR).glob("*"):
            os.remove(item) if os.path.isfile(item) else rmtree(item)


@app.command(rich_help_panel="Docs")
def html():
    """
    Build the documentation (HTML)
    """
    run_doc([SPHINX_BUILD, "-b", "html", *ALLSPHINXOPTS, f"{BUILD_DIR}/html"])
    print()
    print(f"Build finished. The HTML pages are in {FULL_BUILD_DIR}/html.")


@app.command(rich_help_panel="Docs")
def serve():
    """
    Build and serve the docs with automatic rebuilds and live reload.
    """
    run_doc(
        [SPHINX_AUTOBUILD, *SPHINXAUTOBUILDOPTS, "-b", "html", *ALLSPHINXOPTS, f"{BUILD_DIR}/html"]
    )


@app.command(rich_help_panel="Docs")
def linkcheck():
    """
    Check for broken links in the documentation
    """
    run_doc([SPHINX_BUILD, "-b", "linkcheck", *ALLSPHINXOPTS, f"{BUILD_DIR}/linkcheck"])
    print()
    print(
        "Link check complete; look for any errors in the above output "
        + f"or in {FULL_BUILD_DIR}/linkcheck/output.txt."
    )


# @app.command(rich_help_panel="Docs Extra Formats")
# def dirhtml():
#     """
#     to make HTML files named index.html in directories
#     """
#     run_doc([SPHINX_BUILD, "-b", "dirhtml", *ALLSPHINXOPTS, f"{BUILD_DIR}/dirhtml"])
#     print()
#     print(f"Build finished. The HTML pages are in {FULL_BUILD_DIR}/dirhtml.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def singlehtml():
#     """
#     to make a single large HTML file
#     """
#     run_doc([SPHINX_BUILD, "-b", "singlehtml", *ALLSPHINXOPTS, f"{BUILD_DIR}/singlehtml"])
#     print()
#     print(f"Build finished. The HTML page is in {FULL_BUILD_DIR}/singlehtml.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def pickle():
#     """
#     to make pickle files
#     """
#     run_doc([SPHINX_BUILD, "-b", "pickle", *ALLSPHINXOPTS, f"{BUILD_DIR}/pickle"])
#     print()
#     print("Build finished; now you can process the pickle files.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def json():
#     """
#     to make JSON files
#     """
#     run_doc([SPHINX_BUILD, "-b", "json", *ALLSPHINXOPTS, f"{BUILD_DIR}/json"])
#     print()
#     print("Build finished; now you can process the JSON files.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def htmlhelp():
#     """
#     to make HTML files and a HTML help project
#     """
#     run_doc([SPHINX_BUILD, "-b", "htmlhelp", *ALLSPHINXOPTS, f"{BUILD_DIR}/htmlhelp"])
#     print()
#     print(
#         "Build finished; now you can run HTML Help Workshop with the"
#         + f".hhp project file in {FULL_BUILD_DIR}/htmlhelp."
#     )


# @app.command(rich_help_panel="Docs Extra Formats")
# def devhelp():
#     """
#     to make HTML files and a Devhelp project
#     """
#     home = Path.home().expanduser().resolve(strict=True)
#     run_doc([SPHINX_BUILD, "-b", "devhelp", *ALLSPHINXOPTS, f"{BUILD_DIR}/devhelp"])
#     print()
#     print("Build finished.")
#     print("To view the help file:")
#     print(f"# mkdir -p {home}/.local/share/devhelp/Arcade")
#     print(f"# ln -s {FULL_BUILD_DIR}/devhelp {home}/.local/share/devhelp/Arcade")
#     print("# devhelp")


# @app.command(rich_help_panel="Docs Extra Formats")
# def epub():
#     """
#     to make an epub
#     """
#     run_doc([SPHINX_BUILD, "-b", "epub", *ALLSPHINXOPTS, f"{BUILD_DIR}/epub"])
#     print()
#     print(f"Build finished. The epub file is in {FULL_BUILD_DIR}/epub.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def latex():
#     """
#     to make LaTeX files, you can set PAPER_SIZE=a4 or PAPER_SIZE=letter
#     """
#     run_doc([SPHINX_BUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILD_DIR}/latex"])
#     print()
#     print(f"Build finished; the LaTeX files are in {FULL_BUILD_DIR}/latex.")
#     print(
#         "Run `make' in that directory to run these through (pdf)latex"
#         + "(use `make latexpdf' here to do that automatically)."
#     )


# @app.command(rich_help_panel="Docs Extra Formats")
# def latexpdf():
#     """
#     to make LaTeX files and run them through pdflatex
#     """
#     run_doc([SPHINX_BUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILD_DIR}/latex"])
#     print("Running LaTeX files through pdflatex...")
#     run_doc(["make", "-C", f"{BUILD_DIR}/latex", "all-pdf"])
#     print(f"pdflatex finished; the PDF files are in {FULL_BUILD_DIR}/latex.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def latexpdfja():
#     """
#     to make LaTeX files and run them through platex/dvipdfmx
#     """
#     run_doc([SPHINX_BUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILD_DIR}/latex"])
#     print("Running LaTeX files through platex and dvipdfmx...")
#     run_doc(["make", "-C", f"{BUILD_DIR}/latex", "all-pdf-ja"])
#     print(f"pdflatex finished; the PDF files are in {FULL_BUILD_DIR}/latex.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def text():
#     """
#     to make text files
#     """
#     run_doc([SPHINX_BUILD, "-b", "text", *ALLSPHINXOPTS, f"{BUILD_DIR}/text"])
#     print()
#     print(f"Build finished. The text files are in {FULL_BUILD_DIR}/text.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def man():
#     """
#     to make manual pages
#     """
#     run_doc([SPHINX_BUILD, "-b", "man", *ALLSPHINXOPTS, f"{BUILD_DIR}/man"])
#     print()
#     print(f"Build finished. The manual pages are in {FULL_BUILD_DIR}/man.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def texinfo():
#     """
#     to make Texinfo files
#     """
#     run_doc([SPHINX_BUILD, "-b", "texinfo", *ALLSPHINXOPTS, f"{BUILD_DIR}/texinfo"])
#     print()
#     print(f"Build finished. The Texinfo files are in {FULL_BUILD_DIR}/texinfo.")
#     print(
#         "Run `make' in that directory to run these through makeinfo"
#         + "(use `make info' here to do that automatically)."
#     )


# @app.command(rich_help_panel="Docs Extra Formats")
# def info():
#     """
#     to make Texinfo files and run them through makeinfo
#     """
#     run_doc([SPHINX_BUILD, "-b", "texinfo", *ALLSPHINXOPTS, f"{BUILD_DIR}/texinfo"])
#     print("Running Texinfo files through makeinfo...")
#     run_doc(["make", "-C", f"{BUILD_DIR}/texinfo", "info"])
#     print(f"makeinfo finished; the Info files are in {FULL_BUILD_DIR}/texinfo.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def gettext():
#     """
#     to make PO message catalogs
#     """
#     run_doc([SPHINX_BUILD, "-b", "gettext", *I18NSPHINXOPTS, f"{BUILD_DIR}/locale"])
#     print()
#     print(f"Build finished. The message catalogs are in {FULL_BUILD_DIR}/locale.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def changes():
#     """
#     to make an overview of all changed/added/deprecated items
#     """
#     run_doc([SPHINX_BUILD, "-b", "changes", *ALLSPHINXOPTS, f"{BUILD_DIR}/changes"])
#     print()
#     print(f"The overview file is in {FULL_BUILD_DIR}/changes.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def doctest():
#     """
#     to run all doctests embedded in the documentation (if enabled)
#     """
#     run_doc([SPHINX_BUILD, "-b", "doctest", *ALLSPHINXOPTS, f"{BUILD_DIR}/doctest"])
#     print(
#         "Testing of doctests in the sources finished, look at the "
#         + f"results in {FULL_BUILD_DIR}/doctest/output.txt."
#     )


# @app.command(rich_help_panel="Docs Extra Formats")
# def coverage():
#     """
#     to run coverage check of the documentation (if enabled)
#     """
#     run_doc([SPHINX_BUILD, "-b", "coverage", *ALLSPHINXOPTS, f"{BUILD_DIR}/coverage"])
#     print(
#         "Testing of coverage in the sources finished, look at the "
#         + f"results in {FULL_BUILD_DIR}/coverage/python.txt."
#     )


# @app.command(rich_help_panel="Docs Extra Formats")
# def xml():
#     run_doc([SPHINX_BUILD, "-b", "xml", *ALLSPHINXOPTS, f"{BUILD_DIR}/xml"])
#     print()
#     print(f"Build finished. The XML files are in {FULL_BUILD_DIR}/xml.")


# @app.command(rich_help_panel="Docs Extra Formats")
# def pseudoxml():
#     run_doc([SPHINX_BUILD, "-b", "pseudoxml", *ALLSPHINXOPTS, f"{BUILD_DIR}/pseudoxml"])
#     print()
#     print(f"Build finished. The pseudo-XML files are in {FULL_BUILD_DIR}/pseudoxml.")


@app.command(rich_help_panel="Code Quality")
def lint():
    """
    Run tasks: ruff, mypy, and pyright (Run before making a pull request)
    """
    ruff_check()
    mypy()
    pyright()


@app.command(rich_help_panel="Code Quality - Advanced")
def ruff_check():
    """Run ruff check for code quality"""
    run([RUFF, *RUFFOPTS, RUFFOPTS_PACKAGE])


@app.command(rich_help_panel="Code Quality")
def format(check: bool = False):
    """Format code (Run before making a pull request)"""
    ruff_format(check)
    ruff_isort(check)


@app.command(rich_help_panel="Code Quality - Advanced")
def ruff_format(check: bool = False):
    """Format code using ruff"""
    ruff_fmt = [RUFF, "format"]
    if check:
        ruff_fmt.append("--check")
    run(ruff_fmt)


@app.command(rich_help_panel="Code Quality - Advanced")
def ruff_isort(check: bool = False):
    """Sort imports with ruff"""
    if not check:
        RUFFOPTS_ISORT.append("--fix")
    run([RUFF, *RUFFOPTS_ISORT, RUFFOPTS_PACKAGE])


@app.command(rich_help_panel="Code Quality - Advanced")
def mypy():
    """Typecheck using mypy"""
    run([MYPY, *MYPYOPTS])


@app.command(rich_help_panel="Code Quality - Advanced")
def pyright():
    """Typecheck using pyright"""
    run([PYRIGHT, *PYRIGHTOPTS])


@app.command(rich_help_panel="Tests")
def test():
    """Run unit tests"""
    run([PYTEST, UNITTESTS])


@app.command(rich_help_panel="Tests")
def test_full():
    """Run unit and integration tests"""
    run([PYTEST, TESTDIR])


# @app.command(rich_help_panel="Shell Completion")
# def whichshell():
#     """Find out which shell your system seems to be running"""
#     shell_name = Path(os.environ.get("SHELL")).stem
#     print(f"Your default shell appears to be: {shell_name}")

#     shells = ("bash", "zsh", "fish", "powershell", "powersh")
#     if shell_name in shells:
#         print("This shell is known to support tab-completion!")
#         print("See CONTRIBUTING.md for more information on how to enable it.")


if __name__ == "__main__":
    app()
