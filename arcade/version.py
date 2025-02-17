"""
Loads the Arcade version into a Python-readable ``VERSION`` string.

Everyday Arcade users may prefer accessing the ``VERSION`` string
from Arcade's top-level alias:

.. code-block:: python

   import sys
   import arcade

   if arcade.version < "3.0.0":
       # Using file=sys.stderr prints to the error stream (usually prints red)
       print("This game requires Arcade 3.0.0+ to run!", file=sys.stderr)


Arcade contributors will benefit from understanding how and why
this file loads and converts the contents of the ``VERSION`` file.

After a release build succeeds, GitHub's CI is configured to do
the following:

#. Push the package files to PyPI
#. Call the ``remorses/bump-version@js`` action to auto-increment
   Arcade's version on the development branch

This is where an edge case arises:

#. Our CI expects ``3.1.0-dev.1`` for dev preview builds
#. Python expects ``3.1.0.dev1`` for dev preview builds

The ``VERSION`` file in this file's directory stores the version
in the form the GH Action prefers. This allows it to auto-increment
the version number on the ``development`` branch after we make an
Arcade release to PyPI.

The auto-bump action is configured by the following file:
https://github.com/pythonarcade/arcade/blob/development/.github/workflows/bump_version.yml

As an example, the GH action would auto-increment a dev preview's
version after releasing the 5th dev preview of ``3.1.0`` by updating
the ``VERSION`` file from this:

.. code-block::

   3.1.0-dev.5

...to this:

.. code-block::

   3.1.0-dev.6

"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Final

_HERE = Path(__file__).parent

# Grab version numbers + optional dev point preview
# Assumes $MAJOR.$MINOR.$POINT format with optional -dev$DEV_PREVIEW
# Q: Why did you use regex?!
# A: If the dev_preview field is invalid, the whole match fails instantly
_VERSION_REGEX = re.compile(
    r"""
    # First three version number fields
      (?P<major>[0-9]+)
    \.(?P<minor>[0-9]+)
    \.(?P<point>[0-9]+)
    # Optional dev preview suffix
    (?:
        -dev                    # Dev prefix as a literal
        \.                      # Point
        (?P<dev_preview>[0-9]+) # Dev preview number
    )?
    """,
    re.X,
)


def _parse_python_friendly_version(version_for_github_actions: str) -> str:
    """Convert a GitHub CI version string to a Python-friendly one.

    For example, ``3.1.0-dev.1`` would become ``3.1.0.dev1``.

    Args:
        version_for_github_actions:
            A raw GitHub CI version string, as read from a file.
    Returns:
        A Python-friendly version string.
    """
    # Quick preflight check: we don't support tuple format here!
    if not isinstance(version_for_github_actions, str):
        raise TypeError(
            f"Expected a string of the format MAJOR.MINOR.POINT"
            f"or MAJOR.MINOR.POINT-dev.DEV_PREVIEW,"
            f"not {version_for_github_actions!r}"
        )

    # Attempt to extract our raw data
    match = _VERSION_REGEX.fullmatch(version_for_github_actions.strip())
    if match is None:
        raise ValueError(
            f"String does not appear to be a version number: {version_for_github_actions!r}"
        )

    # Build final output, including a dev preview version if present
    group_dict = match.groupdict()
    major, minor, point, dev_preview = group_dict.values()
    parts = [major, minor, point]
    if dev_preview is not None:
        parts.append(f"dev{dev_preview}")
    joined = ".".join(parts)

    return joined


def _parse_py_version_from_github_ci_file(
    version_path: str | Path = _HERE / "VERSION", write_errors_to=sys.stderr
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
    except Exception as e:
        print(
            f"ERROR: Unable to load version number via '{str(version_path)}': {e}",
            file=write_errors_to,
        )

    return data


VERSION: Final[str] = _parse_py_version_from_github_ci_file()
"""A Python-friendly version string.

This value is converted from the GitHub-style ``VERSION`` file at the
top-level of the arcade module.
"""
