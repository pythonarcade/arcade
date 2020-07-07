import re
import os
from string import Template


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
                if type_name not in ['LOG']:
                    type_list.append([filename, type_name])

    except Exception as e:
        print(f"Exception processing {filename} on line {line_no}: {e}")

    class_list.sort()
    function_list.sort()
    type_list.sort()
    return type_list, class_list, function_list


def main():

    with open('template_init.py', 'r') as content_file:
        init_template = Template(content_file.read())

    text_data = []
    text_classes = []
    text_functions = []

    os.chdir("../arcade")
    file_list = (
        "window_commands.py",
        "application.py",
        "arcade_types.py",
        "earclip_module.py",
        "utils.py",
        "drawing_support.py",
        "texture.py",
        "buffered_draw_commands.py",
        "draw_commands.py",
        "geometry.py",
        "isometric.py",
        "joysticks.py",
        "emitter.py",
        "emitter_simple.py",
        "particle.py",
        "sound.py",
        "sprite.py",
        "sprite_list.py",
        "physics_engines.py",
        "text.py",
        "tilemap.py",
        "pymunk_physics_engine.py",
        "version.py",
        "paths.py",
        "context.py",
    )


    import_strings = ""
    all_strings = ""
    all_list = []

    for filename in file_list:
        type_list, class_list, function_list = get_member_list(filename)

        for member in type_list:
            import_strings += f"from .{member[0][:-3]} import {member[1]}\n"
            all_list.append(member[1])
        for member in class_list:
            import_strings += f"from .{member[0][:-3]} import {member[1]}\n"
            all_list.append(member[1])
        for member in function_list:
            import_strings += f"from .{member[0][:-3]} import {member[1]}\n"
            all_list.append(member[1])

        import_strings += "\n"

        for item in type_list:
            text_data += [f"- :data:`~arcade.{item[1]}`\n"]
        for item in function_list:
            text_functions += [f"- :func:`~arcade.{item[1]}`\n"]
        for item in class_list:
            text_classes += [f"- :class:`~arcade.{item[1]}`\n"]

    all_strings += "\n__all__ = ["
    all_list.sort()
    first = True
    for item in all_list:
        if not first:
            all_strings += "           "
        else:
            first = False
        all_strings += f"'{item}',\n"
    all_strings += "           ]\n\n"

    all_strings += "__version__ = VERSION\n"

    text_file = open("__init__.py", "w")
    text_file.write(init_template.substitute({
        'imports': import_strings,
        'all': all_strings,
    }))
    text_file.close()

    text_data.sort()
    text_functions.sort()
    text_classes.sort()

    text_file.close()


main()
