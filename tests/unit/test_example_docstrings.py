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
        check_code_docstring(path, f"{module_path}.{name}")


def check_code_docstring(path: Path, name: str):
    """
    path: Path to the file
    name: Name of module
    """
    with open(path) as f:
        code = ast.parse(f.read())
        docstring = ast.get_docstring(code)
        run_line = f"python -m {name}"
        # print(f"Checking if example {name} has a run instruction..")
        assert docstring is not None, f"{run_line} not in {name} docstring."
        assert run_line in docstring, f"{run_line} not in {name} docstring."
