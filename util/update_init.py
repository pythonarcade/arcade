import re
import os


def get_member_list(filename):
    file_pointer = open(filename)

    class_re = re.compile("^class ([A-Za-z0-9]+[^\(:]*)")
    function_re = re.compile("^def ([a-z][a-z0-9_]*)")
    type_re = re.compile("^([A-Za-z][A-Za-z0-9_]*) = ")
    class_list = []
    function_list = []
    type_list = []
    line_no = 0
    try:
        for line in file_pointer:
            line_no += 1

            class_names = class_re.findall(line)
            for class_name in class_names:
                class_list.append([filename, class_name])

            function_names = function_re.findall(line)
            for method_name in function_names:
                function_list.append([filename, method_name])

            type_names = type_re.findall(line)
            for type_name in type_names:
                type_list.append([filename, type_name])

    except Exception as e:
        print(f"Exception processing {filename} on line {line_no}: {e}")

    class_list.sort()
    function_list.sort()
    type_list.sort()
    return type_list, class_list, function_list


def main():

    with open('template_init.py', 'r') as content_file:
        init_template = content_file.read()

    with open('template_quick_index.rst', 'r') as content_file:
        quick_index_content = content_file.read()

    text_data = []
    text_classes = []
    text_functions = []

    os.chdir("../arcade")
    file_list = "window_commands.py", \
                "application.py", \
                "arcade_types.py", \
                "earclip_module.py", \
                "utils.py", \
                "drawing_support.py", \
                "buffered_draw_commands.py", \
                "draw_commands.py", \
                "geometry.py", \
                "gui.py", \
                "isometric.py", \
                "joysticks.py", \
                "emitter.py", \
                "emitter_simple.py", \
                "particle.py", \
                "sound.py", \
                "sprite.py", \
                "sprite_list.py", \
                "physics_engines.py", \
                "read_tiled_map.py", \
                "text.py", \
                "tilemap.py", \
                "utils.py", \
                "version.py"

    all_list = []

    for filename in file_list:
        type_list, class_list, function_list = get_member_list(filename)
        for member in type_list:
            init_template += f"from .{member[0][:-3]} import {member[1]}\n"
            all_list.append(member[1])
        for member in class_list:
            init_template += f"from .{member[0][:-3]} import {member[1]}\n"
            all_list.append(member[1])
        for member in function_list:
            init_template += f"from .{member[0][:-3]} import {member[1]}\n"
            all_list.append(member[1])

        init_template += "\n"

        for item in type_list:
            text_data += [f"- :data:`~arcade.{item[1]}`\n"]
        for item in function_list:
            text_functions += [f"- :func:`~arcade.{item[1]}`\n"]
        for item in class_list:
            text_classes += [f"- :class:`~arcade.{item[1]}`\n"]


    init_template += "\n__all__ = ["
    all_list.sort()
    first = True
    for item in all_list:
        if not first:
            init_template += "           "
        else:
            first = False
        init_template += f"'{item}',\n"
    init_template += "           ]\n\n"

    text_file = open("__init__.py", "w")
    text_file.write(init_template)
    text_file.close()

    text_data.sort()
    text_functions.sort()
    text_classes.sort()

    text_file = open("../doc/quick_index.rst", "w")
    text_file.write(quick_index_content)

    text_file.write("\n\nClasses\n")
    text_file.write("-------\n")
    for item in text_classes:
        text_file.write(item)

    text_file.write("\n\nFunctions\n")
    text_file.write("---------\n")
    for item in text_functions:
        text_file.write(item)

    text_file.write("\n\nData\n")
    text_file.write("----\n")
    for item in text_data:
        text_file.write(item)

    text_file.close()


main()
