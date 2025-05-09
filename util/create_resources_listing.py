"""
Quick Index Generator

Generate quick API indexes in Restructured Text Format for Sphinx documentation.
"""
# fmt: off
# ruff: noqa
import copy
import html
import re
import sys
import textwrap
from collections import defaultdict
from collections.abc import Mapping
from functools import lru_cache, cache
from io import StringIO
from itertools import chain, cycle, islice
from pathlib import Path
from typing import List, Callable, Protocol, Sequence, Iterable, TypeVar, NamedTuple
import logging

import PIL.Image
from typing_extensions import TypedDict, NotRequired, Self

FILE = Path(__file__)

log = logging.getLogger(FILE.name)

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
_ = RTD_EVIL  # noqa  # explode ASAP or the links will all be broken
log.info(f" RTD EVIL: {RTD_EVIL!r}")  # noqa
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


def src_kludge(strpath): # pending: post-3.0 cleanup: # evil evil evil evil
    """We inject what RTD says the canonical domain is up top + the version"""
    return f"{RTD_EVIL}{strpath}"

MODULE_DIR = Path(__file__).parent.resolve()
ARCADE_ROOT = MODULE_DIR.parent
RESOURCE_DIR = ARCADE_ROOT / "arcade" / "resources"
ASSET_DIR = RESOURCE_DIR / "assets"
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
    include: NotRequired[str | bool]
    list_table: NotRequired[TableConfigDict]


FONT_TABLE_DEFAULTS: TableConfigDict= {
    'widths' : (30, 15, 55),
    'header_row': (
        ':py:class:`font_name <arcade.Text>`',
        "Style(s)",
        ":ref:`Resource Handle <resource_handles>`",
    ),
}


RESOURCE_HANDLE_CONFIGS: dict[str,HandleLevelConfigDict] = {
    ":resources:/": {
        "heading": {
            "value": "Top-Level Resources",
            "ref_target": "resources-top-level-resources",
            "level": 1
        },
        "include": "resources_Top-Level_Resources.rst"
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
        "list_table": {**FONT_TABLE_DEFAULTS}
    },
    ":resources:/fonts/ttf/Liberation/": {
        "heading": {
            "ref_target": "resources-fonts-liberation",
            "value": "Liberation TTFs",
            "level": 2,
        },
        "include": "resources_Liberation.rst",
        "list_table": {**FONT_TABLE_DEFAULTS}
    },
    ":resources:/images/": {
        "heading": {
            "value": "Image Theme Sets",
        },
        "include": "resources_Image_Theme_Sets.rst"
    },
    ":resources:/gui_basic_assets/": {
        "heading": {"value": "GUI Basic Assets"},
    },
    ":resources:/gui_basic_assets/window/": {
        "heading": {"value": "Window & Panel"}
    },
    ":resources:/video/": {
        # pending: post-3.0 cleanup # trains are hats
        "heading:": {
            "value": "Video",
            "ref_target": "resources_video"
        },
        "include": "resources_Video.rst"
    }
}

T = TypeVar('T')
R = TypeVar('R')  # Result type


# pending: post-3.0 cleanup  # more unstructured filth
SKIP_HANDLES = set([
    handle for handle, d in RESOURCE_HANDLE_CONFIGS.items()
    if (
        'heading' in d and d['heading'].get('skip', None)
    )
])
# print("ALL_HANDLES", SKIP_HANDLES)


visited_headings = set()


@cache
def format_title_part(raw: str):
    out = [word.capitalize() for word in raw.split('_')]
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
        ref_target: str | bool | None = None
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
    log.info(f"doing heading: {heading_text!r} {relative_heading_level}")
    num_headings = len(headings_lookup)

    if ref_target is True:
        ref_target = f"resources-{heading_text}.rst"
    if ref_target:
        log.info(f"   writing ref target {repr(heading_text)}")
        out.write(f".. _{ref_target.lower()}:\n\n")

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


# Yes, this *is* used: we have a PyInstaller folder!
PRIVATE_NAME = re.compile(r'^__')


def is_nonprotected_dir(p: Path) -> bool:
    """True if ``p`` is a folder which isn't marked with ``__`` or other privacy checks."""
    return p.is_dir() and not PRIVATE_NAME.match(p.stem)


def is_unskipped_file(p: Path) -> bool:
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


def coerce_iterable_to_str(
        i: str | Iterable[T],
        converter: Callable[[T], R] = str
) -> str:
    if isinstance(i, str):
        return i
    else:
        return ' '.join(map(converter, i))


