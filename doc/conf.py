#!/usr/bin/env python
"""Sphinx configuration file"""
from __future__ import annotations
from functools import cache
import logging
from pathlib import Path
from textwrap import dedent
from typing import Any, NamedTuple
import docutils.nodes
import os
import re
import runpy
import sphinx.ext.autodoc
import sphinx.transforms
import sys

# As of pyglet==2.1.dev7, this is no longer set in pyglet/__init__.py
# because Jupyter / IPython always load Sphinx into sys.modules. See
# the following for more info:
# 1. The ticket: https://github.com/pyglet/pyglet/issues/1215
# 2. The commit: https://github.com/pyglet/pyglet/commit/97076c3a33a7d368cc9c9e44ca67769b6a16a905
sys.is_pyglet_doc_run = True

# --- Pre-processing Tasks

log = logging.getLogger('conf.py')
logging.basicConfig(level=logging.INFO)

HERE = Path(__file__).resolve()
REPO_LOCAL_ROOT = HERE.parent.parent
ARCADE_MODULE = REPO_LOCAL_ROOT / "arcade"
UTIL_DIR = REPO_LOCAL_ROOT / "util"

log.info(f"Absolute path for our conf.py       : {str(HERE)!r}")
log.info(f"Absolute path for the repo root     : {str(REPO_LOCAL_ROOT)!r}")
log.info(f"Absolute path for the arcade module : {str(REPO_LOCAL_ROOT)!r}")
log.info(f"Absolute path for the util dir      : {str(UTIL_DIR)!r}")

# _temp_version = (REPO_LOCAL_ROOT / "arcade" / "VERSION").read_text().replace("-",'')

sys.path.insert(0, str(REPO_LOCAL_ROOT))
sys.path.insert(0, str(ARCADE_MODULE))
log.info(f"Inserted elements in system path: First two are now:")
for i in range(2):
    log.info(f"  {i}: {sys.path[i]!r}")

# Don't change to
# from arcade.version import VERSION
# or read the docs build will fail.
from version import VERSION # pyright: ignore [reportMissingImports]
log.info(f"Got version {VERSION!r}")

REPO_URL_BASE="https://github.com/pythonarcade/arcade"
if 'dev' in VERSION:
    GIT_REF = 'development'
    log.info(f"Got .dev release: using {GIT_REF!r}")
else:
    GIT_REF = VERSION
    log.info(f"Got real release: using {GIT_REF!r}")

# We'll pass this to our generation scripts to initialize their globals
FMT_URL_REF_BASE=f"{REPO_URL_BASE}/blob/{GIT_REF}"
RESOURCE_GLOBALS = dict(
    GIT_REF=GIT_REF,
    BASE_URL_REPO=REPO_URL_BASE,
    # This double-bracket escapes brackets in f-strings
    FMT_URL_REF_PAGE=f"{FMT_URL_REF_BASE}/{{}}",
    FMT_URL_REF_EMBED=f"{FMT_URL_REF_BASE}/{{}}?raw=true",
)

def run_util(filename, run_name="__main__", init_globals=None):

    full_absolute_path = UTIL_DIR / filename
    full_str = str(full_absolute_path)

    log.info(f"Running {full_str!r} with:")
    log.info(f"  run_name={run_name!r}")
    kwargs = dict(run_name=run_name)
    if init_globals is not None:
        kwargs['init_globals'] = init_globals
        log.info(f"  init_globals={{")
        num_left = len(init_globals)
        for k, v in init_globals.items():
            end = "," if num_left else ""
            log.info(f"    {k!r} : {v!r}{end}")
            num_left -= num_left
        log.info(f"  }}")

    runpy.run_path(full_str, **kwargs)

# Make thumbnails for the example code screenshots
run_util("generate_example_thumbnails.py")
# Create a tabular representation of the resources with embeds
run_util("create_resources_listing.py", init_globals=RESOURCE_GLOBALS)
# Run the generate quick API index script
run_util('../util/update_quick_index.py')


