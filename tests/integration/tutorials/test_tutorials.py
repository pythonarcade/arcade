"""
Find and run all tutorials in the doc/tutorials directory
"""

import contextlib
import io
import os
import runpy
import sys
from pathlib import Path

import pytest

import arcade

TUTORIAL_DIR = Path(arcade.__file__).parent.parent / "doc" / "tutorials"
ALLOW_STDOUT = {}


def find_tutorials():
    for path in TUTORIAL_DIR.rglob("*.py"):
        if path.stem.startswith("_"):
            continue
        yield path, path.stem in ALLOW_STDOUT


# Some tutorial steps use draw_text, which warns that it's slow
@pytest.mark.filterwarnings("ignore::arcade.exceptions.PerformanceWarning")
@pytest.mark.parametrize(
    "file_path, allow_stdout",
    list(find_tutorials()),
)
def test_tutorials(window_proxy, file_path, allow_stdout):
    """Run all tutorials"""
    if file_path.parent.name == "compute_shader" and sys.platform == "darwin":
        raise pytest.skip("compute_shader tutorial not working on MacOS")

    os.environ["ARCADE_TEST"] = "TRUE"
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        # Run the tutorial as __main__, as `python -m` would
        os.chdir(file_path.parent)
        runpy.run_path(str(file_path), run_name="__main__")

    if not allow_stdout:
        output = stdout.getvalue()
        assert not output, f"Example {file_path} printed to stdout: {output}"
