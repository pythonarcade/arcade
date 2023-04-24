"""
Build script for documentation
"""
import os
from shutil import which, rmtree
import subprocess
from pathlib import Path
from typing import Union, List


# General sphinx state / options
SPHINXOPTS      = []
SPHINXBUILD     = "sphinx-build"
SPHINXAUTOBUILD = "sphinx-autobuild"
PAPER_SIZE      = None
DOCDIR          = "doc"
BUILDDIR        = "build"


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
    print("Build finished. The HTML pages are in $(BUILDDIR)/html.")


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
    print("Build finished. The HTML pages are in $(BUILDDIR)/dirhtml.")


@app.command()
def singlehtml():
    """
    to make a single large HTML file
    """
    run([SPHINXBUILD, "-b", "singlehtml", *ALLSPHINXOPTS, f"{BUILDDIR}/singlehtml"])
    print()
    print("Build finished. The HTML page is in $(BUILDDIR)/singlehtml.")


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
          ".hhp project file in $(BUILDDIR)/htmlhelp.")


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
    print("# assistant -collectionFile $(BUILDDIR)/qthelp/Arcade.qhc")


@app.command()
def applehelp():
    """
    to make an Apple Help Book
    """
    run([SPHINXBUILD, "-b", "applehelp", *ALLSPHINXOPTS, f"{BUILDDIR}/applehelp"])
    print()
    print("Build finished. The help book is in $(BUILDDIR)/applehelp.")
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
    print("# mkdir -p $$HOME/.local/share/devhelp/Arcade")
    print("# ln -s $(BUILDDIR)/devhelp $$HOME/.local/share/devhelp/Arcade")
    print("# devhelp")


@app.command()
def epub():
    """
    to make an epub
    """
    run([SPHINXBUILD, "-b", "epub", *ALLSPHINXOPTS, f"{BUILDDIR}/epub"])
    print()
    print("Build finished. The epub file is in $(BUILDDIR)/epub.")


@app.command()
def latex():
    """
    to make LaTeX files, you can set PAPER_SIZE=a4 or PAPER_SIZE=letter
    """
    run([SPHINXBUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILDDIR}/latex"])
    print()
    print("Build finished; the LaTeX files are in $(BUILDDIR)/latex.")
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
    print("pdflatex finished; the PDF files are in $(BUILDDIR)/latex.")


@app.command()
def latexpdfja():
    """
    to make LaTeX files and run them through platex/dvipdfmx
    """
    run([SPHINXBUILD, "-b", "latex", *ALLSPHINXOPTS, f"{BUILDDIR}/latex"])
    print("Running LaTeX files through platex and dvipdfmx...")
    run(['make', '-C', f'{BUILDDIR}/latex', 'all-pdf-ja'])
    print("pdflatex finished; the PDF files are in $(BUILDDIR)/latex.")


@app.command()
def text():
    """
    to make text files
    """
    run([SPHINXBUILD, "-b", "text", *ALLSPHINXOPTS, f"{BUILDDIR}/text"])
    print()
    print("Build finished. The text files are in $(BUILDDIR)/text.")


@app.command()
def man():
    """
    to make manual pages
    """
    run([SPHINXBUILD, "-b", "man", *ALLSPHINXOPTS, f"{BUILDDIR}/man"])
    print()
    print("Build finished. The manual pages are in $(BUILDDIR)/man.")


@app.command()
def texinfo():
    """
    to make Texinfo files
    """
    run([SPHINXBUILD, "-b", "texinfo", *ALLSPHINXOPTS, f"{BUILDDIR}/texinfo"])
    print()
    print("Build finished. The Texinfo files are in $(BUILDDIR)/texinfo.")
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
    print("makeinfo finished; the Info files are in $(BUILDDIR)/texinfo.")


@app.command()
def gettext():
    """
    to make PO message catalogs
    """
    run([SPHINXBUILD, "-b", "gettext", *I18NSPHINXOPTS, f"{BUILDDIR}/locale"])
    print()
    print("Build finished. The message catalogs are in $(BUILDDIR)/locale.")


@app.command()
def changes():
    """
    to make an overview of all changed/added/deprecated items
    """
    run([SPHINXBUILD, "-b", "changes", *ALLSPHINXOPTS, f"{BUILDDIR}/changes"])
    print()
    print("The overview file is in $(BUILDDIR)/changes.")


@app.command()
def linkcheck():
    """
    to check all external links for integrity
    """
    run([SPHINXBUILD, "-b", "linkcheck", *ALLSPHINXOPTS, f"{BUILDDIR}/linkcheck"])
    print()
    print("Link check complete; look for any errors in the above output " +
          "or in $(BUILDDIR)/linkcheck/output.txt.")


@app.command()
def doctest():
    """
    to run all doctests embedded in the documentation (if enabled)
    """
    run([SPHINXBUILD, "-b", "doctest", *ALLSPHINXOPTS, f"{BUILDDIR}/doctest"])
    print("Testing of doctests in the sources finished, look at the " +
          "results in $(BUILDDIR)/doctest/output.txt.")


@app.command()
def coverage():
    """
    to run coverage check of the documentation (if enabled)
    """
    run([SPHINXBUILD, "-b", "coverage", *ALLSPHINXOPTS, f"{BUILDDIR}/coverage"])
    print("Testing of coverage in the sources finished, look at the " +
          "results in $(BUILDDIR)/coverage/python.txt.")


@app.command()
def xml():
    run([SPHINXBUILD, "-b", "xml", *ALLSPHINXOPTS, f"{BUILDDIR}/xml"])
    print()
    print("Build finished. The XML files are in $(BUILDDIR)/xml.")


@app.command()
def pseudoxml():
    run([SPHINXBUILD, "-b", "pseudoxml", *ALLSPHINXOPTS, f"{BUILDDIR}/pseudoxml"])
    print()
    print("Build finished. The pseudo-XML files are in $(BUILDDIR)/pseudoxml.")


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
