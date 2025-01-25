"""
Version

We are using a github action to bump the VERSION file versions.

2.7.3-dev.5
will go to:
2.7.3-dev.6

Problem is, python doesn't like that last period:
2.7.3-dev.5
should be
2.7.3.dev5
...and our github action doesn't like that pattern.
So this will delete that last period and flip around the dash.

ALSO note that this bumps the version AFTER the deploy.
So if we are at version 2.7.3.dev5 that's the version deploy. Bump will bump it to dev6.
"""

from __future__ import annotations

import os


def _rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def _get_version():
    dirname = os.path.dirname(__file__) or "."
    my_path = f"{dirname}/VERSION"

    try:
        text_file = open(my_path, "r")
        data = text_file.read().strip()
        text_file.close()
        data = _rreplace(data, ".", "", 1)
        data = _rreplace(data, "-", ".", 1)
    except Exception:
        print(f"ERROR: Unable to load version number via '{my_path}'.")
        data = "0.0.0"

    return data


VERSION = _get_version()
