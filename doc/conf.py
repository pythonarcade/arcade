#!/usr/bin/env python
"""
Generate HTML docs
"""

import docutils.nodes
import os
import re
import runpy
import sphinx.ext.autodoc
import sphinx.transforms
import sys


# --- Pre-processing Tasks

# Then generate thumbnails if they do not exist

# Make thumbnails for the example code screenshots
runpy.run_path('../util/generate_example_thumbnails.py', run_name='__main__')
# Create a listing of the resources
runpy.run_path('../util/create_resources_listing.py', run_name='__main__')
# Run the generate quick API index script
runpy.run_path('../util/update_quick_index.py', run_name='__main__')

# Enable this is you want __init__ to show up in docs.
# Ideally, these docs should be in the class docs, not __init__ so try to
# leave this disabled.
# autodoc_default_options = {
#     'special-members': '__init__',
# }

autodoc_inherit_docstrings = False
autodoc_default_options = {
    'members': True,
    'member-order': 'groupwise',
    'undoc-members': True,
    'show-inheritance': True
}
toc_object_entries_show_parents = 'hide'
prettyspecialmethods_signature_prefix = '🧙'

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../arcade'))

# Don't change to
# from arcade.version import VERSION
# or read the docs build will fail.
from version import VERSION # pyright: ignore [reportMissingImports]

RELEASE = VERSION

# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx_rtd_theme',
    'sphinx_rtd_dark_mode',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.imgconverter',  # Converts .gif for PDF doc build
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
    'sphinx_sitemap',
    # "sphinx_autodoc_typehints",
    'doc.extensions.prettyspecialmethods'
]

# --- Spell check. Never worked well.
# try:
#     import sphinxcontrib.spelling
# except ImportError:
#     pass
# else:
#     extensions.append("sphinxcontrib.spelling")
#
# spelling_word_list_filename = "wordlist.txt"

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
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
pygments_style = 'default'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

napoleon_numpy_docstring = False
napoleon_google_docstring = True

nitpicky = True  # Warn about all references where the target cannot be found.

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# See sphinx-rtd-theme docs for details on each option:
# https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html
html_theme_options = {
    'display_version': True,
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
    'pyglet': ('https://pyglet.readthedocs.io/en/latest/', None),
    'PIL': ('https://pillow.readthedocs.io/en/stable', None),
    'pymunk': ('https://www.pymunk.org/en/latest/', None),
}

def strip_init_return_typehint(app, what, name, obj, options, signature, return_annotation):
    # Prevent a the `-> None` annotation from appearing after classes.
    # This annotation comes from the `__init__`, but it renders on the class,
    # e.g. `Foo() -> None`
    # From the user's perspective, this is wrong: `Foo() -> Foo` not `None`
    if what == "class" and return_annotation is None:
        return (signature, None)

def warn_undocumented_members(_app, what, name, _obj, _options, lines):
    if len(lines) == 0:
        print(f"{what} {name} is undocumented")
        # lines.append(f".. Warning:: {what} ``{name}`` undocumented")

    # Check for docstring on __init__ in classes and raise an error.
    # The class docstring should cover docs for the initializer only!
    if what == "class":
        doc = _obj.__init__.__doc__
        if doc and isinstance(doc, str) and not doc.startswith("Initialize self"):
            raise ValueError((
                f"Class {name} has a docstring on __init__. "
                "The class docstring should cover docs for the initializer:\n {_obj.__init__.__doc__}"
            ))


def generate_color_table(filename, source):
    """This function Generates the Color tables in the docs for color and csscolor packages"""

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

            color_rgba = f"({matches.group('red')}, {matches.group('green')}, {matches.group('blue')}, {matches.group('alpha')})"

            # Generate the alpha for CSS color function
            alpha = int( matches.group('alpha') ) / 255
            css_rgba = f"({matches.group('red')}, {matches.group('green')}, {matches.group('blue')}, {alpha!s:.4})"


            append_text += "    <tr>"
            append_text += f"<td>{matches.group('name')}</td>"
            append_text += f"<td>{color_rgba}</td>"
            append_text += f"<td class='checkered'><div style='background-color:rgba{css_rgba};'>&nbsp</div></td>"
            append_text += "</tr>\n"

    append_text += "    </tbody></table>"
    source[0] += append_text


def source_read(_app, docname, source):
    """Event handler for source-read event"""

    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)

    # Transform source for arcade.color and arcade.csscolor
    if docname == "api_docs/arcade.color":
        generate_color_table("../arcade/color/__init__.py", source)
    elif docname == "api_docs/arcade.csscolor":
        generate_color_table("../arcade/csscolor/__init__.py", source)


def post_process(_app, _exception):
    pass

#     try:
#         dir_path = os.path.dirname(os.path.realpath(__file__))
#         print(f"Performing dirsync")
#         print(f"Current dir: {dir_path}")
#         print(os.listdir("."))
#         from dirsync import sync
#         source_path = '../arcade/resources'
#         print(f"Items in resource path:")
#         print(os.listdir(source_path))
#
#         target_path = 'build/html/resources'
#
#         sync(source_path, target_path, 'sync', create=True)  # for syncing one way
#
#     except:
#         print("ERROR: Exception in post-process.")
#         import traceback
#         traceback.print_exc()
#         raise


def on_autodoc_process_bases(app, name, obj, options, bases):
    # Strip `object` from bases, it's just noise
    bases[:] = [base for base in bases if base is not object]


class ClassDocumenter(sphinx.ext.autodoc.ClassDocumenter):
    """A replacement for the default autodocumenter.

    .. warning:: You must monkeypatch the baseclass with this!

                 .. code-block:: python

                    sphinx.ext.autodoc.ClassDocumenter = ClassDocumenter

    Why? New ClassDocumenter subclasses appear to be registered for
    specific names. For example, ``.. autointenum::`` would be declared
    as follows::

        class IntEnumDocumenter(ClassDocumenter):
            objtype = 'intenum'
            # Full class omitted, taken from the extension tutorial:
            # https://www.sphinx-doc.org/en/master/development/tutorials/autodoc_ext.html#writing-the-extension

    However, this documenter is for the default name, so passing it to
    `app.app_autodocumenter` will produce a warning about a conflict.
    Arcade's build config promotes warnings to errors, breaking build.
    """
    def add_directive_header(self, sig: str) -> None:
        r = super().add_directive_header(sig)
        # Strip empty `Bases: `, will be empty when only superclass is `object`
        # cuz we remove it earlier
        strings = self.directive.result
        if strings[-1] == '   Bases: ':
            strings.pop()
        return r


class Transform(sphinx.transforms.SphinxTransform):
    default_priority = 800
    def apply(self):
        self.document.walk(Visitor(self.document))

class Visitor(docutils.nodes.SparseNodeVisitor):
    def visit_desc_annotation(self, node):
        # Remove `property` prefix from properties so they look the same as
        # attributes
        if 'property' in node.astext():
            node.parent.remove(node)


def setup(app):
    app.add_css_file("css/custom.css")
    app.add_js_file("js/custom.js")

    # IMPORTANT: We can't use app.add_autodocumenter!
    # See the docstring of ClassDocumenter above for why.
    sphinx.ext.autodoc.ClassDocumenter = ClassDocumenter
    app.connect('source-read', source_read)
    app.connect('build-finished', post_process)
    app.connect("autodoc-process-docstring", warn_undocumented_members)
    app.connect('autodoc-process-signature', strip_init_return_typehint, -1000)
    app.connect('autodoc-process-bases', on_autodoc_process_bases)
    app.add_transform(Transform)
