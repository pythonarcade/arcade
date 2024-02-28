"""
Import and run all examples one frame
"""
import os
import sys
import importlib
import inspect
from pathlib import Path
import arcade
import pyglet
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
        print(f"Running {example}")
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
def test_examples(window_tools, module_path, allow_stdout):
    """Run all examples"""
    os.environ["ARCADE_TEST"] = "TRUE"
    # Function based example will run on import.
    # This is fine because the window_tools fixture patches arcade.open_window
    # TODO: Capture stdout from here
    module = importlib.import_module(module_path)
    # Figure out
    # * Is there a class inheriting from arcade.Window?
    # * Do we have a main function?
    window_cls = find_class_inheriting_from_window(module)
    main_func = find_main_function(module)
    print(window_cls, main_func)

    if window_cls:
        assert main_func, f"Expected a main function in {module_path}"

        # Run the example
        with window_tools.patch_window_as_global_window_subclass(window_cls) as window:
            main_func()


# test_examples()

# Attempt to inject an existing parent instance

# window = arcade.Window(800, 600, "My Title")

# class CustomWindow(arcade.Window):
#     def __init__(self):
#         super().__init__(800, 600, "My Title")
#         self.color = arcade.color.AMAZON

#     def on_draw(self):
#         self.clear()
#         arcade.draw_text("Hello, world", 200, 300, self.color, 20)

# def dummy_func(self, *args, **kwargs):
#     pass

# print(window.__dict__)

# window.__class__ = CustomWindow
# pyglet.window.Window.__init__ = dummy_func
# window.__init__()


# arcade.run()

# print("-" * 100)
# window.__class__ = arcade.Window
# print(window.__dict__)
