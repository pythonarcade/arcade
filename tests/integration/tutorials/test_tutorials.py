"""
Find and run all tutorials in the doc/tutorials directory
"""
import io
import os
import contextlib
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys

import pytest
import arcade

TUTORIAL_DIR = Path(arcade.__file__).parent.parent / "doc" /"tutorials"
ALLOW_STDOUT = {}


def find_tutorials():
    for path in TUTORIAL_DIR.rglob("*.py"):
        if path.stem.startswith("_"):
            continue
        yield path, path.stem in ALLOW_STDOUT


@pytest.mark.parametrize(
    "file_path, allow_stdout",
    find_tutorials(),
)
def test_tutorials(window_proxy, file_path, allow_stdout):
    """Run all tutorials"""
    if file_path.parent.name == "compute_shader" and sys.platform == "darwin":
        raise pytest.skip("compute_shader tutorial not working on MacOS")

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
