import os
import glob
import shutil
import re

from pathlib import Path


def search_files(file_pattern, reg_pattern):
    # Validate HTML files
    html_files = glob.glob(file_pattern, recursive=True)

    regex = re.compile(reg_pattern)
    grand_total = 0
    file_count = 0
    for file_name in html_files:
        file_count += 1
        line_no = 0
        with open(file_name, encoding="utf8") as f:
            for line in f:
                line_no += 1
                result = regex.search(line)
                if result:
                    print(f"  {file_name}:{line_no}: " + line.strip())
                    grand_total += 1
    print(f"{grand_total} across {file_count} files.")
    return grand_total


def generic_test(title, file_pattern, text_pattern):
    print()
    print(title)
    search_files(file_pattern, text_pattern)


def main():
    # Remove old directory
    generic_test("LINE_LENGTH", "../arcade/examples/**/*.py", "^.{115}.*$")


main()