autodoc_inherit_docstrings = False
autodoc_default_options = {
    'members': True,
    # 'member-order': 'groupwise',
    'member-order': 'alphabetical',
    'undoc-members': True,
    'show-inheritance': True
}
toc_object_entries_show_parents = 'hide'
# Special methods in api docs gets a special prefix emoji
prettyspecialmethods_signature_prefix = '🧙'


RELEASE = VERSION
# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx_rtd_theme',  # Read the Docs theme
    'sphinx_rtd_dark_mode',  # Dark mode for the RTD theme
    'sphinx.ext.autodoc',  # API doc generation tools
    'sphinx.ext.napoleon',  # Support for NumPy and Google style docstrings
    'sphinx.ext.imgconverter',  # Converts .gif for PDF doc build
    'sphinx.ext.intersphinx',  # Link to other projects' docs
    'sphinx.ext.viewcode',  # display code with line numbers and line highlighting
    'sphinx_copybutton',  # Adds a copy button to code blocks
    'sphinx_sitemap',  # sitemap.xml generation
    'doc.extensions.prettyspecialmethods',  # Forker plugin for prettifying special methods
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Python Arcade Library'
copyright = '2024, Paul Vincent Craven'
author = 'Paul Vincent Craven'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = VERSION
# The full version, including alpha/beta/rc tags.
release = RELEASE

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    "links.rst",
    "substitutions.rst",
    "_archive/*",
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'default'  # will use "sphinx" or the theme's default

# If true, `todo` and `todoList` produce output, else they produce nothing.
# todo_include_todos = True

# napoleon_numpy_docstring = False
# napoleon_google_docstring = True

# Warn about all references where the target cannot be found.
# This is important to always enable to catch broken doc or api links
# nitpicky = True

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# See sphinx-rtd-theme docs for details on each option:
# https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html
html_theme_options = {
    'logo_only': False,
    'sticky_navigation': True,
    'navigation_depth': 3,
    'collapse_navigation': False,
}

# The single config option provided by sphinx-rtd-dark-mode
# https://github.com/MrDogeBro/sphinx_rtd_dark_mode#config
default_dark_mode = True

html_title = f'Python Arcade {version}'

html_js_files = [
    'https://code.jquery.com/jquery-3.6.3.min.js',
    'https://cdn.datatables.net/1.13.2/js/jquery.dataTables.min.js',
]

html_css_files = [
    'https://cdn.datatables.net/1.13.2/css/jquery.dataTables.min.css',
]
# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = '_static/android-chrome-192x192.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = '_static/favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
html_extra_path = ['html_extra']

# Output file base name for HTML help builder.
htmlhelp_basename = 'Arcade'
html_baseurl = 'https://api.arcade.academy/'

# Fix line numbers on code listings until the RTD theme updates to sphinx 4+
# html_codeblock_linenos_style = 'table'

# Configuration for intersphinx enabling linking other projects
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pyglet': ('https://pyglet.readthedocs.io/en/development/', None),
    'PIL': ('https://pillow.readthedocs.io/en/stable', None),
    'pymunk': ('https://www.pymunk.org/en/latest/', None),
}


# These will be joined as one block and prepended to every source file.
# Substitutions for |version| and |release| are predefined by Sphinx.
PROLOG_PARTS = [
    #".. include:: /links.rst",
    ".. |pyglet Player| replace:: pyglet :py:class:`~pyglet.media.player.Player`",
    ".. _Arcade's License File on GitHub: {FMT_URL_REF_BASE}/license.rst"
]
with open("links.rst") as f:
    PROLOG_PARTS.extend(f.readlines())

rst_prolog = "\n".join(PROLOG_PARTS)



def strip_init_return_typehint(app, what, name, obj, options, signature, return_annotation):
    # Prevent a the `-> None` annotation from appearing after classes.
    # This annotation comes from the `__init__`, but it renders on the class,
    # e.g. `Foo() -> None`
    # From the user's perspective, this is wrong: `Foo() -> Foo` not `None`
    if what == "class" and return_annotation is None:
        return (signature, None)

