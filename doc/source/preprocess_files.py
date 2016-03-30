import re


def list_functions(filename, output_file):
    file_pointer = open(filename)
    file_text = file_pointer.read()
    my_re = re.compile("\ndef ([a-z][a-z_]*)")
    functions = my_re.findall(file_text)
    functions.sort()
    first = True
    for function in functions:
        if first:
            first = False
            output_file.write("Functions\n")
            output_file.write("^^^^^^^^^\n")
        output_file.write("- ")
        output_file.write(function)
        output_file.write("\n")
    if not first:
        output_file.write("\n")


def list_classes(filename, output_file):
    file_pointer = open(filename)
    file_text = file_pointer.read()
    my_re = re.compile("\nclass ([A-Za-z]+)")
    functions = my_re.findall(file_text)
    functions.sort()
    first = True
    for function in functions:
        if first:
            first = False
            output_file.write("Classes\n")
            output_file.write("^^^^^^^\n")
        output_file.write("- ")
        output_file.write(function)
        output_file.write("\n")
    if not first:
        output_file.write("\n")


def main():
    output_file = open("quick_index.rst", "w")
    output_file.write("Quick Index\n")
    output_file.write("===========\n")
    output_file.write("\n")

    output_file.write("Window\n")
    output_file.write("------\n")
    output_file.write("\n")
    list_classes("../../arcade/window_commands.py", output_file)
    list_functions("../../arcade/window_commands.py", output_file)
    output_file.write("\n")

    output_file.write("Drawing\n")
    output_file.write("-------\n")
    output_file.write("\n")
    list_classes("../../arcade/draw_commands.py", output_file)
    list_functions("../../arcade/draw_commands.py", output_file)

    output_file.write("Geometry\n")
    output_file.write("--------\n")
    output_file.write("\n")
    list_classes("../../arcade/geometry.py", output_file)
    list_functions("../../arcade/geometry.py", output_file)

    output_file.write("Sprite\n")
    output_file.write("------\n")
    output_file.write("\n")
    list_classes("../../arcade/sprite.py", output_file)
    list_functions("../../arcade/sprite.py", output_file)

    output_file.write("Physics Engines\n")
    output_file.write("---------------\n")
    output_file.write("\n")
    list_classes("../../arcade/physics_engines.py", output_file)
    list_functions("../../arcade/physics_engines.py", output_file)

    output_file.write("Application\n")
    output_file.write("-----------\n")
    output_file.write("\n")
    list_classes("../../arcade/application.py", output_file)
    list_functions("../../arcade/application.py", output_file)

    output_file.close()
