import re


def list_functions(filename, output_file):
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
        output_file.write(":func:`~arcade."+file_split[1]+"."+function+"`")
        output_file.write("\n")
    if not first:
        output_file.write("\n")


def list_classes(filename, output_file):
    file_pointer = open(filename)
    file_split = filename.replace("/",".")
    file_split = file_split.split(".")

    class_re = re.compile("^class ([A-Za-z]+[^\(:]*)")
    method_re = re.compile("^    def ([a-z][^:]*)|^    def (__init__[^:]*)")
    remove_self_re = re.compile(r"self(, )?")
    first = True

    for line in file_pointer:

        class_names = class_re.findall(line)
        if len(class_names) > 0:
            if first:
                first = False
                output_file.write("Classes\n")
                output_file.write("^^^^^^^\n")
            output_file.write("- ")
            output_file.write(":class:`~arcade."+file_split[1]+"."+class_names[0]+"`")
            output_file.write("\n")

        method_names = method_re.findall(line)
        for name in method_names:
            name = ''.join(name)
            output_file.write("    - ")
            name = remove_self_re.sub("", name)
            output_file.write(name)
            output_file.write("\n")

    if not first:
        output_file.write("\n")


def main():
    output_file = open("doc/quick_index.rst", "w")

    output_file.write(".. _quick-index:\n\n")

    output_file.write("Quick API Index\n")
    output_file.write("===============\n")
    output_file.write("\n")

    output_file.write("Window Module\n")
    output_file.write("-------------\n")
    output_file.write("\n")
    list_classes("arcade/window_commands.py", output_file)
    list_functions("arcade/window_commands.py", output_file)
    output_file.write("\n")

    output_file.write("Drawing Module\n")
    output_file.write("--------------\n")
    output_file.write("\n")
    list_classes("arcade/draw_commands.py", output_file)
    list_functions("arcade/draw_commands.py", output_file)

    output_file.write("Shape Objects Module\n")
    output_file.write("--------------------\n")
    output_file.write("\n")
    list_classes("arcade/shape_objects.py", output_file)
    list_functions("arcade/shape_objects.py", output_file)

    output_file.write("Geometry Module\n")
    output_file.write("---------------\n")
    output_file.write("\n")
    list_classes("arcade/geometry.py", output_file)
    list_functions("arcade/geometry.py", output_file)

    output_file.write("Sprite Module\n")
    output_file.write("-------------\n")
    output_file.write("\n")
    list_classes("arcade/sprite.py", output_file)
    list_functions("arcade/sprite.py", output_file)

    output_file.write("Physics Engines Module\n")
    output_file.write("----------------------\n")
    output_file.write("\n")
    list_classes("arcade/physics_engines.py", output_file)
    list_functions("arcade/physics_engines.py", output_file)

    output_file.write("Application Module\n")
    output_file.write("------------------\n")
    output_file.write("\n")
    list_classes("arcade/application.py", output_file)
    list_functions("arcade/application.py", output_file)

    output_file.close()

if __name__ == '__main__':
    main()
