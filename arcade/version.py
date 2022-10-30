import os


def _get_version():
    _dirname = os.path.dirname(__file__) or '.'
    _my_path = f"{_dirname}/VERSION"

    try:
        text_file = open(_my_path, "r")
        data = text_file.read().strip()
        text_file.close()
    except Exception as e:
        print(f"ERROR: Unable to load version number via {_my_path}.")
        data = "0.0.0"

    return data


VERSION = _get_version()
