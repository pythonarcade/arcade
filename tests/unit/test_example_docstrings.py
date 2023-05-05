import ast
import importlib
from pathlib import Path
import pkgutil
import arcade.examples

EXAMPLE_ROOT = "arcade.examples"


def test_docstrings():
    """
    Check each example for a docstring with correct run instructions.
    """
    ignore_patterns = ["__", "perf_test", "text_loc"]

    # Get all the modules in the examples directory
    check_submodules(EXAMPLE_ROOT)

    # Check subdirectories
    for path in Path(arcade.examples.__path__[0]).iterdir():
        if not path.is_dir():
            continue

        if any(pattern in path.name for pattern in ignore_patterns):
            continue

        check_submodules(f"{EXAMPLE_ROOT}.{path.name}")


def check_submodules(module_path: str):
    module = importlib.import_module(module_path)
    for finder, name, is_pkg in pkgutil.iter_modules(module.__path__):
        path = Path(finder.path) / f"{name}.py"
        check_single_example_docstring(path, f"{module_path}.{name}")


def check_single_example_docstring(path: Path, name: str):
    """
    Read & check a single file for an appropriate docstring

    A docstring should consist of the following:

    1. A summary line explaining what it demonstrates per PEP-0257
       (https://peps.python.org/pep-0257/#multi-line-docstrings)
    2. If necessary, a further minimal explanation of how it will do so
    3. A line specifying how this example can be as a module run, usually at
       the end

    Example::

       \"\"\"
       Show a timer on screen

       If Python and Arcade are installed, this example can be run from the command line with:
       python -m arcade.examples.sprite_rooms
       \"\"\"

    :param path: Path to the file
    :param name: Name of module
    """

    # Read the file & extract the docstring
    code = ast.parse(path.read_text())
    docstring = ast.get_docstring(code)

    # print(f"Checking if example {name} has a run instruction..")
    run_line = f"python -m {name}"
    assert docstring is not None, f"{run_line} not in {name} docstring."
    assert run_line in docstring, f"{run_line} not in {name} docstring."
