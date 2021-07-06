"""
Quick Index Generator

Generate quick API indexes in Restructured Text Format for Sphinx documentation.
"""

import re
import os
import shutil
from pathlib import Path

COLUMNS = 3


def process_resource_directory(out, my_path: Path):

    for cur_node in my_path.iterdir():

        curr_node_rel = cur_node.relative_to('../arcade/')
        if cur_node.is_dir():

            if cur_node.name.endswith("__"):
                continue

            has_files = False
            for check_node in cur_node.iterdir():
                if check_node.is_file():
                    has_files = True
                    break

            os.makedirs(Path("build/html", *curr_node_rel.parts), exist_ok=True)

            # out.write(f"\n{cur_node.name}\n")
            # out.write("-" * len(cur_node.name) + "\n\n")
            process_resource_directory.cell_count = 0

            if has_files:
                header_title = f":resources:{curr_node_rel.relative_to('resources').as_posix()}/"
                # out.write(f"\n{header_title}\n")
                # out.write("-" * (len(header_title)) + "\n\n")

                out.write(f"\n")
                out.write(f".. list-table:: {header_title}\n")
                out.write(f"    :widths: 33 33 33\n")
                out.write(f"    :header-rows: 0\n")
                out.write(f"    :class: resource-table\n\n")

                process_resource_files(out, cur_node)
                out.write("\n\n")

            process_resource_directory(out, cur_node)


def process_resource_files(out, my_path: Path):

    start_row = True
    for cur_node in my_path.iterdir():
        cur_node_rel = cur_node.relative_to('../arcade')
        r1 = cur_node.relative_to('.')
        r3 = 'resources/' + str(r1)[20:].replace('\\', '/')
        if not cur_node.is_dir():
            r2 = f":resources:{cur_node_rel.relative_to('resources').as_posix()}"
            if process_resource_directory.cell_count % COLUMNS == 0:
                start_row = "*"
            if cur_node.suffix in [".png", ".jpg", ".gif", ".svg"]:
                out.write(f"    {start_row} - .. image:: ../arcade/{r3}\n\n")
                out.write(f"        {cur_node.name}\n")
                process_resource_directory.cell_count += 1
            # elif cur_node.suffix == ".wav":
            #     out.write(f"    {start_row} - .. raw:: html\n\n")
            #     out.write(f"            <audio controls><source src='{r3}' type='audio/x-wav'></audio><br />{cur_node.name}\n")
            # elif cur_node.suffix == ".mp3":
            #     out.write(f"    {start_row} - .. raw:: html\n\n")
            #     out.write(f"            <audio controls><source src='{r3}' type='audio/mpeg'></audio><br />{cur_node.name}\n")
            # elif cur_node.suffix == ".ogg":
            #     out.write(f"    {start_row} - .. raw:: html\n\n")
            #     out.write(f"            <audio controls><source src='{r3}' type='audio/ogg'></audio><br />{cur_node.name}\n")
            elif cur_node.suffix in [".url", ".txt"]:
                pass
            else:
                out.write(f"    {start_row} - {cur_node.name}\n")
                process_resource_directory.cell_count += 1

            start_row = " "

    while process_resource_directory.cell_count % COLUMNS > 0:
        out.write(f"      -\n")
        process_resource_directory.cell_count += 1


process_resource_directory.cell_count = 0


def resources():
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)
    try:
        os.makedirs("build/html/resources")
    except FileExistsError:
        pass

    out = open("../doc/resources.rst", "w")

    out.write(".. _resources:\n")
    out.write("\n")
    out.write("Resources\n")
    out.write("=========\n")
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
    process_resource_directory(out, Path('../arcade/resources/'))
    print("Done creating resources.rst")


def main():
    resources()


if __name__ == '__main__':
    main()
