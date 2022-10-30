import os.path


dirname = os.path.dirname(__file__) or '.'
my_path = f"{dirname}/VERSION"

try:
    text_file = open(my_path, "r")
    data = text_file.read().strip()
    text_file.close()
except:
    print(f"ERROR: Unable to load version number via {my_path}.")
    data = "0.0.0"

VERSION = data
