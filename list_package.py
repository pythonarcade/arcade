import re
import os


def print_functions(file_name):
    file_handle = open(file_name)
    file_contents = file_handle.read()

    # print(file_contents)

    matches = re.findall("\ndef (\w+)", file_contents)

    for match in matches:
        print(match)


def print_classes(file_name):
    file_handle = open(file_name)
    file_contents = file_handle.read()

    # print(file_contents)

    matches = re.findall("\nclass (\w+)", file_contents)

    for match in matches:
        print(match)

for root, dirs, files in os.walk("arcade"):
    for file_name in files:
        if file_name.endswith(".py"):
            file_name = os.path.join(root, file_name)

            print("-----------")
            print("\nFile: {}".format(file_name))
            print("FUNCTIONS:")
            print_functions(file_name)

            print("\nCLASSES:")
            print_classes(file_name)
