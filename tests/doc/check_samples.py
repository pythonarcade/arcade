"""
Each example file in /arcade/examples should have an rst file in /doc/examples

This program sees where there is not a match.
"""

import os


def main():
    mypath = "../../arcade/examples"

    # Get list of python files
    python_example_filename_list = []
    filenames = os.listdir(mypath)
    for filename in filenames:
        if filename.endswith(".py"):
            python_example_filename_list.append(filename)

    # Get list of rst files
    mypath = "../../doc/examples"
    python_rst_filename_list = []
    filenames = os.listdir(mypath)
    for filename in filenames:
        if filename.endswith(".rst"):
            python_rst_filename_list.append(filename)

    # See if there are rst files for all the py files
    for py_file in python_example_filename_list:
        base_name = py_file[:len(py_file) - 3]
        rst_name = base_name + ".rst"
        if rst_name not in python_rst_filename_list:
            print("Missing " + rst_name)

    # See if there are py files for all the rst files
    print()
    for rst_file in python_rst_filename_list:
        base_name = rst_file[:len(rst_file) - 4]
        py_name = base_name + ".py"
        if py_name not in python_example_filename_list:
            print("Missing " + py_name)

main()
