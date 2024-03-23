"""
Import and run all examples one frame
"""
import contextlib
import io
import inspect
import importlib
import os
# import time
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


def list_examples():
    for example in EXAMPLE_DIR.glob("*.py"):
        if example.stem.startswith("_"):
            continue
        yield f"arcade.examples.{example.stem}", True


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
    "module_path, allow_stdout",
    list_examples(),
)


def test_examples(window_proxy, module_path, allow_stdout):
    """Run all examples"""
    os.environ["ARCADE_TEST"] = "TRUE"

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        # Function based example will run on import.
        # This is fine because the window_tools fixture patches arcade.open_window
        module = importlib.import_module(module_path)
        # importlib.reload(module)

        window_cls = find_class_inheriting_from_window(module)
        main_func = find_main_function(module)

        if window_cls:
            assert main_func, f"Expected a main function in {module_path}"
            # Run the example
            main_func()
            # time.sleep(1)

    if not allow_stdout:
        output = stdout.getvalue()
        assert not output, f"Example {module_path} printed to stdout: {output}"
