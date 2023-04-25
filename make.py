"""
Build script for documentation
"""
import os
from contextlib import contextmanager
from shutil import which, rmtree
import subprocess
from pathlib import Path
from typing import Union, List, Generator, Optional

PathLike = Union[Path, str, bytes]


def _resolve(p: PathLike, strict: bool = False) -> Path:
    return Path(p).expanduser().resolve(strict=strict)


PROJECT_ROOT      = _resolve(Path(__file__).parent, strict=True)


# General sphinx state / options
SPHINXOPTS        = []
SPHINXBUILD       = "sphinx-build"
SPHINXAUTOBUILD   = "sphinx-autobuild"
PAPER_SIZE        = None
DOCDIR            = "doc"
BUILDDIR          = "build"


# Used for user output; relative to project root
FULL_DOC_DIR      = PROJECT_ROOT / DOCDIR
FULL_BUILD_PREFIX = f"{DOCDIR}/{BUILDDIR}"
FULL_BUILD_DIR    = PROJECT_ROOT / FULL_BUILD_PREFIX


# Linting
RUFF        = "ruff"
RUFFOPTS    = ["arcade"]
MYPY        = "mypy"
MYPYOPTS    = ["arcade"]


# Testing
PYTEST  = "pytest"
TESTDIR = "tests"
UNITTESTS = TESTDIR + "/unit"

# Internal variables.
PAPER_SIZE_OPTS = {}
PAPER_SIZE_OPTS[None] = []
PAPER_SIZE_OPTS['a4'] = ['-D', 'latex_paper_size=a4']
PAPER_SIZE_OPTS['letter'] = ['-D', 'latex_paper_size=letter']
ALLSPHINXOPTS       = ['-d', f'{BUILDDIR}/doctrees', *PAPER_SIZE_OPTS[PAPER_SIZE], *SPHINXOPTS, '.']
SPHINXAUTOBUILDOPTS = ['--watch', './arcade']

# Important: the i18n builder cannot share the environment and doctrees with the others
# This allows for internationalization / localization of doc.
I18NSPHINXOPTS      = [*PAPER_SIZE_OPTS[PAPER_SIZE], *SPHINXOPTS, '.']


# User-friendly check for dependencies and binaries
binaries = ['sphinx-build', 'sphinx-autobuild']
libraries = ['typer']
for binary in binaries:
    not_found = [binary for binary in binaries if which(binary) is None]
    if not_found:
        print("Command-line tools not found: " + ', '.join(not_found))
        print("Did you forget to install them with `pip`?  See CONTRIBUTING.md file for instructions.")
        exit(1)
for library in libraries:
    def find(library):
        try:
            __import__(library)
            return True
        except: pass
    not_found = [library for library in libraries if not find(library)]
    if not_found:
        print("Python dependencies not found: " + ', '.join(not_found))
        print("Did you forget to install them with `pip`?  See CONTRIBUTING.md file for instructions.")
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

    :param directory: The directory to cd into.
    :return:
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


def run(args: Union[str, List[str]], cd: Optional[PathLike] = None) -> None:
    """
    Try to run `args` with subprocess, switching into & out of `cd` if provided.

    Switching back out should occur regardless of any exceptions, unless the
    interpreter crashes.

    :param args: the command to run.
    :param cd: a directory to switch into beforehand, if any.
    :return:
    """
    if cd is not None:
        with cd_context(_resolve(cd, strict=True)):
            result = subprocess.run(args)
    else:
        result = subprocess.run(args)

    if result.returncode != 0:
        exit(result.returncode)


def run_doc(args: Union[str, List[str]]) -> None:
    run(args, cd=FULL_DOC_DIR)


@app.command()
def clean():
    """
    Delete built website files.
    """
    if os.path.exists(FULL_BUILD_DIR):
        for item in Path(FULL_BUILD_DIR).glob('*'):
            os.remove(item) if os.path.isfile(item) else rmtree(item)


@app.command()
def html():
    """
    to make standalone HTML files
    """
    run_doc([SPHINXBUILD, "-b", "html", *ALLSPHINXOPTS, f"{BUILDDIR}/html"])
    print()
    print(f"Build finished. The HTML pages are in {FULL_BUILD_PREFIX}/html.")


@app.command()
def serve():
    """
    Build and serve standalone HTML files, with automatic rebuilds and live reload.
    """
    run_doc([SPHINXAUTOBUILD, *SPHINXAUTOBUILDOPTS, '-b', 'html', *ALLSPHINXOPTS, f'{BUILDDIR}/html'])


