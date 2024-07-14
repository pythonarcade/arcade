"""
Utility for finding long lines in example.

This causes issues when displaying in docs because the code will
visually be cut off on the right side.
"""
import re
from pathlib import Path

EXAMPLE_ROOT = Path(__file__).resolve().parent.parent / "arcade" / "examples"
IGNORE_PATTERNS = [
    "examples/gl/",
    "examples/perf_test/",
]

def is_ignored(path: Path):
    path_str = str(path.as_posix())
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return True 

    return False


def search_files(path: Path, reg_pattern):
    paths = path.glob("**/*.py") 

    regex = re.compile(reg_pattern)
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
                result = regex.search(line)
                if result:
                    print(f"  {path.relative_to(EXAMPLE_ROOT)}:{line_no}: " + line.strip())
                    grand_total += 1

    print(f"{grand_total} across {file_count} files.")
    return grand_total


def main():
    # Look for lines in examples with line length > 115
    print()
    print("LINE_LENGTH")
    search_files(path=EXAMPLE_ROOT, reg_pattern="^.{97}.*$")


main()
