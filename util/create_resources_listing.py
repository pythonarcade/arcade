"""
Quick Index Generator

Generate quick API indexes in Restructured Text Format for Sphinx documentation.
"""
import sys
from pathlib import Path
from typing import List

# Ensure we get utility and arcade imports first
sys.path.insert(0, str(Path(__file__).parent.resolve()))
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import arcade
from vfs import Vfs

MODULE_DIR = Path(__file__).parent.resolve()
ARCADE_ROOT = MODULE_DIR.parent
RESOURCE_DIR = ARCADE_ROOT / "arcade" / "resources"
OUT_FILE = ARCADE_ROOT / "doc" / "api_docs" / "resources.rst"
RESOURCE_URL = "https://github.com/pythonarcade/arcade/blob/development/arcade/{}?raw=true"

COLUMNS = 3
skip_extensions = arcade.resources._resource_list_skip_extensions


def skipped_file(file_path: Path):
    """Return True if file should be skipped."""
    return file_path.suffix in skip_extensions


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
        if len(file_list) > 0:
            # header_title = f":resources:{path.relative_to(RESOURCE_DIR).as_posix()}/"
            header_title = create_resource_path(path, suffix="/")
            if header_title == ":resources:images/":
                for f in file_list:
                    print(f.name)
            # out.write(f"\n{header_title}\n")
            # out.write("-" * (len(header_title)) + "\n\n")

            out.write(f"\n")
            out.write(f".. list-table:: {header_title}\n")
            out.write(f"    :widths: 33 33 33\n")
            out.write(f"    :header-rows: 0\n")
            out.write(f"    :class: resource-table\n\n")

            process_resource_files(out, file_list)
            out.write("\n\n")

        process_resource_directory(out, path)


def process_resource_files(out, file_list: List[Path]):
    start_row = True
    cell_count = 0

    for path in file_list:
        resource_path = path.relative_to(ARCADE_ROOT).as_posix()

        if cell_count % COLUMNS == 0:
            start_row = "*"
        if path.suffix in [".png", ".jpg", ".gif", ".svg"]:
            out.write(f"    {start_row} - .. image:: ../../{resource_path}\n\n")
            out.write(f"        {path.name}\n")
            cell_count += 1
        elif path.suffix == ".wav":
            file_path = RESOURCE_URL.format(resource_path)
            out.write(f"    {start_row} - .. raw:: html\n\n")
            out.write(f"            <audio controls><source src='{file_path}' type='audio/x-wav'></audio><br />{path.name}\n")
            cell_count += 1
        elif path.suffix == ".mp3":
            file_path = RESOURCE_URL.format(resource_path)
            out.write(f"    {start_row} - .. raw:: html\n\n")
            out.write(f"            <audio controls><source src='{file_path}' type='audio/mpeg'></audio><br />{path.name}\n")
            cell_count += 1
        elif path.suffix == ".ogg":
            file_path = RESOURCE_URL.format(resource_path)
            out.write(f"    {start_row} - .. raw:: html\n\n")
            out.write(f"            <audio controls><source src='{file_path}' type='audio/ogg'></audio><br />{path.name}\n")
            cell_count += 1
        elif path.suffix == ".glsl":
            file_path = RESOURCE_URL.format(resource_path)
            out.write(f"    {start_row} - `{path.name} <{file_path}>`_\n")
            # out.write(f"    {start_row} - .. raw:: html\n\n")
            # out.write(f"            <audio controls><source src='{file_path}' type='audio/ogg'></audio><br />{path.name}\n")
            cell_count += 1
        else:
            out.write(f"    {start_row} - {path.name}\n")
            cell_count += 1

        start_row = " "

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
