"""
Quick Index Generator

Generate quick API indexes in Restructured Text Format for Sphinx documentation.
"""

import re
import os
import shutil
from pathlib import Path


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
                out.write(f"\n{header_title}\n")
                out.write("-" * (len(header_title)) + "\n\n")

                out.write(".. raw:: html\n\n")
                out.write("    <table class='resource-table'><tr>\n")
                process_resource_files(out, cur_node)
                out.write("    </tr></table>\n")

            process_resource_directory(out, cur_node)


def process_resource_files(out, my_path: Path):

    for cur_node in my_path.iterdir():
        # cur_node ..\arcade\resources\tmx_maps\standard_tileset.tsx
        # cur_node_rel tmx_maps\standard_tileset.tsx
        # r1 ..\arcade\resources\tmx_maps\standard_tileset.tsx
        # r3 resources/tmx_maps/standard_tileset.tsx
        # r2 :resources:tmx_maps/standard_tileset.tsx
        cur_node_rel = cur_node.relative_to('../arcade')
        r1 = cur_node.relative_to('.')
        r3 = 'resources/' + str(r1)[20:].replace('\\', '/')
        if not cur_node.is_dir():
            r2 = f":resources:{cur_node_rel.relative_to('resources').as_posix()}"
            if process_resource_directory.cell_count % 3 == 0:
                out.write(f"    </tr>\n")
                out.write(f"    <tr>\n")
            if cur_node.suffix in [".png", ".jpg", ".gif", ".svg"]:
                out.write(f"    <td>")
                out.write(f"<a href='{r3}'><img alt='{r2}' title='{r2}' src='{r3}'></a><br />")
                out.write(f"{cur_node.name}")
                process_resource_directory.cell_count += 1
                out.write("</td>\n")
            elif cur_node.suffix == ".wav":
                out.write(f"    <td>")
                out.write(f"<audio controls><source src='{r3}' type='audio/x-wav'></audio><br />")
                out.write(f"{cur_node.name}")
                process_resource_directory.cell_count += 1
                out.write("</td>\n")
            elif cur_node.suffix == ".mp3":
                out.write(f"    <td>")
                out.write(f"<audio controls><source src='{r3}' type='audio/mpeg'></audio><br />")
                out.write(f"{cur_node.name}")
                process_resource_directory.cell_count += 1
                out.write("</td>\n")
            elif cur_node.suffix == ".ogg":
                out.write(f"    <td>")
                out.write(f"<audio controls><source src='{r3}' type='audio/ogg'></audio><br />")
                out.write(f"{cur_node.name}")
                process_resource_directory.cell_count += 1
                out.write("</td>\n")
            elif cur_node.suffix in [".url", ".txt"]:
                pass
            else:
                out.write(f"    <td>")
                out.write(f"{cur_node.name}")
                process_resource_directory.cell_count += 1
                out.write("</td>\n")
            # out.write(f"<br />{r2}</td>")
            src = r1
            dst = Path("build/html", r3)
            shutil.copyfile(src, dst)


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
