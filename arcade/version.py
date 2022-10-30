import os


# open text file in read mode
path = f"{os.path.dirname(__file__)}\VERSION"

try:
    text_file = open(path, "r")

    # read whole file to a string
    data = text_file.read().strip()

    # close file
    text_file.close()
except:
    print(f"ERROR: Unable to load version number via {path}.")
    data = "0.0.0"

VERSION = data