def inspect_docstring_for_member(
    _app,
    what: str,
    name: str,
    _obj: object,
    _options: dict[str, Any],
    lines: list[str],
):
    """
    Callback for the autodoc-process-docstring event.
    Where we can plug in various sanity checks such as warning about
    undocumented members.

    Args:
        _app: The Sphinx application object
        what (string): The type of object ("attribute", "class", "module", "function", "method")
        name: The fully qualified name of the object
        _obj: The object being documented
        _options: The autodoc options for this object
        lines: The lines of the docstring
    """
    # For debugging purposes
    # print(
    #     f"app={_app}\n"
    #     f"what={what}\n"
    #     f"name={name}\n"
    #     f"obj={_obj}\n"
    #     f"options={_options}\n"
    #     f"lines){lines}\n"
    # )
    if len(lines) == 0:
        print(f"{what} {name} is undocumented")

    # Docstring on __init__ in classes raise an error.
    # Class docstrings should cover the initializer.
    if what == "class":
        doc = _obj.__init__.__doc__
        if doc and isinstance(doc, str) and not doc.startswith("Initialize self"):
            raise ValueError((
                f"Class {name} has a docstring on __init__. "
                "The class docstring should cover docs for the initializer:\n {_obj.__init__.__doc__}"
            ))


def generate_color_table(filename, source):
    """
    This function Generates the Color tables in the docs for color and csscolor packages.
    """
    append_text = "\n\n.. raw:: html\n\n"
    append_text += "    <table class='colorTable'><tbody>\n"

    # Will match a line containing:
    #    name    '(?P<name>[a-z_A-Z]*)' followed by
    #    a Color '(?: *= *Color *\( *)' followed by
    #    red     '(?P<red>\d*)' followed by
    #    green   '(?P<green>\d*)' followed by
    #    blue    '(?P<blue>\d*)' followed by
    #    alpha   '(?P<alpha>\d*)'
    color_match = re.compile(r'(?P<name>[a-z_A-Z]*)(?:[ =]*Color[ (]*)(?P<red>\d*)[ ,]*(?P<green>\d*)[ ,]*(?P<blue>\d*)[ ,]*(?P<alpha>\d*)')

    with open(filename) as color_file:
        for line in color_file:
            # Check if the line has a Color.
            matches = color_match.match(line)
            if not matches:
                continue

            name, r, g, b, a = matches.groupdict().values()
            color_rgb_comma_sep= f"{r}, {g}, {b}"

            # Generate the alpha for CSS color function
            rgba_css = f"rgba({color_rgb_comma_sep}, {int(a) / 255!s:.4})"

            append_text += "    <tr>"
            append_text += (
                f"<td>"
                f"<code class=\"docutils literal notranslate\">"
                f"<span class=\"pre\">{name}</span>"
                f"</code>"
                f"</td>"
            )
            append_text += f"<td class=\"color-swatch\"><div style=\"background: {rgba_css};\">&nbsp</div></td>"
            append_text += f"<td>({color_rgb_comma_sep}, {a})</td>"
            append_text += "</tr>\n"

    append_text += "    </tbody></table>"
    source[0] += append_text


@cache
def get_module_root(doc_confdir):  # pending: revert #2304 or figure out a better solution
    """Temp fix since RTD doesn't use our make.py and offers no clean way to set build dir

    1. https://github.com/pythonarcade/arcade/pull/2304/ tried to change the build dir in make.py
    2. The readthedocs config does not use make.py
    3. They don't seem to offer any support for non-default build locations
    4. Instead, the options seem to be:
       * Weird environment variable API that's managed from their admin console (bus factor++)
       * Overwrite the entire build process https://blog.readthedocs.com/build-customization/
    """
    return doc_confdir.parent / "arcade"


