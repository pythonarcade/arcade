import re


def get_member_list(filename):
    file_pointer = open(filename)

    class_re = re.compile("^class ([A-Za-z0-9]+[^\(:]*)")
    function_re = re.compile("^def ([a-z][a-z0-9_]*)")
    type_re = re.compile("^([A-Za-z][A-Za-z0-9_]*) = ")
    member_list = []
    line_no = 0
    try:
        for line in file_pointer:
            line_no += 1

            class_names = class_re.findall(line)
            for class_name in class_names:
                member_list.append([filename, class_name])

            method_names = function_re.findall(line)
            for method_name in method_names:
                member_list.append([filename, method_name])

            type_names = type_re.findall(line)
            for type_name in type_names:
                member_list.append([filename, type_name])

    except Exception as e:
        print(f"Exception processing {filename} on line {line_no}: {e}")

    member_list.sort()
    return member_list


def main():
    file_list = "window_commands.py", \
                "application.py", \
                "arcade_types.py", \
                "buffered_draw_commands.py", \
                "draw_commands.py", \
                "emitter.py", \
                "emitter_simple.py", \
                "geometry.py", \
                "gui.py", \
                "isometric.py", \
                "joysticks.py", \
                "particle.py", \
                "sound.py", \
                "sprite.py", \
                "sprite_list.py", \
                "physics_engines.py", \
                "read_tiled_map.py", \
                "text.py", \
                "tilemap.py", \
                "utils.py", \
                "version.py", \



    all_list = []

    for filename in file_list:
        member_list = get_member_list(filename)
        for member in member_list:
            print(f"from {member[0][:-3]} import {member[1]}")
            all_list.append(member[1])
        print()

    print("__all__ = [", end="")
    all_list.sort()
    for item in all_list:
        print(f"           '{item}',")
    print("           ]")

main()