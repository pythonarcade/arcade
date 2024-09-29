import ast
import importlib
from pathlib import Path
import pkgutil
import arcade.examples


EXAMPLE_ROOT = "arcade.examples"


def check_single_example_docstring(path: Path, name: str) -> None:
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

    Args:
        path: Path to the file
        name: Name of module
    """

    # Read the file & extract the docstring
    code = ast.parse(path.read_text())
    docstring = ast.get_docstring(code)

    # print(f"Checking if example {name} has a run instruction..")
    run_line = f"python -m {name}"
    assert docstring is not None, f"{run_line} not in {name} docstring."
    assert run_line in docstring, f"{run_line} not in {name} docstring."


def check_submodules(parent_module_absolute_name: str) -> None:
    """
    Check docstrings for all immediate child modules of the passed absolute name

    It is important to understand that module names and file paths are different things:

    * A module name is what Python sees the module's name as (``"arcade.color"``)
    * A file path is the location on disk (``C:\\Users\\Reader\\python_project\game.py``)

    Args:
        parent_module_absolute_name: The absolute import name of the module to check.
    """
    # Get the file system location of the named parent module
    parent_module_info = importlib.import_module(parent_module_absolute_name)
    parent_module_file_path = parent_module_info.__path__

    # Check all modules nested immediately inside it on the file system
    for finder, child_module_name, is_pkg in pkgutil.iter_modules(parent_module_file_path):

        child_module_file_path = Path(finder.path) / f"{child_module_name}.py"
        child_module_absolute_name = f"{parent_module_absolute_name}.{child_module_name}"

        check_single_example_docstring(child_module_file_path, child_module_absolute_name)


def test_docstrings():
    """
    Ensure each user-facing example has a docstring with correct run instructions.
    """

    # Check all immediate child python files in arcade.examples
    check_submodules(EXAMPLE_ROOT)

    # For each immediate child folder module in arcade.examples,
    # check the immediate child python files for correct docstrings.
    for folder_submodule_path in Path(arcade.examples.__path__[0]).iterdir():

        # Skip file modules we already covered above outside the loop
        if not folder_submodule_path.is_dir():
            continue

        folder_submodule_name = folder_submodule_path.name

        # Skip anything which isn't a user-facing example
        if any(pattern in folder_submodule_name for pattern in ("__", "perf_test", "text_loc")):
            continue

        # Check the grandchildren inside the child folder module
        check_submodules(f"{EXAMPLE_ROOT}.{folder_submodule_name}")
