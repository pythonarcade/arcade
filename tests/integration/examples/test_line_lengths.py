"""
Examples should never exceed a certain line length to ensure readability
in the documentation. The source code gets clipped after 90 ish characters.

Adapted from util/check_example_line_length.py
"""

import re
from pathlib import Path
import arcade

EXAMPLE_ROOT = Path(arcade.__file__).resolve().parent / "examples"
IGNORE_PATTERNS = [
    "examples/gl/",  # Not included in docs
    "examples/perf_test/",  # Not included in docs
    "examples/procedural_caves_cellular",  # Contains long link in header
]


def is_ignored(path: Path):
    path_str = str(path.as_posix())
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return True

    return False


def test_line_lengths():
    paths = EXAMPLE_ROOT.glob("**/*.py")

    regex = re.compile("^.{100}.*$")
    grand_total = 0
    file_count = 0

    for path in paths:
        if is_ignored(path):
            continue

        file_count += 1
        line_no = 0
        with open(path, encoding="utf8") as f:
            for line in f:
                line_no += 1
                result = regex.search(line.strip("\r"))
                if result:
                    print(f"  {path.relative_to(EXAMPLE_ROOT)}:{line_no}: " + line.strip())
                    grand_total += 1

    # print(f"{grand_total} across {file_count} files.")
    if grand_total > 0:
        raise AssertionError(f"{grand_total} lines exceed length limit in examples")
