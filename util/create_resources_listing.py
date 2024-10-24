"""
Quick Index Generator

Generate quick API indexes in Restructured Text Format for Sphinx documentation.
"""
# fmt: off
# ruff: noqa
from __future__ import annotations

import math
import re
import sys
from collections import defaultdict
from functools import lru_cache, cache
from pathlib import Path
from typing import List, Callable, Protocol
import logging

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
OUT_FILE = ARCADE_ROOT / "doc" / "api_docs" / "resources.rst"


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
]


def skipped_file(file_path: Path):
    """Return True if file should be skipped."""
    return file_path.suffix in skip_extensions


MAX_COLS: dict[str, int] = defaultdict(lambda: 3)
MAX_COLS[":resources:sounds/"] = 2


@lru_cache(maxsize=None)
def get_header_num_cols(resource_stub: str, n_files = math.inf) -> int:
    return int(min(MAX_COLS[resource_stub], n_files))


@lru_cache(maxsize=None)
def get_column_widths_for_n(n: int) -> str:
    width = str(100 // n)
    return ' '.join((width for _ in range(n)))


@lru_cache(maxsize=None)  # Cache b/c re-using elsewhere
def create_resource_path(
    path: Path,
    prefix: str = "",
    suffix: str = "",
    restrict_to_bases=('system', 'assets')
) -> str:
    """
    Create a resource path. We will use the resources handle
    and will need to the "assets" and "system" directory
    from the path.
    """
    path = path.relative_to(RESOURCE_DIR)
    base = path.parts[0]
    if not restrict_to_bases or base in restrict_to_bases:
        path = path.relative_to(base)
    else:
        raise ValueError(f"Unexpected path: {path}. Expected one of: {', '.join(repr(b) for b in expect_bases)}")

    return f"{prefix}:resources:{path.as_posix()}{suffix}"


# pending: post-3.0 cleanup  # unstructured kludge
REPLACE_TITLE_WORDS = {
    "ttf": "Kenney TTFs",
    "gui": "GUI",
    "window": "Window & Panel",
    ".": "Top-level Resources"
}
# pending: post-3.0 cleanup  # more unstructured filth
SKIP_TITLES = {
    "Kenney TTFs"
}


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


visited_headings = set()


def do_heading(out, relative_heading_level: int, heading_text: str) -> None:
    """Writes a heading to the output file.

    If the page heading is beyond what we have symbols for, the Sphinx
    ``.. rubric::`` directive will be used instead.

    Args:
        out: A file-like object which acts like its opened with ``"w"``
        relative_heading_level: Heading level relative to the page root.
        heading_text: The heading text to display.

    """
    out.write("\n")
    print(f"doing heading: {heading_text!r} {relative_heading_level}")
    num_headings = len(headings_lookup)

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


class SupportsLT(Protocol):
   def __lt__(self, other): ...


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


def process_resource_directory(out, dir: Path):
    """
    Go through resources in a directory.
    """

    for path in filter_dir(dir, keep=is_nonprotected_dir):
        # out.write(f"\n{cur_node.name}\n")
        # out.write("-" * len(cur_node.name) + "\n\n")

        file_list = filter_dir(path, keep=is_unskipped_file)
        num_files = len(file_list)

        if num_files > 0:

            # header_title = f":resources:{path.relative_to(RESOURCE_DIR).as_posix()}/"
            raw_resource_handle = create_resource_path(path, suffix="/")
            resource_handle = raw_resource_handle[:-2] if raw_resource_handle.endswith("./") else raw_resource_handle

            # pending: post-3.0 time to refactor all of this
            parts = raw_resource_handle.replace(":resources:", "").rstrip("/").split("/")
            display_parts = [format_title_part(part) for part in parts]

            for heading_level, part in enumerate(display_parts, start=1):
                if part in SKIP_TITLES:
                    continue
                as_tup = tuple(display_parts[:heading_level])
                if as_tup not in visited_headings:
                    do_heading(out, heading_level, part)
                    visited_headings.add(as_tup)

            if raw_resource_handle == ":resources:images/":
                for f in file_list:
                    print(f.name)

            if raw_resource_handle == ":resources:fonts/ttf/":
                for f in file_list:
                    print(f.name)
                # pending: post-3.0 cleanup
                out.write("\n")
                out.write(".. figure:: images/fonts_blue.png\n")
                out.write("   :alt: The bundled Kenney.nl fonts.\n")
                out.write("\n")
                out.write("   Arcade includes the following fonts from `Kenney.nl's font pack <https://kenney.nl/assets/kenney-fonts>`_\n")
                out.write("   are available using the path and filenames below.\n")

            n_cols = get_header_num_cols(raw_resource_handle, num_files)
            widths = get_column_widths_for_n(n_cols)

            # out.write(f"\n{header_title}\n")
            # out.write("-" * (len(header_title)) + "\n\n")

            out.write(f"\n")
            out.write(f".. raw:: html\n\n")
            out.write(f"   <code class=\"literal resource-category\">{resource_handle}</code>\n")

            # pending: post-3.0 cleanup?
            # ┬─┬ノ( º _ ºノ) <( We're leaving the tables here for now. Grid can be touch )
            #out.write(f".. list-table:: \"{header_title}\"\n")
            out.write(f".. list-table::\n")
            out.write(f"    :widths: {widths}\n")
            out.write(f"    :header-rows: 0\n")
            out.write(f"    :class: resource-table\n\n")

            process_resource_files(out, file_list)
            out.write("\n\n")

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

def process_resource_files(out, file_list: List[Path]):
    cell_count = 0

    prefix = create_resource_path(file_list[0].parent, suffix="/")

    COLUMNS = get_header_num_cols(prefix, len(file_list))

    log.info(f"Processing {prefix=!r} with {COLUMNS=!r}")
    for path in file_list:
        resource_path = path.relative_to(ARCADE_ROOT).as_posix()
        suffix = path.suffix

        if cell_count % COLUMNS == 0:
            start_row = "*"
        else:
            start_row = " "
        name = path.name
        resource_copyable = f"{create_resource_path(path)}"
        if suffix in [".png", ".jpg", ".gif", ".svg"]:
            out.write(f"    {start_row} - .. image:: ../../{resource_path}\n")
            # IMPORTANT:
            # 1. 11 chars to match the start of "image" above
            # 2. :class: checkered-bg to apply the checkers to transparent images
            out.write(f"           :class: checkered-bg\n\n")
            out.write(f"        {name}\n")
        elif suffix in SUFFIX_TO_AUDIO_TYPE:
            file_path = FMT_URL_REF_EMBED.format(resource_path)
            src_type=SUFFIX_TO_AUDIO_TYPE[suffix]
            out.write(f"    {start_row} - .. raw:: html\n\n")
            out.write(f"            <audio controls><source src='{file_path}' type='audio/{src_type}'></audio>\n")
            out.write(f"            <br /><code class='literal'>&quot;{resource_copyable}&quot;</code>\n")
            # out.write(f"            <br /><a href={FMT_URL_REF_PAGE.format(resource_path)}>{path.name} on GitHub</a>\n")
        elif suffix in SUFFIX_TO_VIDEO_TYPE:
            file_path = FMT_URL_REF_EMBED.format(resource_path)
            src_type = SUFFIX_TO_VIDEO_TYPE[suffix]
            out.write(f"    {start_row} - .. raw:: html\n\n")
            out.write(f"            <video style=\"max-width: 100%\" controls><source src='{file_path}' type='video/{src_type}'></video>\n")
            out.write(f"            <br /><code class='literal'>&quot;{resource_copyable}&quot;</code>\n")
        elif suffix == ".glsl":
            file_path = FMT_URL_REF_PAGE.format(resource_path)
            out.write(f"    {start_row} - `{path} <{file_path}>`_\n")
        # Link Tiled maps
        elif suffix in (".json", ".ttf"):
            file_path = FMT_URL_REF_PAGE.format(resource_path)
            out.write(f"    {start_row} - `{name} <{file_path}>`_\n")
        else:
            out.write(f"    {start_row} - {name}\n")
        # The below doesn't work because of how raw HTML / Sphinx images interact:
        # out.write(f"            <br /><code class='literal'>{resource_copyable}</code>\n")
        cell_count += 1

    # Finish any remaining columns with empty cells
    while cell_count % COLUMNS > 0:
        out.write(f"      -\n")
        cell_count += 1


def resources():
    out = vfs.open(OUT_FILE, "w")

    out.write(".. _resources:\n")

    do_heading(out, 0, "Built-In Resources")

    out.write("\n")
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
