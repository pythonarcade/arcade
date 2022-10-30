"""
Version

We are using a github action to bump the VERSION file versions.

2.7.3-dev.5
will go to:
2.7.3-dev.6

Problem is, python doesn't like that last period:
2.7.3-dev.5
should be
2.7.3-dev5
...and our github action doesn't like that pattern.
So this will delete that last period.
"""
import os


def _rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def _get_version():
    dirname = os.path.dirname(__file__) or '.'
    my_path = f"{dirname}/VERSION"

    try:
        text_file = open(my_path, "r")
        data = text_file.read().strip()
        text_file.close()
        data = _rreplace(data, '.', '', 1)
    except Exception as e:
        print(f"ERROR: Unable to load version number via '{my_path}'.")
        print(f"Files in that directory: {os.listdir(my_path)}")
        data = "0.0.0"

    return data


VERSION = _get_version()
