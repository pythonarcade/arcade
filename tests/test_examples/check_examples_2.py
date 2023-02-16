import re
import os
from pathlib import Path


def get_references_in_index():
    txt = Path('../../doc/example_code/how_to_examples/index.rst').read_text()
    references_in_index = re.findall(":ref:`(.*)`", txt)
    return references_in_index

def get_references_in_rsts():
    mypath = Path("../../doc/example_code/how_to_examples/")

    # Get list of python files
    python_example_filename_list = []
    references = []
    filenames = os.listdir(mypath)
    for filename in filenames:
        if filename.endswith(".rst") and filename != "index.rst":
            python_example_filename_list.append(filename)
            txt = Path(mypath / filename).read_text()
            reference = re.findall("\.\. _(.*):", txt)
            references.extend(reference)

    return references

def main():
    references_in_index = get_references_in_index()
    files_to_reference = get_references_in_rsts()

    for reference in files_to_reference:
        if not reference in references_in_index:
            print(f"index.rst is missing any mention of '{reference}'")

    print("Done with checking to make sure references in doc/examples/*.rst are in doc/examples/index.rst")


main()
