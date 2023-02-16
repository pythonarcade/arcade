#!/usr/bin/env python
"""
Generate HTML docs
"""

import runpy
import sys
import os

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

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../arcade'))

# Don't change to
# from arcade.version import VERSION
# or read the docs build will fail.
from version import VERSION

RELEASE = VERSION

# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
    'sphinx_sitemap',
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
copyright = '2023, Paul Vincent Craven'
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
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'default'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'furo'

html_theme_options = {
    "light_logo": "../_images/arcade-logo.svg",
    "dark_logo": "../_images/arcade-logo.svg",
    "light_css_variables": {
       "font-stack--monospace": "Roboto Mono, Courier, monospace",
        "toc-font-size": "16px",
        "sidebar-item-font-size": "15px",
        "sidebar-item-line-height": "20px",
        "sidebar-caption-space-above": "0",
        "sidebar-caption-font-size": "18px",
        "sidebar-tree-space-above": "9px",
        "sidebar-item-spacing-vertical": "4px"
    },
    "dark_css_variables": {
       "font-stack--monospace": "Roboto Mono, Courier, monospace",
        "toc-font-size": "16px",
        "sidebar-item-font-size": "15px",
        "sidebar-item-line-height": "20px",
        "sidebar-caption-space-above": "0",
        "sidebar-caption-font-size": "18px",
        "sidebar-tree-space-above": "9px",
        "sidebar-item-spacing-vertical": "4px"
    },
}

html_title = f"Python Arcade {version}"

html_js_files = [
    'https://code.jquery.com/jquery-3.6.3.min.js',
    'https://cdn.datatables.net/1.13.2/js/jquery.dataTables.min.js',
]

html_css_files = [
    'https://cdn.datatables.net/1.13.2/css/jquery.dataTables.min.css',
]
# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = '_static/favicon-32x32.png'

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

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'python': ('https://docs.python.org/3', None),
                       'pyglet': ('https://pyglet.readthedocs.io/en/latest/', None),
                       'PIL': ('https://pillow.readthedocs.io/en/stable', None)}

# Fix: "more than one target found for cross-reference 'Texture'"
suppress_warnings = [
    "ref.python",
]


def warn_undocumented_members(_app, what, name, _obj, _options, lines):
    if len(lines) == 0:
        print(f"{what} {name} is undocumented")
        # lines.append(f".. Warning:: {what} ``{name}`` undocumented")


def source_read(_app, docname, source):

    # print(f"  XXX Reading {docname}")
    import os
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)

    filename = None
    if docname == "api_docs/arcade.color":
        filename = "../arcade/color/__init__.py"
    elif docname == "api_docs/arcade.csscolor":
        filename = "../arcade/csscolor/__init__.py"

    if filename:
        # print(f"  XXX Handling color file: {filename}")
        import re
        p = re.compile(r"^([A-Z_]+) = (\(.*\))")

        original_text = source[0]
        append_text = "\n\n.. raw:: html\n\n"
        append_text += "    <table class='colorTable'><tbody>\n"
        color_file = open(filename)

        for line in color_file:
            match = p.match(line)

            if match:
                color_variable_name = match.group(1)
                color_tuple = tuple(int(num) for num in match.group(2).strip('()').split(','))
                color_rgb_string = ', '.join(str(i) for i in color_tuple[:3])

                append_text += "    <tr>"
                append_text += f"<td>{color_variable_name}</td>"
                append_text += f"<td>{color_tuple}</td>"
                append_text += f"<td style='background-color:rgba({color_rgb_string}, {color_tuple[3] / 255});'><div></div></td>"
                append_text += "</tr>\n"

        append_text += "    </tbody></table>"
        source[0] = original_text + append_text


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

def add_ga_javascript(app, pagename, templatename, context, doctree):

    body = context.get('metatags', '')
    body += """
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-C7W6VSD1H5"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-C7W6VSD1H5');
</script>
    """
    context['metatags'] = body

def setup(app):
    app.add_css_file("css/custom.css")
    app.connect('source-read', source_read)
    app.connect('build-finished', post_process)
    app.connect("autodoc-process-docstring", warn_undocumented_members)
    # Should be added automatically by RTD.
    # app.connect('html-page-context', add_ga_javascript)
