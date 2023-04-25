"""
Build script for documentation
"""
import os
from shutil import which, rmtree
import subprocess
from pathlib import Path
from typing import Union, List


# General sphinx state / options
SPHINXOPTS        = []
SPHINXBUILD       = "sphinx-build"
SPHINXAUTOBUILD   = "sphinx-autobuild"
PAPER_SIZE        = None
DOCDIR            = "doc"
BUILDDIR          = "build"
# Intentionally brittle; the user should not be building as root
HOME             = Path.home().expanduser().resolve(strict=True)

# Used for user output; relative to project root
FULL_BUILD_PREFIX = f"{DOCDIR}/{BUILDDIR}"


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

os.chdir(Path(DOCDIR))

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


def run(args: Union[str, List[str]]) -> None:
    result = subprocess.run(args)
    if result.returncode != 0:
        exit(result.returncode)


@app.command()
def clean():
    """
    Delete built website files.
    """
    if os.path.exists(BUILDDIR):
        for item in Path(BUILDDIR).glob('*'):
            os.remove(item) if os.path.isfile(item) else rmtree(item)

@app.command()
def html():
    """
    to make standalone HTML files
    """
    run([SPHINXBUILD, "-b", "html", *ALLSPHINXOPTS, f"{BUILDDIR}/html"])
    print()
    print(f"Build finished. The HTML pages are in {FULL_BUILD_PREFIX}/html.")


@app.command()
def serve():
    """
    Build and serve standalone HTML files, with automatic rebuilds and live reload.
    """
    run([SPHINXAUTOBUILD, *SPHINXAUTOBUILDOPTS, '-b', 'html', *ALLSPHINXOPTS, f'{BUILDDIR}/html'])


@app.command()
def dirhtml():
    """
    to make HTML files named index.html in directories
    """
    run([SPHINXBUILD, "-b", "dirhtml", *ALLSPHINXOPTS, f"{BUILDDIR}/dirhtml"])
    print()
    print(f"Build finished. The HTML pages are in {FULL_BUILD_PREFIX}/dirhtml.")


@app.command()
def singlehtml():
    """
    to make a single large HTML file
    """
    run([SPHINXBUILD, "-b", "singlehtml", *ALLSPHINXOPTS, f"{BUILDDIR}/singlehtml"])
    print()
    print(f"Build finished. The HTML page is in {FULL_BUILD_PREFIX}/singlehtml.")


@app.command()
def pickle():
    """
    to make pickle files
    """
    run([SPHINXBUILD, "-b", "pickle", *ALLSPHINXOPTS, f"{BUILDDIR}/pickle"])
    print()
    print("Build finished; now you can process the pickle files.")


@app.command()
def json():
    """
    to make JSON files
    """
    run([SPHINXBUILD, "-b", "json", *ALLSPHINXOPTS, f"{BUILDDIR}/json"])
    print()
    print("Build finished; now you can process the JSON files.")


@app.command()
def htmlhelp():
    """
    to make HTML files and a HTML help project
    """
    run([SPHINXBUILD, "-b", "htmlhelp", *ALLSPHINXOPTS, f"{BUILDDIR}/htmlhelp"])
    print()
    print("Build finished; now you can run HTML Help Workshop with the" +
          f".hhp project file in {FULL_BUILD_PREFIX}/htmlhelp.")


@app.command()
def qthelp():
    """
    to make HTML files and a qthelp project
    """
    run([SPHINXBUILD, "-b", "qthelp", *ALLSPHINXOPTS, f"{BUILDDIR}/qthelp"])
    print()
    print('Build finished; now you can run "qcollectiongenerator" with the' +
          ".qhcp project file in $(BUILDDIR)/qthelp, like this:")
    print("# qcollectiongenerator $(BUILDDIR)/qthelp/Arcade.qhcp")
    print("To view the help file:")
    print(f"# assistant -collectionFile {FULL_BUILD_PREFIX}/qthelp/Arcade.qhc")


@app.command()
def applehelp():
    """
    to make an Apple Help Book
    """
    run([SPHINXBUILD, "-b", "applehelp", *ALLSPHINXOPTS, f"{BUILDDIR}/applehelp"])
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
    run([SPHINXBUILD, "-b", "devhelp", *ALLSPHINXOPTS, f"{BUILDDIR}/devhelp"])
    print()
    print("Build finished.")
    print("To view the help file:")
    print(f"# mkdir -p {HOME}/.local/share/devhelp/Arcade")
    print(f"# ln -s {FULL_BUILD_PREFIX}/devhelp {HOME}/.local/share/devhelp/Arcade")
    print("# devhelp")


@app.command()
def epub():
    """
    to make an epub
    """
    run([SPHINXBUILD, "-b", "epub", *ALLSPHINXOPTS, f"{BUILDDIR}/epub"])
    print()
    print(f"Build finished. The epub file is in {FULL_BUILD_PREFIX}/epub.")


