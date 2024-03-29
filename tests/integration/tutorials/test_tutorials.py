"""
FInd and run all tutorials in the doc/tutorials directory
"""
import io
import os
import contextlib
from importlib.machinery import SourceFileLoader
from pathlib import Path
import pytest
import arcade

TUTORIAL_DIR = Path(arcade.__file__).parent.parent / "doc" /"tutorials"
ALLOW_STDOUT = {}


def find_tutorials():
    # Loop the directory of tutorials dirs
    for dir in TUTORIAL_DIR.iterdir():
        if not dir.is_dir():
            continue

        print(dir)
        # Find python files in each tutorial dir
        for file in dir.glob("*.py"):
            if file.stem.startswith("_"):
                continue
            # print("->", file)
            yield file, file.stem in ALLOW_STDOUT


@pytest.mark.parametrize(
    "file_path, allow_stdout",
    find_tutorials(),
)
def test_tutorials(window_proxy, file_path, allow_stdout):
    """Run all tutorials"""
    os.environ["ARCADE_TEST"] = "TRUE"
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        # Manually load the module as __main__ so it runs on import
        os.chdir(file_path.parent)
        loader = SourceFileLoader("__main__", str(file_path))
        loader.exec_module(loader.load_module())

    if not allow_stdout:
        output = stdout.getvalue()
        assert not output, f"Example {file_path} printed to stdout: {output}"