@app.command()
def dirhtml():
    """
    to make HTML files named index.html in directories
    """
    run_doc([SPHINXBUILD, "-b", "dirhtml", *ALLSPHINXOPTS, f"{BUILDDIR}/dirhtml"])
    print()
    print(f"Build finished. The HTML pages are in {FULL_BUILD_PREFIX}/dirhtml.")


@app.command()
def singlehtml():
    """
    to make a single large HTML file
    """
    run_doc([SPHINXBUILD, "-b", "singlehtml", *ALLSPHINXOPTS, f"{BUILDDIR}/singlehtml"])
    print()
    print(f"Build finished. The HTML page is in {FULL_BUILD_PREFIX}/singlehtml.")


@app.command()
def pickle():
    """
    to make pickle files
    """
    run_doc([SPHINXBUILD, "-b", "pickle", *ALLSPHINXOPTS, f"{BUILDDIR}/pickle"])
    print()
    print("Build finished; now you can process the pickle files.")


@app.command()
def json():
    """
    to make JSON files
    """
    run_doc([SPHINXBUILD, "-b", "json", *ALLSPHINXOPTS, f"{BUILDDIR}/json"])
    print()
    print("Build finished; now you can process the JSON files.")


@app.command()
def htmlhelp():
    """
    to make HTML files and a HTML help project
    """
    run_doc([SPHINXBUILD, "-b", "htmlhelp", *ALLSPHINXOPTS, f"{BUILDDIR}/htmlhelp"])
    print()
    print("Build finished; now you can run HTML Help Workshop with the" +
          f".hhp project file in {FULL_BUILD_PREFIX}/htmlhelp.")


@app.command()
def qthelp():
    """
    to make HTML files and a qthelp project
    """
    run_doc([SPHINXBUILD, "-b", "qthelp", *ALLSPHINXOPTS, f"{BUILDDIR}/qthelp"])
    print()
    print('Build finished; now you can run "qcollectiongenerator" with the' +
          f".qhcp project file in {FULL_BUILD_PREFIX}/qthelp, like this:")
    print(f"# qcollectiongenerator {FULL_BUILD_PREFIX}/qthelp/Arcade.qhcp")
    print("To view the help file:")
    print(f"# assistant -collectionFile {FULL_BUILD_PREFIX}/qthelp/Arcade.qhc")


@app.command()
def applehelp():
    """
    to make an Apple Help Book
    """
    run_doc([SPHINXBUILD, "-b", "applehelp", *ALLSPHINXOPTS, f"{BUILDDIR}/applehelp"])
    print()
    print(f"Build finished. The help book is in {FULL_BUILD_PREFIX}/applehelp.")
    print("N.B. You won't be able to view it unless you put it in" +
          "~/Library/Documentation/Help or install it in your application" +
          "bundle.")


@app.command()
def devhelp():
    """
    to make HTML files and a Devhelp project
    """
    home = Path.home().expanduser().resolve(strict=True)
    run_doc([SPHINXBUILD, "-b", "devhelp", *ALLSPHINXOPTS, f"{BUILDDIR}/devhelp"])
    print()
    print("Build finished.")
    print("To view the help file:")
    print(f"# mkdir -p {home}/.local/share/devhelp/Arcade")
    print(f"# ln -s {FULL_BUILD_PREFIX}/devhelp {home}/.local/share/devhelp/Arcade")
    print("# devhelp")


@app.command()
def epub():
    """
    to make an epub
    """
    run_doc([SPHINXBUILD, "-b", "epub", *ALLSPHINXOPTS, f"{BUILDDIR}/epub"])
    print()
    print(f"Build finished. The epub file is in {FULL_BUILD_PREFIX}/epub.")


