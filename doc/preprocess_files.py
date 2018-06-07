"""
Quick Index Generator

Generate quick API indexes in Restructured Text Format for Sphinx documentation.
"""

import re
import os


def list_functions(filename, output_file):
    """
    Use a regular expression to output all the functions in a file
    Args:
        filename:
        output_file:

    Returns:

    """
    file_pointer = open(filename)
    file_split = filename.replace("/",".")
    file_split = file_split.split(".")

    file_text = file_pointer.read()
    my_re = re.compile("\ndef ([a-z][^\(]*)")
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
        module = file_split[4]
        output_file.write(f":func:`~arcade.{module}.{function}`")
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
    file_pointer = open(filename)
    file_split = filename.replace("/",".")
    file_split = file_split.split(".")

    class_re = re.compile("^class ([A-Za-z]+[^\(:]*)")
    method_re = re.compile("^    def ([a-z][a-z_]*)")
    # remove_self_re = re.compile(r"self(, )?")
    first = True

    for line in file_pointer:

        class_names = class_re.findall(line)
        if len(class_names) > 0:
            if first:
                first = False
                output_file.write("Classes\n")
                output_file.write("^^^^^^^\n")
            output_file.write("- ")
            module = file_split[4]
            class_name = class_names[0]
            output_file.write(f":class:`~arcade.{module}.{class_name}`")
            output_file.write("\n")

        method_names = method_re.findall(line)
        for method_name in method_names:
            # method_name = name[2]
            output_file.write(f"   - :func:`~arcade.{module}.{class_name}.{method_name}`\n")
            # name = remove_self_re.sub("", name)

    if not first:
        output_file.write("\n")


def main():
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

    output_file.write("Window Module\n")
    output_file.write("-------------\n")
    output_file.write("\n")
    list_classes("../arcade/window_commands.py", output_file)
    list_functions("../arcade/window_commands.py", output_file)
    output_file.write("\n")

    output_file.write("Drawing Module\n")
    output_file.write("--------------\n")
    output_file.write("\n")
    list_classes("../arcade/draw_commands.py", output_file)
    list_functions("../arcade/draw_commands.py", output_file)

    output_file.write("Buffered Drawing Module\n")
    output_file.write("-----------------------\n")
    output_file.write("\n")
    list_classes("../arcade/buffered_draw_commands.py", output_file)
    list_functions("../arcade/buffered_draw_commands.py", output_file)

    output_file.write("Geometry Module\n")
    output_file.write("---------------\n")
    output_file.write("\n")
    list_classes("../arcade/geometry.py", output_file)
    list_functions("../arcade/geometry.py", output_file)

    output_file.write("Sprite Module\n")
    output_file.write("-------------\n")
    output_file.write("\n")
    list_classes("../arcade/sprite.py", output_file)
    list_functions("../arcade/sprite.py", output_file)

    output_file.write("Sprite List Module\n")
    output_file.write("------------------\n")
    output_file.write("\n")
    list_classes("../arcade/sprite_list.py", output_file)
    list_functions("../arcade/sprite_list.py", output_file)

    output_file.write("Physics Engines Module\n")
    output_file.write("----------------------\n")
    output_file.write("\n")
    list_classes("../arcade/physics_engines.py", output_file)
    list_functions("../arcade/physics_engines.py", output_file)

    output_file.write("Application Module\n")
    output_file.write("------------------\n")
    output_file.write("\n")
    list_classes("../arcade/application.py", output_file)
    list_functions("../arcade/application.py", output_file)

    output_file.close()

if __name__ == '__main__':
    main()