_sphinx_option_handlers: dict[str, Callable] = defaultdict(lambda: str)
_sphinx_option_handlers.update({
    'class': coerce_iterable_to_str,
    'widths': coerce_iterable_to_str,
    'header-row': coerce_iterable_to_str
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


known_dirs = {}


def process_resource_directory(out, dir: Path):
    """
    Go through resources in a directory.
    """

    child_directories = filter_dir(dir, keep=is_nonprotected_dir)
    if dir == RESOURCE_DIR:
        child_directories.sort(reverse=True)

    for path in child_directories:
        # out.write(f"\n{cur_node.name}\n")
        # out.write("-" * len(cur_node.name) + "\n\n")
        temp_rel = path.relative_to(RESOURCE_DIR.parent)
        log.info(f" Checking subdir {temp_rel}...")

        file_list = filter_dir(path, keep=is_unskipped_file)
        num_files = len(file_list)
        if num_files <= 0:
            log.info(f" SKIP: No files... {num_files}")
        else:
            log.info("  HAS FILES!")
            handle_raw = path_as_resource_handle(path, suffix="/")
            config: HandleLevelConfigDict = RESOURCE_HANDLE_CONFIGS.get(handle_raw, {})
            resource_handle = handle_raw.removesuffix('./')

            # print("CONFIG:\n",
            #       "raw    :", raw_resource_handle, "\n",
            #       "handle :", resource_handle, "\n",
            #       "config :", config)

            # Generate a list of full-length resource handles
            handle_steps_parts = resource_handle.strip("/").split("/")
            handle_steps_wholes = [f"{handle_steps_parts[0]}/"]
            for handle_step_whole in islice(handle_steps_parts, 1, len(handle_steps_parts)):
                handle_steps_wholes.append(
                    f"{handle_steps_wholes[-1]}{handle_step_whole}/")

            log.info("  Subdir Config:")
            _l = locals()
            for k in filter(lambda _k: 'handle' in _k and('steps' in _k or _k.count('_') <2), _l.keys()):
                log.info(f"    {k} : {_l.get(k, None)!r}" if k else '')

            # Process headings and render any new ones we haven't seen
            for heading_level, handle_step_whole in enumerate(handle_steps_wholes, start=0):
                log.info("  heading check", (heading_level, handle_step_whole))
                if handle_step_whole in SKIP_HANDLES:
                    log.info("    skipping excluded")
                    continue
                if handle_step_whole in visited_headings:
                    log.info("    skipping visited")
                    continue
                visited_headings.add(handle_step_whole)

                local_config = RESOURCE_HANDLE_CONFIGS.get(handle_step_whole, {})
                local_heading_config = local_config.get('heading', {})

                log.info(
                    ("proceeding... "
                      f"\n   config         {local_config}", 
                      f"\n   heading_config {local_heading_config}"
                    )
                )

                # Heading config fetch and write
                use_level = local_heading_config.get('level', heading_level)
                use_value = local_heading_config.get('value', None)
                use_target = local_heading_config.get('ref_target', None)
                if use_value is None:
                    use_value = format_title_part(handle_steps_parts[heading_level])
                if use_target is None:
                    use_target = f"resources-{use_value.lower()}"

                for k, v in locals().items():
                    if k.startswith("use_"):
                        log.info("%s : %s", repr(k), repr(v))

                log.info(f"  got target: {use_target!r}")
                do_heading(out, use_level, use_value, ref_target=use_target)
                out.write(f"\n.. comment `{handle_step_whole!r}``\n\n")

                # Include any include .rst  # pending: inline via pluginification
                if include := local_config.get("include", None):
                    if isinstance(include, bool) and include:
                        include = f"resources_{use_value}.rst"
                    if isinstance(include, str):
                        include = INCLUDES_ROOT / include
                    log.info(f"     INCLUDE: Include resolving to {include})")
                    out.include_file(include)

            # Write table, header, and stuff after it
            # Calculate configuration
            opts = copy.deepcopy(config.get('list_table', {}))
            parent_name = path.parent.name
            columns = 3 if parent_name == "ttf" else min(len(file_list), 2)

            log.info(f" Rendering table for {path=!r} with {columns=!r}, {parent_name!r}")
            write_list_table_header(out, resource_handle, opts)
            process_resource_files(out, file_list, columns)

        # Recurse dirs
        process_resource_directory(out, path)


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

# pending: post-3.0 cleanup, I don't have time to make this CSS nice right now.
COPY_BUTTON_PATH = "https://raw.githubusercontent.com/pythonarcade/arcade/refs/heads/development/doc/_static/icons/tabler/copy.svg"
#COPY_BUTTON_RAW = (DOC_ROOT / "_static/icons/tabler/copy.svg").read_text().strip() + "\n"


def html_copyable(
        value: str,
        resource_handle: str,
        string_quote_char: str | None = "'"
) -> str:
    if string_quote_char:
        value = f"{string_quote_char}{value}{string_quote_char}"
    escaped = html.escape(value)
    # src = src_kludge(COPY_BUTTON_PATH)
    src = FMT_URL_REF_EMBED.format(COPY_BUTTON_PATH)
    raw = (
        f"<span class=\"resource-handle\">\n"
        f"    <code class=\"docutils literal notranslate\">\n"
        f"        <span class=\"pre\">{escaped}</span>\n"
        f"    </code>\n"
        f"    <button class=\"arcade-ezcopy\" data-clipboard-text=\"{resource_handle}\">\n"
        f"        <img src=\"{COPY_BUTTON_PATH}\"/>\n"
        # + indent("    " * 2, COPY_BUTTON_RAW) +  # pending: post-3.0 cleanup
        f"    </button>\n"
        f"</span>\n"
        f"<br/>\n\n")

    return raw


def highlight_copyable(out, inner: str) -> None:
    out.write(f".. code-block:: python\n\n")
    out.write(f"   {inner!r}\n\n", "")


# Regex because why not? We're detecting CapitalWordBounds.
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


class BrittleFontData(NamedTuple):
    face_name: str
    styles: Iterable[str]

    @classmethod
    def from_path(cls, path: Path) -> Self:
        face_name_parts = BRITTLE_FONT_NAME_REGEX.match(path.name).groupdict()
        face_name_pieces = (face_name_parts.get("face_name") or '').split('_')

        raw_name = ' '.join(face_name_pieces)
        log.info(face_name_parts)

        styles = tuple(BRITTLE_CAP_WORD_REGEX.findall(
            face_name_parts.get('styles', None) or ''))

        return cls(raw_name, styles)


class MediaTypeConfig(TypedDict):
    media_kind: str
    mime_suffix: str


MEDIA_EMBED = {
    '.wav': {
        'media_kind': 'audio',
        'mime_suffix': 'x-wav'
    },
    '.ogg': {
        'media_kind': 'audio',
        'mime_suffix': 'x-wav'
    },
    '.mp3': {
        'media_kind': 'audio',
        'mime_suffix': 'mpeg'
    },
    '.mp4': {
        'media_kind': 'video',
        'mime_suffix': 'mp4'
    },
    '.webm': {
        'media_kind': 'video',
        'mime_suffix': 'webm'
    },
    '.avi': {
        'media_kind': 'video',
        'mime_suffix': 'avi'
    }
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


def write_list_table_header(out, handle: str, options: Mapping | None = None):
    merged = {
        'class': 'resource-table',
        **(options or {})
    }
    if (header_row := merged.pop('header_row', None)) is not None:
        merged['header-rows'] = 1

    out.write(f"\n.. list-table:: ``{handle!r}``\n")
    for k, v in merged.items():
        new_k = k.replace('_', '-')
        new_v = _sphinx_option_handlers[new_k](v)
        out.write(f"    :{new_k}: {new_v}\n")
    out.write("\n")

    # Write header row
    if header_row is not None:
        # this non-repeating style is best for broken header row detection?
        # todo: add strict=True?
        for prefix, col in zip(('*' + ' ' * (len(header_row) - 1)), header_row):
            out.write(f"    {prefix} - {col}\n")
        out.write("\n")



FILETILE_DIR = DOC_ROOT / "_static" / "filetiles"


def do_filetile(out, suffix: str | None = None, state: str = None):
    name = None
    if suffix is not None:
        p = FILETILE_DIR / f"type-{suffix.strip('.')}.png"
        log.info(f" FILETILE: {p}")
        if p.exists():
            log.info(f"    KNOWN! {p.name!r}")
            name = p.name
        else:
            name = f"type-unknown.png"
            log.info("    ... unknown :(")
    else:
        name = "state-error.png"
    out.write(indent(f"        ",
                     f".. raw:: html\n\n"
                     f"   <img class=\"resource-thumb\" src=\"{src_kludge('/_static/filetiles/' + name)}\"/>\n\n"))


# pending: a fix for Pillow / Sphinx interactions?
def read_image_size(path: Path | str) -> tuple[int, int]:
    """Get the size of a raster image and close the file.

    This function ensures Sphinx does not break ``with``
    blocks using  :py:func:`PIL.Image.open`:

    Pillow makes assumptions about streams which Sphinx
    may interfere with:

    #. Pillow assumes things about stream read / write
    #. Sphinx sometimes changes stream read / write global
    #. This makes :py:func:`PIL.Image.open` fail to close files
    #. Python 3.11+ reports unclosed files with warning

    This is where the problem begins:

    * When nitpicky mode is off, the logs are filled with noise
    * When it is on, build can break

    The fix below is good-enough to get build running. To dive
    deper, start with these:

    #. Pillow dislikes things which alter stream read/write
       (See https://github.com/python-pillow/Pillow/issues/2760)
    #. Sphinx overrides logging stream handling
       (See https://www.sphinx-doc.org/en/master/extdev/logging.html#sphinx.util.logging.getLogger)

    Args:
        path: A path to an image file to read the size of.

    Returns:
        A ``(width, height)`` tuple of the image size.
    """
    # Isolating this in a function prevents Sphinx and other
    # "magic" stream things from breaking the context manager.
    # If you care to investigate, see the docstring's links.
    with PIL.Image.open(path) as im:
        return im.size


def read_size_info(path: Path) -> str:
    """Cleanliness wrapper for reading image sizes.

    #. SVGs say they are SVGs
    #. Raster graphics report pixel size
    #. All else says it couldn't get size info.

    Args:
        path: A path to an image file.

    Returns:
        The formatted size info as either dimensions or
        another status string.
    """
    if path.suffix == ".svg":
        return "Scalable Vector Graphic"

    elif (pair := read_image_size(path)):
        width, height = pair
        return f"{width} px x {height} px"

    return "Could not read size info"


def process_resource_files(
        out,
        file_list: List[Path],
        columns: int,
) -> None:
    """
    Render the table without any recursion or real FS navigation.

    :param out:
    :param file_list:
    :return:
    """
    cell_count = 0

    column_iter = cycle(chain('*', ' ' * (columns - 1)))

    def start():
        nonlocal cell_count
        cell_count += 1
        return next(column_iter)

    for path in file_list:

        # Shared items
        resource_path = path.relative_to(ARCADE_ROOT).as_posix()
        resource_handle_raw = path_as_resource_handle(path)
        resource_copyable = html_copyable(path.name, resource_handle_raw)
        resource_handle_no_prefix = resource_handle_raw\
            .replace(':', '')\
            .replace('/', '-')\
            .replace('_', '-')\
            .replace('.', '-')

        # Decide how we're going to render the file
        suffix = path.suffix
        if suffix in [".png", ".jpg", ".gif", ".svg"]:

            out.write(f"    {start()} - .. raw:: html\n\n"
                      + indent("         ", resource_copyable + "\n"))
            parts = []
            # out.write(indent("           ", resource_copyable))

            tile_rst_code = sphinx_directive(
                'image', f'../../{resource_path}',
                options={
                    'class':(
                        'checkered-bg',  # Show transparency via gray tile bg
                        'resource-thumb',  # Clamp max display size
                    ),
                    # lazy helps avoid GitHub and readthedocs from 429ing us ("chill pls")
                    'loading': 'lazy',
                    'name': resource_handle_no_prefix
                }
            )
            parts.append(tile_rst_code + "\n")
            #out.write(indent("        ", tile_rst_code))

            size_info = None
            try:
                size_info = read_size_info(path)
            except Exception as e:
                log.warning(f"FAILED to read size info for {path}:\n {e}")


            parts.append(f"*({size_info})*\n")
            out.write(indent("        ", '\n'.join(parts)))
            out.write("\n\n")

        elif suffix in MEDIA_EMBED:
            config = MEDIA_EMBED[suffix]
            kind = config.get('media_kind')
            mime_suffix = config.get('mime_suffix')
            file_path = FMT_URL_REF_EMBED.format(resource_path)
            #rel = path.relative_to(RESOURCE_DIR)
            #file_path = src_kludge(f"/_static/{str(rel)}")
            out.write(f"    {start()} - .. raw:: html\n\n")
            out.write(indent(
                "           ", resource_copyable))

            out.write(f"        .. raw:: html\n\n")
            out.write(indent("           ",
                      # Using preload="none" is gentler on GitHub and readthedocs
                      f"<{kind} class=\"resource-thumb\" controls preload=\"none\">\n"
                      f"  <source src=\"{file_path}\" type=\"{kind}/{mime_suffix}\">\n"
                      f"  <source src=\"{src_kludge(file_path)}\" type=\"{kind}/{mime_suffix}\">\n"
                      f"</{kind}>\n\n"))

        # Fonts
        elif suffix == ".ttf":

            data = BrittleFontData.from_path(path)

            style_string = ", ".join(data.styles or ("Regular",))

            out.write(f"    {start()} - .. code-block:: python\n\n")
            out.write(f"           {data.face_name!r}\n\n")

            out.write(f"    {start()} - {style_string}\n\n")
            # out.write(indent(f"        ", code_block(resource_copyable, language='python')))
            out.write(f"    {start()} - .. code-block:: python\n\n")
            out.write(f"           {resource_handle_raw!r}\n\n")

        # File tiles we don't have previews for
        else:#  suffix == ".json":
            # file_path = FMT_URL_REF_PAGE.format(resource_path)
            out.write(f"    {start()} - .. raw:: html\n\n")
            out.write(indent("             ",
                 resource_copyable))

            do_filetile(out, suffix=suffix)

    # Finish any remaining columns with empty cells
    while cell_count % columns > 0:
        out.write(f"    {start()} -\n")


def resources():
    out = vfs.open(OUT_FILE, "w")

    out.write(".. _resources:\n")

    do_heading(out, 0, "Built-In Resources")

    # pending: post-3.0 cleanup: get the linking working
    # out.write("\n\n:resource:`:resources:/gui_basic_assets/window/panel_green.png`\n\n")
    # out.write("Linking test: :ref:`resources-gui-basic-assets-window-panel-green-png`.\n")

    out.write("Every file below is included when you :ref:`install Arcade <install>`.\n\n"
              "Afterward, you can try running one of Arcade's :py:ref:`examples <example-code>`,\n"
              "such as the one below:\n\n"
              ".. code-block:: shell\n"
              "   :caption: Taken from :ref:`sprite_collect_coins`\n"
              "\n"
              "   python -m arcade.examples.sprite_collect_coins\n"
              "\n"
              "If the example mini-game runs, every image, sound, font, and example Tiled map below should\n"
              "work with zero additional software. You can still download the resources from this page for\n"
              "convenience, or visit `Kenney.nl`_ for more permissively licensed game assets.\n"
              "\n" 
              "The one feature which may require additional software is Arcade's experimental video playback\n"
              "support. The :ref:`resources-video` section below will explain further.\n")

    do_heading(out, 1, "Do I have to credit anyone?")
    # Injecting the links.rst doesn't seem to be working?
    out.write("That's a good question and one you should always ask when searching for assets online.\n"
              "To help users get started quickly, the Arcade team makes sure to only bundle assets which\n"
              # pending: post-3.0 cleanup # Why does it refuse to accept external links definitions? Who knows?
              "are specifically released under `CC0`_ or similar terms.\n")
    out.write("Most are from `Kenney.nl`_.\n") # pending: post-3.0 cleanup.
    logo = html.escape("'logo.png'")
    do_heading(out, 1, "How do I use these?")
    out.write(
        # '.. |Example Copy Button| raw:: html\n\n'
        # '   <div class="arcade-ezcopy doc-ui-example-dummy" style="display: inline-block;">\n'
        # '      <img src="/_static/copy-button.svg"/>\n\n'
        # '   </div>\n\n'
        # +
        f"Each file preview below has the following items above it:\n\n"
        f".. raw:: html\n\n"
        f"   <ol>\n"
        f"      <li>A <strong>file name</strong> as a single-quoted string (<code class=\"docutils literal notranslate\"><span class=\"pre\">{logo}</span></code>)</li>\n"
        f"      <li>A <strong>copy button</strong> to the right of the string (<div class=\"arcade-ezcopy doc-ui-example-dummy\" style=\"display: inline-block;\">"
        f"<img src=\"{src_kludge('/_static/icons/tabler/copy.svg')}\"></div>)</li>\n"
        f"   </ol>\n\n"
        +
        "Click the button above a preview to copy the **resource handle** string for loading the asset. It should\n"
        "look something like this::\n\n"
        "  ':resources:/logo.png'\n"
        "\n"
        "Each resource preview on this page has a button which copies a corresponding string. These\n"
        "resource handle strings allow using Arcade's built-in assets without worrying where a file is\n"
        "on a computer.\n\n"
        "To learn more, please see:\n\n"
        "* The :ref:`resources-top-level-resources` section for a short tutorial on resource handles\n"
        "* :ref:`example-code` for runnable example code\n"
        "* :ref:`main-page-tutorials` for a step-by-step introduction to Arcade\n"
        "* :ref:`resource_handles` for in-depth explanations of resource handles\n\n"
    )

    out.write("\n")
    process_resource_directory(out, RESOURCE_DIR)

    out.close()
    log.info("Done creating resources.rst")


vfs = Vfs()


def main():
    resources()
    vfs.write()


if __name__ == '__main__':
    main()