@app.command()
def latex():
    """
    to make LaTeX files, you can set PAPER_SIZE=a4 or PAPER_SIZE=letter
    """
    run_doc([SPHINXBUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILDDIR}/latex"])
    print()
    print(f"Build finished; the LaTeX files are in {FULL_BUILD_PREFIX}/latex.")
    print("Run \`make' in that directory to run these through (pdf)latex" +
          "(use \`make latexpdf' here to do that automatically).")


@app.command()
def latexpdf():
    """
    to make LaTeX files and run them through pdflatex
    """
    run_doc([SPHINXBUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILDDIR}/latex"])
    print("Running LaTeX files through pdflatex...")
    run_doc(['make', '-C', f'{BUILDDIR}/latex', 'all-pdf'])
    print(f"pdflatex finished; the PDF files are in {FULL_BUILD_PREFIX}/latex.")


@app.command()
def latexpdfja():
    """
    to make LaTeX files and run them through platex/dvipdfmx
    """
    run_doc([SPHINXBUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILDDIR}/latex"])
    print("Running LaTeX files through platex and dvipdfmx...")
    run_doc(['make', '-C', f'{BUILDDIR}/latex', 'all-pdf-ja'])
    print(f"pdflatex finished; the PDF files are in {FULL_BUILD_PREFIX}/latex.")


@app.command()
def text():
    """
    to make text files
    """
    run_doc([SPHINXBUILD, "-b", "text", *ALLSPHINXOPTS, f"{BUILDDIR}/text"])
    print()
    print(f"Build finished. The text files are in {FULL_BUILD_PREFIX}/text.")


@app.command()
def man():
    """
    to make manual pages
    """
    run_doc([SPHINXBUILD, "-b", "man", *ALLSPHINXOPTS, f"{BUILDDIR}/man"])
    print()
    print(f"Build finished. The manual pages are in {FULL_BUILD_PREFIX}/man.")


@app.command()
def texinfo():
    """
    to make Texinfo files
    """
    run_doc([SPHINXBUILD, "-b", "texinfo", *ALLSPHINXOPTS, f"{BUILDDIR}/texinfo"])
    print()
    print(f"Build finished. The Texinfo files are in {FULL_BUILD_PREFIX}/texinfo.")
    print("Run \`make' in that directory to run these through makeinfo" +
          "(use \`make info' here to do that automatically).")


@app.command()
def info():
    """
    to make Texinfo files and run them through makeinfo
    """
    run_doc([SPHINXBUILD, "-b", "texinfo", *ALLSPHINXOPTS, f"{BUILDDIR}/texinfo"])
    print("Running Texinfo files through makeinfo...")
    run_doc(['make', '-C', f'{BUILDDIR}/texinfo', 'info'])
    print(f"makeinfo finished; the Info files are in {FULL_BUILD_PREFIX}/texinfo.")


@app.command()
def gettext():
    """
    to make PO message catalogs
    """
    run_doc([SPHINXBUILD, "-b", "gettext", *I18NSPHINXOPTS, f"{BUILDDIR}/locale"])
    print()
    print(f"Build finished. The message catalogs are in {FULL_BUILD_PREFIX}/locale.")


@app.command()
def changes():
    """
    to make an overview of all changed/added/deprecated items
    """
    run_doc([SPHINXBUILD, "-b", "changes", *ALLSPHINXOPTS, f"{BUILDDIR}/changes"])
    print()
    print(f"The overview file is in {FULL_BUILD_PREFIX}/changes.")


@app.command()
def linkcheck():
    """
    to check all external links for integrity
    """
    run_doc([SPHINXBUILD, "-b", "linkcheck", *ALLSPHINXOPTS, f"{BUILDDIR}/linkcheck"])
    print()
    print("Link check complete; look for any errors in the above output " +
          f"or in {FULL_BUILD_PREFIX}/linkcheck/output.txt.")


@app.command()
def doctest():
    """
    to run all doctests embedded in the documentation (if enabled)
    """
    run_doc([SPHINXBUILD, "-b", "doctest", *ALLSPHINXOPTS, f"{BUILDDIR}/doctest"])
    print("Testing of doctests in the sources finished, look at the " +
          f"results in {FULL_BUILD_PREFIX}/doctest/output.txt.")


@app.command()
def coverage():
    """
    to run coverage check of the documentation (if enabled)
    """
    run_doc([SPHINXBUILD, "-b", "coverage", *ALLSPHINXOPTS, f"{BUILDDIR}/coverage"])
    print("Testing of coverage in the sources finished, look at the " +
          f"results in {FULL_BUILD_PREFIX}/coverage/python.txt.")


@app.command()
def xml():
    run_doc([SPHINXBUILD, "-b", "xml", *ALLSPHINXOPTS, f"{BUILDDIR}/xml"])
    print()
    print(f"Build finished. The XML files are in {FULL_BUILD_PREFIX}/xml.")


@app.command()
def pseudoxml():
    run_doc([SPHINXBUILD, "-b", "pseudoxml", *ALLSPHINXOPTS, f"{BUILDDIR}/pseudoxml"])
    print()
    print(f"Build finished. The pseudo-XML files are in {FULL_BUILD_PREFIX}/pseudoxml.")


@app.command()
def lint():
    run([RUFF, *RUFFOPTS])
    print("Ruff Finished.")
    run([MYPY, *MYPYOPTS])
    print("Mypy Finished.")
    print("Linting Complete.")


@app.command()
def ruff():
    run([RUFF, *RUFFOPTS])
    print("Ruff Finished.")


@app.command()
def mypy():
    run([MYPY, *MYPYOPTS])
    print("MyPy Finished.")


@app.command()
def test_full():
    run([PYTEST, TESTDIR])


@app.command()
def test():
    run([PYTEST, UNITTESTS])


if __name__ == "__main__":
    app()
