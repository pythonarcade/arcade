"""
Quick Index Generator

Generate quick API indexes in Restructured Text Format for Sphinx documentation.
"""

import re
import os
import shutil
from pathlib import Path

def list_functions(filename, output_file):
    """
    Use a regular expression to output all the functions in a file
    Args:
        filename:
        output_file:

    Returns:

    """
    file_pointer = open(filename)
    file_split = filename.replace("/", ".")
    file_split = file_split.split(".")

    file_text = file_pointer.read()
    my_re = re.compile("\ndef ([a-z][^\\(]*)")
    functions = my_re.findall(file_text)
    functions.sort()
    first = True

    cr_re = re.compile(r"\n *")
    for function in functions:
        function = cr_re.sub(" ", function)
        if first:
            first = False
            output_file.write("Functions\n")
            output_file.write("^^^^^^^^^\n")
        output_file.write("- ")
        # module = file_split[4]
        output_file.write(f":func:`~arcade.{function}`")
        output_file.write("\n")
    if not first:
        output_file.write("\n")


def list_classes(filename, output_file):
    """
    Use regular expressions to output all the classes and methods in a file
    Args:
        filename:
        output_file:

    Returns:

    """
    print(filename)
    file_pointer = open(filename)
    file_split = filename.replace("/", ".")
    file_split = file_split.split(".")

    class_re = re.compile("^class ([A-Za-z]+[^\(:]*)")
    method_re = re.compile("^    def ([a-z][a-z_]*)")
    # remove_self_re = re.compile(r"self(, )?")
    first = True

    line_no = 0
    try:
        for line in file_pointer:
            line_no += 1

            class_names = class_re.findall(line)
            if len(class_names) > 0:
                if first:
                    first = False
                    output_file.write("Classes\n")
                    output_file.write("^^^^^^^\n")
                output_file.write("- ")
                # module = file_split[4]
                class_name = class_names[0]
                output_file.write(f":class:`~arcade.{class_name}`")
                output_file.write("\n")

            method_names = method_re.findall(line)
            for method_name in method_names:
                # method_name = name[2]
                output_file.write(f"   - :func:`~arcade.{class_name}.{method_name}`\n")
                # name = remove_self_re.sub("", name)

        if not first:
            output_file.write("\n")
    except Exception as e:
        print(f"Exception processing {filename} on line {line_no}: {e}")


def quick_api():
    # Set the working directory (where we expect to find files) to the same
    # directory this .py file is in. You can leave this out of your own
    # code, but it is needed to easily run the examples using "python -m"
    # as mentioned at the top of this program.
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)

    output_file = open("quick_index.rst", "w")

    output_file.write(".. _quick-index:\n\n")

    output_file.write("Quick API Index\n")
    output_file.write("===============\n")
    output_file.write("\n")

    output_file.write("Window API\n")
    output_file.write("----------\n")
    output_file.write("\n")
    list_classes("../arcade/window_commands.py", output_file)
    list_functions("../arcade/window_commands.py", output_file)
    output_file.write("\n")

    output_file.write("Application API\n")
    output_file.write("---------------\n")
    output_file.write("\n")
    list_classes("../arcade/application.py", output_file)
    list_functions("../arcade/application.py", output_file)

    output_file.write("Arcade Types API\n")
    output_file.write("----------------\n")
    output_file.write("\n")
    list_classes("../arcade/application.py", output_file)
    list_functions("../arcade/application.py", output_file)

    output_file.write("Buffered Drawing API\n")
    output_file.write("--------------------\n")
    output_file.write("\n")
    list_classes("../arcade/buffered_draw_commands.py", output_file)
    list_functions("../arcade/buffered_draw_commands.py", output_file)

    output_file.write("Drawing API\n")
    output_file.write("-----------\n")
    output_file.write("\n")
    list_classes("../arcade/draw_commands.py", output_file)
    list_functions("../arcade/draw_commands.py", output_file)

    output_file.write("Emitter API\n")
    output_file.write("-----------\n")
    output_file.write("\n")
    list_classes("../arcade/emitter.py", output_file)
    list_functions("../arcade/emitter.py", output_file)

    output_file.write("Emitter Simple API\n")
    output_file.write("------------------\n")
    output_file.write("\n")
    list_classes("../arcade/emitter_simple.py", output_file)
    list_functions("../arcade/emitter_simple.py", output_file)

    output_file.write("Geometry API\n")
    output_file.write("------------\n")
    output_file.write("\n")
    list_classes("../arcade/geometry.py", output_file)
    list_functions("../arcade/geometry.py", output_file)

    output_file.write("GUI API\n")
    output_file.write("-------\n")
    output_file.write("\n")
    list_classes("../arcade/gui.py", output_file)
    list_functions("../arcade/gui.py", output_file)

    output_file.write("Text API\n")
    output_file.write("--------\n")
    output_file.write("\n")
    list_classes("../arcade/text.py", output_file)
    list_functions("../arcade/text.py", output_file)

    output_file.write("Game Controller API\n")
    output_file.write("-------------------\n")
    output_file.write("\n")
    list_classes("../arcade/joysticks.py", output_file)
    list_functions("../arcade/joysticks.py", output_file)

    output_file.write("Sound API\n")
    output_file.write("---------\n")
    output_file.write("\n")
    list_classes("../arcade/sound.py", output_file)
    list_functions("../arcade/sound.py", output_file)

    output_file.write("Sprite API\n")
    output_file.write("----------\n")
    output_file.write("\n")
    list_classes("../arcade/sprite.py", output_file)
    list_functions("../arcade/sprite.py", output_file)

    output_file.write("SpriteList API\n")
    output_file.write("--------------\n")
    output_file.write("\n")
    list_classes("../arcade/sprite_list.py", output_file)
    list_functions("../arcade/sprite_list.py", output_file)

    output_file.write("Physics Engines Module\n")
    output_file.write("----------------------\n")
    output_file.write("\n")
    list_classes("../arcade/physics_engines.py", output_file)
    list_functions("../arcade/physics_engines.py", output_file)

    output_file.write("Tiled Map API\n")
    output_file.write("-------------\n")
    output_file.write("\n")
    list_classes("../arcade/tilemap.py", output_file)
    list_functions("../arcade/tilemap.py", output_file)

    output_file.close()

