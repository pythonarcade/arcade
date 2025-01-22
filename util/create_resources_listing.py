"""
Quick Index Generator

Generate quick API indexes in Restructured Text Format for Sphinx documentation.
"""
# fmt: off
# ruff: noqa
from __future__ import annotations

import html
import re
import sys
import textwrap
from collections import defaultdict
from collections.abc import Mapping
from functools import lru_cache, cache
from io import StringIO
from itertools import chain, cycle
from pathlib import Path
from typing import List, Callable, Protocol, Sequence, Iterable, TypeVar
import logging

import PIL.Image
from typing_extensions import TypedDict, NotRequired

log = logging.getLogger(__name__)

# Ensure we get utility and Arcade imports first
sys.path.insert(0, str(Path(__file__).parent.resolve()))
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import arcade
from doc_helpers.vfs import Vfs


def announce_templating(var_name):
    _v = globals()[var_name]
    log.warning(f"Templated {var_name} as {_v!r}")


# The following are provided via runpy.run_path's init_globals keyword
# in conf.py. Uncomment for easy debugger run without IDE config.
try:
    _ = GIT_REF  # noqa
except Exception as _:
    GIT_REF = "development"
    announce_templating("GIT_REF")
try:
    _URL_BASE = "https://github.com/pythonarcade/arcade"
    _ = FMT_URL_REF_PAGE  # noqa
except Exception as _:
    FMT_URL_REF_PAGE = f"{_URL_BASE}/blob/{GIT_REF}/{{}}"
    announce_templating("FMT_URL_REF_PAGE")
try:
    _ = FMT_URL_REF_EMBED  # noqa
except Exception as _:
    FMT_URL_REF_EMBED = f"{_URL_BASE}/blob/{GIT_REF}/{{}}?raw=true"
    announce_templating("FMT_URL_REF_EMBED")


MODULE_DIR = Path(__file__).parent.resolve()
ARCADE_ROOT = MODULE_DIR.parent
RESOURCE_DIR = ARCADE_ROOT / "arcade" / "resources"
DOC_ROOT = ARCADE_ROOT / "doc"
INCLUDES_ROOT = DOC_ROOT / "_includes"
OUT_FILE = DOC_ROOT / "api_docs" / "resources.rst"


class SupportsLT(Protocol):
   def __lt__(self, other): ...


# Metadata for the resource list: utils\create_resource_list.py
skip_extensions = [
    ".glsl",
    ".md",
    ".py",
    ".yml",
    ".url",
    ".txt",
    ".tiled-project",
    ".pyc",
    ""  # Zero-extension stuff like LICENSE and README
]


def skipped_file(file_path: Path):
    """Return True if file should be skipped."""
    return file_path.suffix in skip_extensions


