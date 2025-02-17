"""
Loads the Arcade version into a Python-readable VERSION string.

For everyday use in your projects, you may want to use the ``VERSION``
string from the :py:mod:`arcade` module's top level instead:

.. code-block:: python

   import arcade

   if arcade.version < "3.0.0":
       print("This game requires Arcade 3.0.0+ to run1")

This loads and converts the ``VERSION`` file's contents before storing
them in the ``VERSION`` attribute. We have convert it because we use a
GitHub Action to auto-bump our version after making a release.

When a release build succeeds, our GitHub CI then does the following:

#. Pushes the package files to PyPI
#. Calls the ``remorses/bump-version@js`` action to bump Arcade's version
   on the development branch

The auto-bump action is configured by the following file:
https://github.com/pythonarcade/arcade/blob/development/.github/workflows/bump_version.yml

Python expects a different format than the GH action does for dev previews.

Python expects the following format:

.. code-block::

   3.1.0.dev6

However, the GH action bumps the following preview format after a
release succeeds:

.. code-block::

   3.1.0-dev.5

...to this:

.. code-block::

   3.1.0-dev.6

The functions in this file convert and load the data to ``VERSION`` so
we can import it in the top-level ``__init__.py`` file.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_HERE = Path(__file__).parent

# Grab version numbers + optional dev point preview
# Assumes $MAJOR.$MINOR.$POINT format with optional -dev$DEV_PREVIEW
_VERSION_REGEX = re.compile(
    r"""
    (?P<major>[0-9]+)
    \.(?P<minor>[0-9]+)
    \.(?P<point>[0-9]+)
    (?:
        -dev              # Dev prefix read as a literal
        \.(?P<dev>[0-9]+) # Dev preview point number
    )?
    """, re.X)


def _parse_python_friendly_version(version_for_github_actions: str) -> str:
    """Convert a GitHub CI version string to a Python-friendly one.

    Args:
        version_for_github_actions:
            A raw GitHub CI version string, as read from a file.
    Returns:
        A Python-friendly version string.
    """
    # Extract our raw data
    if not isinstance(version_for_github_actions, str):
        raise TypeError(
            f"Expected a string of the format MAJOR.MINOR.POINT or MAJOR.MINOR.POINT-dev.DEV_PREVIEW,"
            f"not {version_for_github_actions!r}"
        )

    match = _VERSION_REGEX.fullmatch(version_for_github_actions.strip())
    if match is None:
        raise ValueError(f"String does not appear to be a version number: {version_for_github_actions!r}")

    group_dict = match.groupdict()
    for name in ('major', 'minor', 'point'):
        if group_dict[name] is None:
            raise ValueError(f"Couldn't parse {name} from {version_for_github_actions!r}")

    # Append an optional Python-friendly dev preview version
    major, minor, point, dev_preview = group_dict.values()
    parts = [major, minor, point]
    if dev_preview is not None:
        parts.append(f"dev{dev_preview}")
    joined = ".".join(parts)

    return joined


def _parse_py_version_from_github_ci_file(
        version_path: str | Path = _HERE / "VERSION",
        write_errors_to = sys.stderr
) -> str:
    """Parse a Python-friendly version from a ``bump-version``-compatible file.

    On failure, it will:

    #. Print an error to stderr
    #. Return "0.0.0"

    Args:
        version_path:
            The VERSION file's path, defaulting to the same directory as
            this file.
        write_errors_to:
            Makes CI simpler by allowing a stream mock to be passed easily.
    Returns:
        Either a converted version or "0.0.0" on failure.
    """
    data = "0.0.0"
    try:
        raw = Path(version_path).resolve().read_text().strip()
        data = _parse_python_friendly_version(raw)
    except Exception as _:
        print(f"ERROR: Unable to load version number via '{str(version_path)}'.", file=write_errors_to)

    return data


VERSION = _parse_py_version_from_github_ci_file()
