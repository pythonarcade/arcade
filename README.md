#make.py – Project Task Runner
#explains make.py
make.py is a Python-based task runner that invokes pytest for testing, ruff for linting and formatting, mypy and pyright for static type checking, and sphinx-build.


##Purpose

The make.py script centralizes routine commands used during development, including:

- Documentation builds
- Code formatting and linting
- Static type analysis
- Unit and integration testing

This ensures that contributors use a consistent workflow regardless of operating system or shell environment.

##Requirements
To use make.py, the following Python packages must be available:

- `typer`
- `pytest`
- `ruff`
- `mypy`
- `pyright`
- `sphinx`
- `sphinx-autobuild`

If any of these are missing, make.py will exit with an error message indicating what needs to be installed.

##Command Structure

All commands follow the same pattern:

```bash
python make.py <command>