@lru_cache(maxsize=None)
def get_column_widths_for_n(n: int) -> str:
    width = str(100 // n)
    return ' '.join((width for _ in range(n)))


@lru_cache(maxsize=None)  # Cache b/c re-using elsewhere
def path_as_resource_handle(
    path: Path,
    prefix: str = "",
    suffix: str = "",
    restrict_to_bases=('system', 'assets'),
    relative_to: str | Path = RESOURCE_DIR
) -> str:
    """
    Create a resource path. We will use the resources handle
    and will need to the "assets" and "system" directory
    from the path.
    """
    path = path.relative_to(relative_to)
    base = path.parts[0]
    if not restrict_to_bases or base in restrict_to_bases:
        path = path.relative_to(base)
    else:
        raise ValueError(f"Unexpected path: {path}. Expected one of: {', '.join(repr(b) for b in restrict_to_bases)}")

    parts = [prefix, ":resources:"]
    as_posix = path.as_posix()

    if not as_posix.startswith('/'):
        parts.append('/')
    parts.extend((as_posix, suffix))

    return ''.join(parts)
    #return f"{prefix}:resources:{path.as_posix()}{suffix}"

# NOTE: Max cols up above
KENNEY_TTFS = "Kenney TTFs"
LIBERATION_TTFS = "Liberation TTFs"


# pending: post-3.0 cleanup  # unstructured kludge
REPLACE_TITLE_WORDS = {
    "Kenney": KENNEY_TTFS,
    "Liberation": LIBERATION_TTFS,
    "gui": "GUI",
    "window": "Window & Panel",
    ".": "Top-level Resources"
}


class TableConfigDict(TypedDict):
    widths: NotRequired[str | Sequence[str | int ]]
    header_row: NotRequired[Sequence[str]]


class HeadingConfigDict(TypedDict):
    ref_target: NotRequired[str]
    skip: NotRequired[bool]
    value: NotRequired[str]
    level: NotRequired[int]


class HandleLevelConfigDict(TypedDict):
    heading: NotRequired[HeadingConfigDict]
    include: NotRequired[str]
    list_table: NotRequired[TableConfigDict]


FONT_TABLE_DEFAULTS: TableConfigDict= {
    'widths' : (30, 15, 55),
    'header_row': (
        ':py:class:`font_name <arcade.Text>`',
        "Style(s)",
        ":ref:`Resource Handle <resource_handles>`",
    ),
}

HANDLE_TO_OVERRIDES: dict[str,HandleLevelConfigDict] = {
    ":resources:/": {
        "heading": {
            "value": "Top-Level Resources"
        }
    },
    ":resources:/fonts/ttf/": {
        "heading": {"skip": True}
    },
    ":resources:/fonts/ttf/Kenney/": {
        "heading": {
            "ref_target": "resources-fonts-kenney",
            "value": "Kenney TTFs",
            "level": 2,
        },
        "include": "resources_Kenney.rst",
        "list-table": {**FONT_TABLE_DEFAULTS}
    },
    ":resources:/fonts/ttf/Liberation/": {
        "heading": {
            "ref_target": "resources-fonts-liberation",
            "value": "Liberation TTFs",
            "level": 2,
        },
        "include": "resources_Liberation.rst",
        "list-table": {**FONT_TABLE_DEFAULTS}
    },
    ":resources:/gui_basic_assets/": {
        "heading": {"value": "GUI Basic Assets"},
    },
    ":resources:/gui_basic_assets/window/": {
        "heading": {"value": "Window & Panel"}
    }
}

T = TypeVar('T')


# We have benedict at home
def drill_get(
        m: Mapping[str, Mapping[str, T] | T],
        key: str | Iterable[str],
        default: T
) -> T:
    if isinstance(key, str):
        key = str.split('/')
    current = m
    try:
        for k in key:
            current = current[k]
    except Exception as _:
        return default
    return current


# pending: post-3.0 cleanup  # more unstructured filth
SKIP_HANDLES = set([
    handle for handle, d in HANDLE_TO_OVERRIDES.items()
    if (
        'heading' in d and d['heading'].get('skip', None)
    )
])
# print("ALL_HANDLES", SKIP_HANDLES)
visited_headings = set()


@cache
def format_title_part(raw: str):
    out = []
    for word in raw.split('_'):
        if word in REPLACE_TITLE_WORDS:
            out.append(REPLACE_TITLE_WORDS[word])
        else:
            out.append(word.capitalize())

    return ' '.join(out)


# starts at = for top of page, drill down for here
# https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#sections
headings_lookup = (
    '=',  # Page root heading
    '-',
    '^',
    '"',
)


def do_heading(
        out,
        relative_heading_level: int,
        heading_text: str,
        ref_target: str | None = None
) -> None:
    """Writes a heading to the output file.

    If the page heading is beyond what we have symbols for, the Sphinx
    ``.. rubric::`` directive will be used instead.

    Args:
        out: A file-like object which acts like its opened with ``"w"``
        relative_heading_level: Heading level relative to the page root.
        heading_text: The heading text to display.
        ref_target: ``True`` to auto-generate it or a str to use a specific one.
    """
    out.write("\n")
    print(f"doing heading: {heading_text!r} {relative_heading_level}")
    num_headings = len(headings_lookup)

    if ref_target:
        out.write(f".. _{ref_target}:\n\n")

    if relative_heading_level >= num_headings:
        # pending: post-3.0 cleanup
        log.warning(
            f"Using .. rubric:: due to running out of heading levels:"
            f"({relative_heading_level} >= {num_headings})")
        out.write(f".. rubric:: {heading_text}\n")
    else:
        header_char = headings_lookup[relative_heading_level]
        out.write(f"{heading_text}\n")
        out.write(f"{header_char * (len(heading_text))}\n")
    out.write("\n")


PRIVATE_NAME = re.compile(r'^__')


def is_nonprotected_dir(p: Path):
    return p.is_dir() and not PRIVATE_NAME.match(p.stem)


def is_unskipped_file(p: Path):
    return not (p.is_dir() or p.suffix in skip_extensions)



def filter_dir(
        dir: Path,
        keep: Callable[[Path], bool] = lambda path: True,
        key: Callable[[Path], SupportsLT] | Callable | None = str,
        reverse: bool = False,
) -> list[Path]:
    """Iterate cleanly over directory elements as

    .. warning:: Don't give this or anything in this file circular symlinks.

    Args:
        dir: the directory
        keep: When to keep an item in the directory
        key: how to sort the folder elements
        reverse: whether to reverse the sort
    Returns:
        A list of paths matching keep and sorted by both key and reverse.
    """
    kept = [p for p in dir.iterdir() if keep(p)]
    if key or reverse:
        kept.sort(key=key, reverse=reverse)
    return kept



def smash_iterable(i: str | Iterable[str]):
    if isinstance(i, str):
        return i
    else:
        return ' '.join(i)


_sphinx_option_handlers: dict[str, Callable] = defaultdict(lambda: str)
_sphinx_option_handlers.update({
    'class': smash_iterable,
    'widths': smash_iterable
})


def sphinx_directive(
        name: str,
        *arguments: str,
        options: Mapping[str, str | int | Iterable] | None = None,
        body: str | Iterable | None = None
) -> str:
    lines = [f".. {name}:: {' '.join(arguments)}\n"]

    if options:
        for name, value in options.items():
            converter = _sphinx_option_handlers[name]
            lines.append(
                f"   :{name}: {converter(value)}\n")
        lines.append("\n")
    if body:
        if isinstance(body, str):
            body = (body,)
        # We could use extend but this is nice for debugging
        for i, value in enumerate(body):
            lines.append(indent("   ", value))
        lines.append("\n\n")

    return ''.join(lines)


ALL_THE_PATHS = {}

def process_resource_directory(out, dir: Path):
    """
    Go through resources in a directory.
    """

    for path in filter_dir(dir, keep=is_nonprotected_dir):
        # out.write(f"\n{cur_node.name}\n")
        # out.write("-" * len(cur_node.name) + "\n\n")

        file_list = filter_dir(path, keep=is_unskipped_file)
        num_files = len(file_list)
        def _debug_print_files() -> None:  # pending: post-3.0 cleanup
            """Nasty little temp helper"""
            for file in file_list:
                print(file.name)

        if num_files > 0:
            raw_resource_handle = path_as_resource_handle(path, suffix="/")
            config: HandleLevelConfigDict = HANDLE_TO_OVERRIDES.get(raw_resource_handle, {})
            resource_handle = raw_resource_handle.removesuffix('./')

            # print("CONFIG:\n",
            #       "raw    :", raw_resource_handle, "\n",
            #       "handle :", resource_handle, "\n",
            #       "config :", config)

            parts = raw_resource_handle.replace(":resources:", "").strip("/").split("/")
            display_parts = [format_title_part(part) for part in parts]

            # print("RENDER:")
            # for items in zip(parts, display_parts):
            #     print("   ", *map(repr, items))

            full = [':resources:/']
            for i, part in enumerate(parts, start=1):
                full.append(f"{full[-1]}{part}/")
            print("ALL_TO", full)

            # Process headings and render any new ones we haven't seen
            for heading_level, part in enumerate(display_parts, start=1):
                print("ff", (heading_level, part))
                res_handle_step = full[heading_level]
                if res_handle_step in SKIP_HANDLES:
                    continue
                if res_handle_step in visited_headings:
                    continue

                local_config = drill_get(
                    HANDLE_TO_OVERRIDES, (res_handle_step, 'heading'), {})

                use_level = local_config.get('level', heading_level)
                use_value = local_config.get('value', None)
                if use_value is None:
                    use_value = format_title_part(part)
                use_target = local_config.get('ref_target', None)

                # print("!!!", use_value, use_value, use_target)

                do_heading(out, use_level, use_value, ref_target=use_target)
                visited_headings.add(res_handle_step)

            # Do heading info text

            if include := config.get("include", None):
                if isinstance(include, str):
                    include = INCLUDES_ROOT / include
                out.include_file(include)

            # Ugly table header stuff?
            opts = config.get('list_table', {})

            n_cols = None
            widths = config.get('widths', None)
            header_rows = opts.get('header_row', ())
            if isinstance(widths, str):
                n_cols = len(widths.split()) + 1
            elif widths is not None:
                n_cols = len(widths)
                widths = ''.join(map(str, widths))
            elif widths is None and header_rows:
                n_cols = len(header_rows)
                widths = get_column_widths_for_n(n_cols)
            width = None

            out.write(f"\n")
            # sphinx_directive('list-table', options=opts)
            out.write(f".. list-table:: ``{resource_handle!r}``\n")
            print("widths ", widths)
            if widths:
                out.write(f"    :widths: {widths}\n")
            if header_rows:
                out.write(f"    :header-rows: {len(header_rows)}\n")
            if width:
                out.write(f"    :width: {width}\n")
            out.write(f"    :class: resource-table\n\n")

            # Write header row
            for row in header_rows:
                r_iter = iter(row)
                out.write(f"    * - {next(r_iter)}\n\n")
                for item in r_iter:
                    out.write(f"      - {item}\n\n")
                out.write("\n")

            # Write table body after header
            process_resource_files(out, file_list)
            out.write("\n\n")

        # Recurse dirs
        process_resource_directory(out, path)


SUFFIX_TO_AUDIO_TYPE = {
    '.wav': 'x-wav',
    '.ogg': 'ogg',
    '.mp3': 'mpeg',
}
SUFFIX_TO_VIDEO_TYPE = {
    '.mp4': 'mp4',
    '.webm': 'webm',
    '.avi': 'avi'
}


def code_block(
        inner: str,
        language: str | None = None,
        options: Mapping[str, str | int | Iterable] | None = None
) -> str:
    return sphinx_directive(
        "code-block", language if language else None, "\n",
        options=options,
        body=inner
    )


def indent(  # pending: post-3.0 refactor  # why would indent come after the text?!
        spacing: str,
        to_indent: str,
        as_row: bool = False
) -> str:
    """More readable ergonomics for text wrapping."""

    if not as_row:
        return textwrap.indent(to_indent, spacing)
    raw = StringIO(to_indent)
    new = StringIO()
    it = chain((spacing,), cycle((' ' * len(spacing),)))
    for prefix, line in zip(it, raw.readlines()):
        new.write(textwrap.indent(line, prefix))

    return new.getvalue()


def html_copyable(
        value: str,
        resource_handle: str,
        string_quote_char: str | None = "'"
) -> str:
    if string_quote_char:
        value = f"{string_quote_char}{value}{string_quote_char}"
    escaped = html.escape(value)

    raw = (
        f"<span class=\"resource-handle\">\n"
        f"    <code class=\"docutils literal notranslate\">\n"
        f"        <span class=\"pre\">{escaped}</span>\n"
        f"    </code>\n"
        f"    <button class=\"arcade-ezcopy\" data-clipboard-text=\"{resource_handle}\">\n"
        f"        <img src=\"/_static/copy-button.svg\"/>\n"
        f"    </button>\n"
        f"</span>\n"
        f"<br/>\n\n")

    return raw


def highlight_copyable(out, inner: str) -> None:
    out.write(f".. code-block:: python\n\n")
    out.write(f"   {inner!r}\n\n", "")


# Regex because it's easier to make complicated
BRITTLE_CAP_WORD_REGEX = re.compile(r"[A-Z][a-z0-9]*")
BRITTLE_FONT_NAME_REGEX = re.compile(
    r"""^
    # The 'redundant' \_ escaping improves readability. 
    (?P<face_name>
        [A-Z][a-z0-9]*         # first capitalized word
        (?:\_[A-Z][a-z0-9]*)?  # Optional second title _Word
    ) 
    (?:\_  # Optional FaceStyleWords (Bold, Italic, etc)
        (?P<styles>(?:[A-Z][a-z0-9]*)+)
    )?
    """, re.X)


def extract_ttf_name_data(
        path: Path
):  # pending: find a non-awful way to read metadata?
    face_name_parts = BRITTLE_FONT_NAME_REGEX.match(path.name).groupdict()


def process_resource_files(
        out,
        file_list: List[Path],
        prefix: str = None,
        path: Path = None,
        header_row: Iterable[str] = ()
) -> None:
    """
    Render the table without any recursion or real FS navigation.

    :param out:
    :param file_list:
    :return:
    """
    cell_count = 0
    path = path or file_list[0].parent
    if not prefix:
        prefix = path_as_resource_handle(path, suffix="/")

    COLUMNS: int = 2
    if len(file_list) == 1:
        COLUMNS = 1
    elif path.parent.name == "ttf":
        COLUMNS = 3

    column_iter = cycle(chain('*', ' ' * (COLUMNS - 1)))

    log.info(f"Processing {prefix=!r} with {COLUMNS=!r}, {path.parent.name!r}")

    def start():
        nonlocal cell_count
        cell_count += 1
        return next(column_iter)

    for path in file_list:

        # Shared items
        resource_path = path.relative_to(ARCADE_ROOT).as_posix()
        resource_handle_raw = path_as_resource_handle(path)
        resource_copyable = html_copyable(path.name, resource_handle_raw)

        # Decide how we're going to render the file
        suffix = path.suffix
        if suffix in [".png", ".jpg", ".gif", ".svg"]:
            out.write(f"    {start()} - .. raw:: html\n\n")
            out.write(indent("           ", resource_copyable))

            tile_rst_code = sphinx_directive(
                'image', f'../../{resource_path}',
                options={
                    'class':(
                        'checkered-bg',  # Show transparency via gray tile bg
                        'resource-thumb',  # Clamp max display size
                    ),
                    # lazy helps avoid GitHub and readthedocs from 429ing us ("chill pls")
                    'loading': 'lazy',
                    'name': resource_handle_raw
                }
            )
            out.write(indent("        ", tile_rst_code))

            size_info = None
            if suffix == ".svg":
                size_info = "Scalable Vector Graphic"
            else:
                try:
                    im = PIL.Image.open(path)
                    im_width, im_height = im.size
                    size_info = f"{im_width}px x {im_height}px"
                except Exception as e:
                    log.warning(f"FAILED to read size info for {path}:\n {e}")

            if size_info is None:
                size_info = "Could not read size info"
            out.write(f"        *({size_info})*\n")
            out.write("\n\n")

        elif suffix in SUFFIX_TO_AUDIO_TYPE:
            file_path = FMT_URL_REF_EMBED.format(resource_path)
            out.write(f"    {start()} - .. raw:: html\n\n")
            out.write(indent(
                "           ", resource_copyable))

            src_type=SUFFIX_TO_AUDIO_TYPE[suffix]
            out.write(f"        .. raw:: html\n\n")
            out.write(indent("           ",
                      f"<audio class=\"resource-thumb\" controls>\n"
                      f"  <source src='{file_path}' type='audio/{src_type}'>\n"
                      f"</audio>\n\n"))

        elif suffix in SUFFIX_TO_VIDEO_TYPE:
            file_path = FMT_URL_REF_EMBED.format(resource_path)
            out.write(f"    {start()} - .. raw:: html\n\n")
            out.write(indent(
                      f"             ", resource_copyable))
            out.write("\n")
            src_type = SUFFIX_TO_VIDEO_TYPE[suffix]
            out.write(f"        .. raw:: html\n\n")
            out.write(indent(
                      f"           ",
                      f"<video class=\"resource-thumb\" controls>\n"
                      f"  <source src='{file_path}' type='video/{src_type}'>\n"
                      f"</video>\n\n"))

        # elif suffix == ".glsl":
        #     file_path = FMT_URL_REF_PAGE.format(resource_path)
        #     out.write(f"    {start_row} - `{code_html} <{file_path}>`_\n")
        # Fonts
        elif suffix == ".ttf":
            # The worst code you've ever seen ; v ; 7  # pending: post-3.0 cleanup
            face_name_parts = BRITTLE_FONT_NAME_REGEX.match(path.name).groupdict()
            face_name_pieces = (face_name_parts.get("face_name") or '').split('_')

            raw_name = ' '.join(face_name_pieces)
            face_name = repr(raw_name)
            print(face_name_parts)

            styles = tuple(BRITTLE_CAP_WORD_REGEX.findall(
                face_name_parts.get('styles', None) or ''))

            style_string = ", ".join(styles or ("Regular",))
            # print("row: ", face_name, style_string, code_html)

            out.write(f"    {start()} - .. code-block:: python\n\n")
            out.write(f"           {raw_name!r}\n\n")

            out.write(f"    {start()} - {style_string}\n\n")
            # out.write(indent(f"        ", code_block(resource_copyable, language='python')))
            out.write(f"    {start()} - .. code-block:: python\n\n")
            out.write(f"           {resource_handle_raw!r}\n\n")

        # Tiled maps
        elif suffix == ".json":
            file_path = FMT_URL_REF_PAGE.format(resource_path)
            out.write(f"    {start()} - .. raw:: html\n\n")
            out.write(indent("             ",
                 resource_copyable))

            icon = "tiled_icon_digi_pls_replace.png"
            out.write(indent(f"        ",
                      f".. image:: images/{icon}\n"
                      f"   :class: resource-thumb\n\n"))

        else:
            out.write(f"    {start()} - .. raw:: html\n\n")
            out.write(indent("             ", resource_copyable))
            out.write(indent("             ",
                # SVG styling and alignment seems odd, so we're doing this the flexbox way
                f"<div class=\"resource-thumb file-icon unknown-file-type\">\n"
                f"  <p>???</p>\n"
                f"  <p>Unknown Filetype</p>\n"
                f"</div>\n\n"
            ))
        # The below doesn't work because of how raw HTML / Sphinx images interact:
        # out.write(f"            <br /><code class='literal'>{resource_copyable}</code>\n")

    # Finish any remaining columns with empty cells
    while cell_count % COLUMNS > 0:
        out.write(f"    {start()} -\n")


def resources():
    out = vfs.open(OUT_FILE, "w")

    out.write(".. _resources:\n")

    do_heading(out, 0, "Built-In Resources")

    out.write("\n")
    out.write("Linking test: :ref:`:resources:gui_basic_assets/window/panel_green.png:`.\n")
    out.write("Every file below is included when you :ref:`install Arcade <install>`. This includes the images,\n"
              "sounds, fonts, and other files to help you get started quickly. You can still download them\n"
              "separately, but Arcade's resource handle system will usually be easier.\n")
    do_heading(out, 1, "Do I have to credit anyone?")
    # Injecting the links.rst doesn't seem to be working?
    out.write("That's a good question and one you should always ask when searching for assets online.\n"
              "To help users get started quickly, the Arcade team makes sure to only bundle assets which\n"
              # pending: post-3.0 cleanup # Why does it refuse to accept external links definitions? Who knows?
              "are specifically released under `CC0  <https://creativecommons.org/publicdomain/#publicdomain-cc0-10>`_"
              " or similar terms.\n")
    out.write("Most are from `Kenney.nl <https://kenney.nl/>`_.\n") # pending: post-3.0 cleanup.

    do_heading(out, 1, "How do I use these?")
    out.write(
        "Arcade projects can use any file on this page by passing a **resource handle** prefix.\n"
        "These are strings which start with ``\":resources:\"``. To learn more, please see the following:\n\n"
        "* :ref:`Sprite Examples <sprite_examples>` for example code\n"
        "* :ref:`The Platformer Tutorial <platformer_tutorial>` for step-by-step guidance\n"
        "* The :ref:`resource_handles` page of the manual covers them in more depth\n")

    out.write("\n")
    process_resource_directory(out, RESOURCE_DIR)

    out.close()
    print("Done creating resources.rst")


vfs = Vfs()


def main():
    resources()
    vfs.write()


if __name__ == '__main__':
    main()
