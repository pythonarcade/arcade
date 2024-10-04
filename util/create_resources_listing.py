"""
Quick Index Generator

Generate quick API indexes in Restructured Text Format for Sphinx documentation.
"""

import os
from pathlib import Path
from typing import Callable

# GIT_URL_FILE_ROOT is set via runpy.run_path's init_globals keyword in conf.py
# Uncomment to run from debugger.
# try:
#     _ = GIT_URL_FILE_ROOT
# except Exception as _:
#     GIT_URL_FILE_ROOT = "https://github.com/pythonarcade/blob/2.6.17"

GIT_URL_MODULE_ROOT= f"{GIT_URL_FILE_ROOT}/arcade" # noqa
COLUMNS = 3
COLUMN_PCT_WIDTHS = ' '.join([str(100 // COLUMNS) for _ in range(COLUMNS)])
skip_extensions = frozenset(('.glsl', '.md', '.py', '.yml', '.url', '.txt'))


# Initial debug output
print("Generating resource listing...")
to_show = dict(locals())
for var_name in sorted(to_show.keys()):
    if var_name.startswith("GIT_") or var_name == "skip_extensions":
        print(f"Using {var_name}={to_show[var_name]!r}")


def skip_by_extension(path: Path) -> bool:
    """Debugabble and replaceable condition for skipping files.

    Keeping this separate allows stepping through it in a debugger for
    strange edge cases (.tar.gz if we have to, etc).
    """
    extension = path.suffix
    return extension in skip_extensions


def process_resource_directory(
        out,
        my_path: Path,
        skip_condition: Callable[[Path], bool] = skip_by_extension
):
    """Recursively process a resource directory.

    Args:
         out: A file-like write target.
         my_path: A directory path.
         skip_condition: A callable which tells us when to skip a file.
    """
    for cur_node in my_path.iterdir():

        cur_node_rel = cur_node.relative_to('../arcade/')
        if cur_node.is_dir():

            if cur_node.name.endswith("__"):
                continue

            os.makedirs(Path("build/html", *cur_node_rel.parts), exist_ok=True)

            # out.write(f"\n{cur_node.name}\n")
            # out.write("-" * len(cur_node.name) + "\n\n")
            process_resource_directory.cell_count = 0

            files_to_show = [
                item for item in cur_node.iterdir()
                if not (item.is_dir() or skip_condition(item))
            ]

            if len(files_to_show) > 0:
                header_title = f":resources:{cur_node_rel.relative_to('resources').as_posix()}/"
                if header_title == ":resources:images/":
                    for f in files_to_show:
                        print(f.name)
                # out.write(f"\n{header_title}\n")
                # out.write("-" * (len(header_title)) + "\n\n")

                out.write(f"\n")
                out.write(f".. list-table:: {header_title}\n")
                out.write(f"    :widths: {COLUMN_PCT_WIDTHS}\n")
                out.write(f"    :header-rows: 0\n")
                out.write(f"    :class: resource-table\n\n")

                process_resource_files(out, files_to_show)
                out.write("\n\n")

            process_resource_directory(out, cur_node)


def embed_url(r3, raw: bool = True):
    parts = [GIT_URL_MODULE_ROOT, '/', r3]
    if raw:
        parts.append("?raw=true")
    return ''.join(parts)


def process_resource_files(out, file_list):

    start_row = True
    for cur_node in file_list:
        rel = cur_node.relative_to('.')
        cleaned = '/'.join(rel.parts[3:])
        r3 = f"resources/{cleaned}"

        # r2 = f":resources:{cur_node_rel.relative_to('resources').as_posix()}"
        if process_resource_directory.cell_count % COLUMNS == 0:
            start_row = "*"

        if cur_node.suffix in [".png", ".jpg", ".gif", ".svg"]:
            out.write(f"    {start_row} - .. image:: ../arcade/{r3}\n\n")
            out.write(f"        {cur_node.name}\n")
            process_resource_directory.cell_count += 1
        elif cur_node.suffix == ".wav":
            file_path = embed_url(r3)
            out.write(f"    {start_row} - .. raw:: html\n\n")
            out.write(f"            <audio controls><source src='{file_path}' type='audio/x-wav'></audio><br />{cur_node.name}\n")
            process_resource_directory.cell_count += 1
        elif cur_node.suffix == ".mp3":
            file_path = embed_url(r3)
            out.write(f"    {start_row} - .. raw:: html\n\n")
            out.write(f"            <audio controls><source src='{file_path}' type='audio/mpeg'></audio><br />{cur_node.name}\n")
            process_resource_directory.cell_count += 1
        elif cur_node.suffix == ".ogg":
            file_path = embed_url(r3)
            out.write(f"    {start_row} - .. raw:: html\n\n")
            out.write(f"            <audio controls><source src='{file_path}' type='audio/ogg'></audio><br />{cur_node.name}\n")
            process_resource_directory.cell_count += 1
        elif cur_node.suffix == ".glsl":
            file_path = embed_url(r3, raw=False)
            out.write(f"    {start_row} - `{cur_node.name} <{file_path}>`_\n")
            # out.write(f"    {start_row} - .. raw:: html\n\n")
            # out.write(f"            <audio controls><source src='{file_path}' type='audio/ogg'></audio><br />{cur_node.name}\n")
            process_resource_directory.cell_count += 1
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

    with open("../doc/resources.rst", "w") as out:
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
        process_resource_directory(out, Path('../arcade/resources/'))

    print("Done creating resources.rst")


def main():
    resources()


if __name__ == '__main__':
    main()
