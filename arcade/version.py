import os


# open text file in read mode
try:
    text_file = open(f"{os.path.dirname(__file__)}\VERSION", "r")

    # read whole file to a string
    data = text_file.read().strip()

    # close file
    text_file.close()
except:
    print("ERROR: Unable to load version number.")
    data = "0.0.0"

VERSION = data
