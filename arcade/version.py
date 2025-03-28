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

The ``VERSION`` constant in this module will be loaded from a file in the
same directory. It will contain the following:

#. major
#. minor
#. point
#. (Optional) one and _only_ one of:

   * .dev{DEV_PREVIEW_NUMBER}
   * rc{RC_NUMBER}

"""

import re
import sys
from pathlib import Path
from typing import Final

_HERE = Path(__file__).parent

# Grab version numbers + optional dev point preview
# Assumes:
# {MAJOR}.{MINOR}.{POINT} format
# optional: one and ONLY one of:
# 1. dev{DEV_PREVIEW}
# 2. rc{RC_NUMBER}
# Q: Why did you use regex?!
# A: If the dev_preview field is invalid, the whole match fails instantly
_VERSION_REGEX: Final[re.Pattern] = re.compile(
    r"""
    # First three version number fields
      (?P<major>[0-9]+)
    \.(?P<minor>0|[1-9][0-9]*)
    \.(?P<point>0|[1-9][0-9]*)
    # Optional and mutually exclusive: dev preview or rc number
    (?:
        \.(?P<dev_preview>dev(?:0|[1-9][0-9]*))
        |  # XOR: can't be both a preview and an rc
        (?P<rc_number>rc(?:0|[1-9][0-9]*))
    )?
    """,
    re.X,
)


def _parse_python_friendly_version(
    raw_version: str, pattern: re.Pattern[str] = _VERSION_REGEX
) -> str:
    """Read a GitHub CI version string to a Python-friendly one.

    For example, ``3.1.0-dev.1`` would become ``3.1.0.dev1``.

    Args:
        raw_version:
            A raw GitHub CI version string, as read from a file.
    Returns:
        A Python-friendly version string.
    """
    # Quick preflight check: we don't support tuple format here!
    problem = None
    if not isinstance(raw_version, str):
        problem = TypeError
    elif (match := pattern.fullmatch(raw_version)) is None:
        problem = ValueError
    if problem:
        raise problem(
            f"{raw_version=!r} not a str of the format MAJOR.MINOR"
            f"POINT with at most one of dev{{DEV_PREVIEW}} or"
            f"rc{{RC_NUMBER}},"
        )

    # Build final output, including a dev preview version if present
    group_dict: dict[str, str | None] = match.groupdict()  # type: ignore
    parts: list[str] = [group_dict[k] for k in ("major", "minor", "point")]  # type: ignore
    dev_preview, rc_number = (group_dict[k] for k in ("dev_preview", "rc_number"))

    if dev_preview and rc_number:
        raise ValueError(f"Can't have both {dev_preview=!r} and {rc_number=!r}")
    elif dev_preview:
        parts.append(dev_preview)

    joined = ".".join(parts)
    if rc_number:
        joined += rc_number

    return joined


def _parse_py_version_from_file(
    version_path: str | Path = _HERE / "VERSION", write_errors_to=sys.stderr
) -> str:
    """Read & validate the VERSION file as from a limited subset.

    On failure, it will:

    #. Print an error to stderr
    #. Return "0.0.0"
    #. (Indirectly) cause any PyPI uploads to fail

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


VERSION: Final[str] = _parse_py_version_from_file()
"""A Python-friendly version string.

This value is converted from the GitHub-style ``VERSION`` file at the
top-level of the arcade module.
"""