def source_read_handler(_app, doc_name: str, source):
    """
    Event handler for source-read event.
    Where we can modify the source of a document before it is parsed.
    """
    def _get_dir(app, path):
        path = get_module_root(_app.confdir) / path
        print(f"Generated corrected module path: {path!r}")
        return path

    # Inject the color tables into the source
    if doc_name == "api_docs/arcade.color":
        generate_color_table(_get_dir(_app, "color/__init__.py"), source)
    elif doc_name == "api_docs/arcade.csscolor":
        generate_color_table(_get_dir(_app, "csscolor/__init__.py"), source)
    elif doc_name == "api_docs/arcade.uicolor":
        generate_color_table(_get_dir(_app, "uicolor.py"), source)

def on_autodoc_process_bases(app, name, obj, options, bases):
    """We don't care about the `object` base class, so remove it from the list of bases."""
    bases[:] = [base for base in bases if base is not object]



class A(NamedTuple):
    dirname: str
    comment: str = ""


APP_CONFIG_DIRS = (
    A('outdir'),
    A('srcdir', 'NOTE: This is reST source, not Python source!'),
    A('confdir'),
    A('doctreedir'),
)

def setup(app):
    print("Diagnostic info since readthedocs doesn't use our make.py:")
    for attr, comment in APP_CONFIG_DIRS:
        val = getattr(app, attr, None)
        print(f"  {attr}: {val!r}")
        if comment:
            print(f"    {comment}")

    # Separate stylesheets loosely by category.
    app.add_css_file("css/colors.css")
    app.add_css_file("css/layout.css")
    app.add_css_file("css/custom.css")

    app.add_js_file("js/custom.js")

    # IMPORTANT: We can't use app.add_autodocumenter!
    # See the docstring of ClassDocumenter above for why.
    # sphinx.ext.autodoc.ClassDocumenter = ClassDocumenter
    app.connect('source-read', source_read_handler)
    app.connect("autodoc-process-docstring", inspect_docstring_for_member)
    app.connect('autodoc-process-signature', strip_init_return_typehint, -1000)
    app.connect('autodoc-process-bases', on_autodoc_process_bases)
    # app.add_transform(Transform)


# ------------------------------------------------------
# Old hacks that breaks the api docs. !!! DO NOT USE !!!
# ------------------------------------------------------

# NOTE: Breaks annotated return types in properties and various other members
# class ClassDocumenter(sphinx.ext.autodoc.ClassDocumenter):
#     """A replacement for the default autodocumenter.

#     .. warning:: You must monkeypatch the baseclass with this!

#                  .. code-block:: python

#                     sphinx.ext.autodoc.ClassDocumenter = ClassDocumenter

#     Why? New ClassDocumenter subclasses appear to be registered for
#     specific names. For example, ``.. autointenum::`` would be declared
#     as follows::

#         class IntEnumDocumenter(ClassDocumenter):
#             objtype = 'intenum'
#             # Full class omitted, taken from the extension tutorial:
#             # https://www.sphinx-doc.org/en/master/development/tutorials/autodoc_ext.html#writing-the-extension

#     However, this documenter is for the default name, so passing it to
#     `app.app_autodocumenter` will produce a warning about a conflict.
#     Arcade's build config promotes warnings to errors, breaking build.
#     """
#     def add_directive_header(self, sig: str) -> None:
#         r = super().add_directive_header(sig)
#         # Strip empty `Bases: `, will be empty when only superclass is `object`
#         # cuz we remove it earlier
#         strings = self.directive.result
#         if strings[-1] == '   Bases: ':
#             strings.pop()
#         return r

# NOTE: Breaks some properties
# class Transform(sphinx.transforms.SphinxTransform):
#     default_priority = 800
#     def apply(self):
#         self.document.walk(Visitor(self.document))

# class Visitor(docutils.nodes.SparseNodeVisitor):
#     def visit_desc_annotation(self, node):
#         # Remove `property` prefix from properties so they look the same as
#         # attributes
#         if 'property' in node.astext():
#             node.parent.remove(node)
