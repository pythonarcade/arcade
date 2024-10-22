"""
Quick Index Generator

Generate quick API indexes in Restructured Text Format for Sphinx documentation.
"""
from __future__ import annotations

import math
import re
import sys
from collections import defaultdict
from functools import lru_cache, cache
from pathlib import Path
from typing import List, Callable, Generator, Protocol
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
    FMT_URL_REF_PAGE  = f"{_URL_BASE}/blob/{GIT_REF}/{{}}"
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


# pending: post-3.0 cleanup
REPLACE_TITLE_WORDS = {
    "ttf": "Kenney TTFs",
    "gui": "GUI",
    "window": "Window & Panel",
    ".": "Top-level Resources"
}
# pending: post-3.0 cleanup
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
headings_lookup = [
    '=',
    '-',
    '^',
    '"',
]

def do_heading(out, title_text: str, page_relative_heading_level: int):
    out.write("\n")
    print(f"doing heading: {title_text!r} {page_relative_heading_level}")
    if page_relative_heading_level >= len(headings_lookup):
        out.write(f".. rubric:: {title_text}")
    else:
        header_char = headings_lookup[page_relative_heading_level]
        out.write(f"{title_text}\n")
        out.write(header_char * (len(title_text)) + "\n")
    out.write("\n")


visited_headings = set()

PRIVATE_NAME = re.compile(r'^__')


def is_nonprotected_dir(p: Path):
    return p.is_dir() and not PRIVATE_NAME.match(p.stem)


class SupportsLT(Protocol):
   def __lt__(self, other): ...


def dir_contents(
        dir: Path,
        keep: Callable[[Path], bool] = lambda path: True,
        key: Callable[[Path], SupportsLT] | Callable | None = None,
        reverse: bool = False
) -> Generator[Path, None, None]:
    kept = []
    # This is "stupid" code to make it easier to debug
    for p in dir.iterdir():
        print("getting ", p)
        if keep(p):
            print("kept it")
            kept.append(p)
    if key or reverse:
        kept.sort(key=key, reverse=reverse)  # type: ignore

    yield from kept



def process_resource_directory(out, dir: Path):
    """
    Go through resources in a directory.
    """

    for path in dir_contents(dir, key=lambda p: str(p), keep=is_nonprotected_dir):
        # out.write(f"\n{cur_node.name}\n")
        # out.write("-" * len(cur_node.name) + "\n\n")

        file_list = [item for item in path.iterdir() if not (item.is_dir() or skipped_file(item))]
        num_files = len(file_list)

        if num_files > 0:

            # header_title = f":resources:{path.relative_to(RESOURCE_DIR).as_posix()}/"
            raw_resource_handle = create_resource_path(path, suffix="/")
            resource_handle = raw_resource_handle[:-2] if raw_resource_handle.endswith("./") else raw_resource_handle

            # pending: post-3.0 time to refactor all of this
            parts = raw_resource_handle.replace(":resources:", "").split("/")
            if parts[-1] == "":
                parts.pop()

            print("got parts", parts)
            display_parts = [format_title_part(part) for part in parts]

            for heading_level, part in enumerate(display_parts, start=1):
                if part in SKIP_TITLES:
                    continue
                as_tup = tuple(display_parts[:heading_level])
                if as_tup not in visited_headings:
                    do_heading(out, part, heading_level)
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

    do_heading(out, "Built-In Resources", 0)

    out.write("\n")
    out.write("Resource files are images and sounds built into Arcade that "
              "can be used to quickly build and test simple code without having "
              "to worry about copying files into the project.\n\n")
    out.write("Any file loaded that starts with ``:resources:`` will attempt "
              "to load that file from the library resources instead of the "
              "project directory.\n\n")
    out.write("Many of the resources come from `Kenney.nl <https://kenney.nl/>`_ ")
    out.write("and are licensed under CC0 (Creative Commons Zero). Be sure to ")
    out.write("check out his web page for a much wider selection of assets.")

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