def process_resource_directory(out, my_path: Path):

    for cur_node in my_path.iterdir():

        r1 = cur_node.relative_to('.')
        r3 = 'resources/' + str(r1)[20:].replace('\\', '/')
        # print(r3)
        if cur_node.is_dir():

            has_files = False
            for check_node in cur_node.iterdir():
                if check_node.is_file():
                    has_files = True
                    break

            try:
                os.makedirs(f"build/html/{r3}")
            except FileExistsError:
                pass

            # out.write(f"\n{cur_node.name}\n")
            # out.write("-" * len(cur_node.name) + "\n\n")
            process_resource_directory.cell_count = 0

            if has_files:
                out.write(f"\n\n:resources:{r3[10:]}/\n")
                out.write("-" * (len(r3) + 2) + "\n\n")

                out.write(".. raw:: html\n\n")
                out.write("    <table class='resource-table'><tr>\n")
                process_resource_files(out, cur_node)
                out.write("    </tr></table>\n")

            process_resource_directory(out, cur_node)


def process_resource_files(out, my_path: Path):
    for cur_node in my_path.iterdir():
        r1 = cur_node.relative_to('.')
        r3 = 'resources/' + str(r1)[20:].replace('\\', '/')
        # print(r3)
        if not cur_node.is_dir():
            r2 = ":resources:" + str(r1)[20:].replace('\\', '/')
            if process_resource_directory.cell_count % 3 == 0:
                out.write(f"    </tr>\n")
                out.write(f"    <tr>\n")
            if r2.endswith(".png") or r2.endswith(".jpg") or r2.endswith(".gif") or r2.endswith(".svg"):
                out.write(f"    <td>")
                out.write(f"<a href='{r3}'><img alt='{r2}' title='{r2}' src='{r3}'></a><br />")
                out.write(f"{cur_node.name}")
                process_resource_directory.cell_count += 1
                out.write("</td>\n")
            elif r2.endswith(".wav"):
                out.write(f"    <td>")
                out.write(f"<audio controls><source src='{r3}' type='audio/x-wav'></audio><br />")
                out.write(f"{cur_node.name}")
                process_resource_directory.cell_count += 1
                out.write("</td>\n")
            elif r2.endswith(".mp3"):
                out.write(f"    <td>")
                out.write(f"<audio controls><source src='{r3}' type='audio/mpeg'></audio><br />")
                out.write(f"{cur_node.name}")
                process_resource_directory.cell_count += 1
                out.write("</td>\n")
            elif r2.endswith(".ogg"):
                out.write(f"    <td>")
                out.write(f"<audio controls><source src='{r3}' type='audio/ogg'></audio><br />")
                out.write(f"{cur_node.name}")
                process_resource_directory.cell_count += 1
                out.write("</td>\n")
            elif r2.endswith(".url") or r2.endswith(".txt"):
                pass
            else:
                out.write(f"    <td>")
                out.write(f"{cur_node.name}")
                process_resource_directory.cell_count += 1
                out.write("</td>\n")
            # out.write(f"<br />{r2}</td>")
            src = r1
            dst = f"build\\html\\{r3}"
            shutil.copyfile(src, dst)


process_resource_directory.cell_count = 0

def resources():
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)
    try:
        os.makedirs("build/html/resources")
    except FileExistsError:
        pass

    out = open("resources.rst", "w")

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


def main():
    # quick_api()
    resources()


if __name__ == '__main__':
    main()
