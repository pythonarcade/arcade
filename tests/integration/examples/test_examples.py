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

import arcade.clock

# File path, module path
EXAMPLE_LOCATIONS = [
    (
        Path(arcade.__file__).parent / "examples",
        "arcade.examples"
    ),
    (
        Path(arcade.__file__).parent / "examples" / "platform_tutorial",
        "arcade.examples.platform_tutorial"
    ),
    (
        Path(arcade.__file__).parent / "examples" / "gl",
        "arcade.examples.gl"
    ),
]
# These examples are allowed to print to stdout
ALLOW_STDOUT = set([
    "arcade.examples.dual_stick_shooter",
    "transform_multi",
])
IGNORE_PATTERNS = [
    "net_process_animal_facts",  # Starts network process
    "transform_emit",  # Broken
    "compute",  # Compute shader stuff we can't run in unit test
    "multisample",  # Anything requiring multisampling we can't run in unit test
    "indirect",  # Indirect rendering cannot be run in unit test
    "bindless",  # Bindless textures cannot be run in unit test
]

def list_examples():
    for path, module_path in EXAMPLE_LOCATIONS:
        for example in path.glob("*.py"):
            if example.stem.startswith("_"):
                continue
            def is_ignored(example):
                for pattern in IGNORE_PATTERNS:
                    if pattern in example.stem:
                        return True
                return False
            if is_ignored(example):
                continue
            yield f"{module_path}.{example.stem}", example, True


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
    print(f"Running {module_path}...")

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        # Manually load the module as __main__ so it runs on import
        loader = SourceFileLoader("__main__", str(file_path))
        loader.exec_module(loader.load_module())
        
    # Reset the global clock's tick speed
    # is this a good argument against a global scope clock?
    # yes.
    arcade.clock.GLOBAL_CLOCK.set_tick_speed(1.0)


    if not allow_stdout:
        output = stdout.getvalue()
        assert not output, f"Example {module_path} printed to stdout: {output}"
