"""
Quick Index Generator

Generate quick API indexes in Restructured Text Format for Sphinx documentation.
"""
import math
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import List
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
    ".ttf",
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
) -> str:
    """
    Create a resource path. We will use the resources handle
    and will need to the "assets" and "system" directory
    from the path.
    """
    path = path.relative_to(RESOURCE_DIR)
    if path.parts[0] == "system":
        path = path.relative_to("system")
    elif path.parts[0] == "assets":
        path = path.relative_to("assets")
    else:
        raise ValueError(f"Unexpected path: {path}")

    return f"{prefix}:resources:{path.as_posix()}{suffix}"


def process_resource_directory(out, dir: Path):
    """
    Go through resources in a directory.
    """
    for path in dir.iterdir():
        if not path.is_dir() or path.name.endswith("__"):
            continue
        # out.write(f"\n{cur_node.name}\n")
        # out.write("-" * len(cur_node.name) + "\n\n")

        file_list = [item for item in path.iterdir() if not (item.is_dir() or skipped_file(item))]
        num_files = len(file_list)
        if num_files > 0:

            # header_title = f":resources:{path.relative_to(RESOURCE_DIR).as_posix()}/"
            raw_header = create_resource_path(path, suffix="/")
            header_title = raw_header[:-2] if raw_header.endswith("./") else raw_header

            if raw_header == ":resources:images/":
                for f in file_list:
                    print(f.name)
            # out.write(f"\n{header_title}\n")
            # out.write("-" * (len(header_title)) + "\n\n")

            n_cols = get_header_num_cols(raw_header, num_files)
            widths = get_column_widths_for_n(n_cols)

            out.write(f"\n")
            out.write(f".. list-table:: \"{header_title}\"\n")
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
        elif suffix == ".json":
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
    out.write("\n")
    out.write("Built-In Resources\n")
    out.write("==================\n")
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