@app.command()
def latex():
    """
    to make LaTeX files, you can set PAPER_SIZE=a4 or PAPER_SIZE=letter
    """
    run([SPHINXBUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILDDIR}/latex"])
    print()
    print(f"Build finished; the LaTeX files are in {FULL_BUILD_PREFIX}/latex.")
    print("Run \`make' in that directory to run these through (pdf)latex" +
          "(use \`make latexpdf' here to do that automatically).")


@app.command()
def latexpdf():
    """
    to make LaTeX files and run them through pdflatex
    """
    run([SPHINXBUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILDDIR}/latex"])
    print("Running LaTeX files through pdflatex...")
    run(['make', '-C', f'{BUILDDIR}/latex', 'all-pdf'])
    print(f"pdflatex finished; the PDF files are in {FULL_BUILD_PREFIX}/latex.")


@app.command()
def latexpdfja():
    """
    to make LaTeX files and run them through platex/dvipdfmx
    """
    run([SPHINXBUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILDDIR}/latex"])
    print("Running LaTeX files through platex and dvipdfmx...")
    run(['make', '-C', f'{BUILDDIR}/latex', 'all-pdf-ja'])
    print(f"pdflatex finished; the PDF files are in {FULL_BUILD_PREFIX}/latex.")


@app.command()
def text():
    """
    to make text files
    """
    run([SPHINXBUILD, "-b", "text", *ALLSPHINXOPTS, f"{BUILDDIR}/text"])
    print()
    print(f"Build finished. The text files are in {FULL_BUILD_PREFIX}/text.")


@app.command()
def man():
    """
    to make manual pages
    """
    run([SPHINXBUILD, "-b", "man", *ALLSPHINXOPTS, f"{BUILDDIR}/man"])
    print()
    print(f"Build finished. The manual pages are in {FULL_BUILD_PREFIX}/man.")


@app.command()
def texinfo():
    """
    to make Texinfo files
    """
    run([SPHINXBUILD, "-b", "texinfo", *ALLSPHINXOPTS, f"{BUILDDIR}/texinfo"])
    print()
    print(f"Build finished. The Texinfo files are in {FULL_BUILD_PREFIX}/texinfo.")
    print("Run \`make' in that directory to run these through makeinfo" +
          "(use \`make info' here to do that automatically).")


@app.command()
def info():
    """
    to make Texinfo files and run them through makeinfo
    """
    run([SPHINXBUILD, "-b", "texinfo", *ALLSPHINXOPTS, f"{BUILDDIR}/texinfo"])
    print("Running Texinfo files through makeinfo...")
    run(['make', '-C', f'{BUILDDIR}/texinfo', 'info'])
    print(f"makeinfo finished; the Info files are in {FULL_BUILD_PREFIX}/texinfo.")


@app.command()
def gettext():
    """
    to make PO message catalogs
    """
    run([SPHINXBUILD, "-b", "gettext", *I18NSPHINXOPTS, f"{BUILDDIR}/locale"])
    print()
    print(f"Build finished. The message catalogs are in {FULL_BUILD_PREFIX}/locale.")


@app.command()
def changes():
    """
    to make an overview of all changed/added/deprecated items
    """
    run([SPHINXBUILD, "-b", "changes", *ALLSPHINXOPTS, f"{BUILDDIR}/changes"])
    print()
    print(f"The overview file is in {FULL_BUILD_PREFIX}/changes.")


@app.command()
def linkcheck():
    """
    to check all external links for integrity
    """
    run([SPHINXBUILD, "-b", "linkcheck", *ALLSPHINXOPTS, f"{BUILDDIR}/linkcheck"])
    print()
    print("Link check complete; look for any errors in the above output " +
          f"or in {FULL_BUILD_PREFIX}/linkcheck/output.txt.")


@app.command()
def doctest():
    """
    to run all doctests embedded in the documentation (if enabled)
    """
    run([SPHINXBUILD, "-b", "doctest", *ALLSPHINXOPTS, f"{BUILDDIR}/doctest"])
    print("Testing of doctests in the sources finished, look at the " +
          f"results in {FULL_BUILD_PREFIX}/doctest/output.txt.")


@app.command()
def coverage():
    """
    to run coverage check of the documentation (if enabled)
    """
    run([SPHINXBUILD, "-b", "coverage", *ALLSPHINXOPTS, f"{BUILDDIR}/coverage"])
    print("Testing of coverage in the sources finished, look at the " +
          f"results in {FULL_BUILD_PREFIX}/coverage/python.txt.")


@app.command()
def xml():
    run([SPHINXBUILD, "-b", "xml", *ALLSPHINXOPTS, f"{BUILDDIR}/xml"])
    print()
    print(f"Build finished. The XML files are in {FULL_BUILD_PREFIX}/xml.")


@app.command()
def pseudoxml():
    run([SPHINXBUILD, "-b", "pseudoxml", *ALLSPHINXOPTS, f"{BUILDDIR}/pseudoxml"])
    print()
    print(f"Build finished. The pseudo-XML files are in {FULL_BUILD_PREFIX}/pseudoxml.")


@app.command()
def lint():
    os.chdir("../")
    run([RUFF, *RUFFOPTS])
    print("Ruff Finished.")
    run([MYPY, *MYPYOPTS])
    print("Mypy Finished.")
    print("Linting Complete.")


@app.command()
def ruff():
    os.chdir("../")
    run([RUFF, *RUFFOPTS])
    print("Ruff Finished.")


@app.command()
def mypy():
    os.chdir("../")
    run([MYPY, *MYPYOPTS])
    print("MyPy Finished.")


@app.command()
def test_full():
    os.chdir("../")
    run([PYTEST, TESTDIR])


@app.command()
def test():
    os.chdir("../")
    run([PYTEST, UNITTESTS])


if __name__ == "__main__":
    app()
