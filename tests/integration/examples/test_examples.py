"""
Import and run all examples one frame
"""
import contextlib
import io
import inspect
import os
from importlib.machinery import SourceFileLoader
from pathlib import Path

import arcade
import pytest

# TODO: Also add platform_tutorial and gl
EXAMPLE_DIR = Path(arcade.__file__).parent / "examples"
# These examples are allowed to print to stdout
ALLOW_STDOUT = set([
    "arcade.examples.dual_stick_shooter",
    "arcade.examples.net_process_animal_facts",
])
IGNORE_PATTERNS = [
    'net_process_animal_facts'
]

def list_examples():
    for example in EXAMPLE_DIR.glob("*.py"):
        if example.stem.startswith("_"):
            continue
        if example.stem in IGNORE_PATTERNS:
            continue
        yield f"arcade.examples.{example.stem}", example, True


def find_class_inheriting_from_window(module):
    for name, obj in module.__dict__.items():
        match = inspect.isclass(obj) and issubclass(obj, arcade.Window)
        if match:
            return obj
    return None


def find_main_function(module):
    if "main" in module.__dict__:
        return module.__dict__["main"]
    return None


@pytest.mark.parametrize(
    "module_path, file_path, allow_stdout",
    list_examples(),
)
def test_examples(window_proxy, module_path, file_path, allow_stdout):
    """Run all examples"""
    os.environ["ARCADE_TEST"] = "TRUE"

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        # Manually load the module as __main__ so it runs on import
        loader = SourceFileLoader("__main__", str(file_path))
        loader.exec_module(loader.load_module())

    if not allow_stdout:
        output = stdout.getvalue()
        assert not output, f"Example {module_path} printed to stdout: {output}"
