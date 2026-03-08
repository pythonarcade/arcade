import re
from typing import Iterable
from pathlib import Path

from .vfs import VirtualFile, Vfs, F
from .import_resolver import build_import_tree

EMPTY_TUPLE = tuple()
_VALID_MODULE_SEGMENT = re.compile(r"[_a-zA-Z][_a-z0-9]*")


class NotExcludedBy:
    """Helper predicate for exclusion.

    This is here because we may eventually define excludes at per-module
    level in our config below instead of a single list.
    """

    def __init__(self, collection: Iterable):
        self.items = set(collection)

    def __call__(self, item) -> bool:
        return item not in self.items


class SharedPaths:
    """These are often used to set up a Vfs and open files."""

    REPO_UTILS_DIR = Path(__file__).parent.parent.resolve()
    REPO_ROOT = REPO_UTILS_DIR.parent
    ARCADE_ROOT = REPO_ROOT / "arcade"
    DOC_ROOT = REPO_ROOT / "doc"
    API_DOC_ROOT = DOC_ROOT / "api_docs"


def get_module_path(module: str, root=SharedPaths.REPO_ROOT) -> Path:
    """Quick-n-dirty module path estimation relative to the repo root.

    Args:
        module: A module path in the project.
    Raises:
        ValueError: When a can't be computed.
    Returns:
        An absolute file path to the module
    """
    # Convert module.name.here to module/name/here
    current = root
    for index, part in enumerate(module.split(".")):
        if not _VALID_MODULE_SEGMENT.fullmatch(part):
            raise ValueError(f"Invalid module segment at index {index}: {part!r}")
        # else:
        #     print(current, part)
        current /= part

    # Account for the two kinds of modules:
    # 1. arcade/module.py
    # 2. arcade/module/__init__.py
    as_package = current / "__init__.py"
    have_package = as_package.is_file()
    as_file = current.with_suffix(".py")
    have_file = as_file.is_file()

    # TODO: When 3.10 becomes our min Python, make this a match-case?
    if have_package and have_file:
        raise ValueError(f"Module conflict between {as_package} and {as_file}")
    elif have_package:
        current = as_package
    elif have_file:
        current = as_file
    else:
        raise ValueError(f"No folder package or file module detected for {module}")

    return current


class SharedPaths:
    """These are often used to set up a Vfs and open files."""

    REPO_UTILS_DIR = Path(__file__).parent.parent.resolve()
    REPO_ROOT = REPO_UTILS_DIR.parent
    ARCADE_ROOT = REPO_ROOT / "arcade"
    DOC_ROOT = REPO_ROOT / "doc"
    API_DOC_ROOT = DOC_ROOT / "api_docs"


def get_module_path(module: str, root=SharedPaths.REPO_ROOT) -> Path:
    """Quick-n-dirty module path estimation relative to the repo root.

    Args:
        module: A module path in the project.
    Raises:
        ValueError: When a can't be computed.
    Returns:
        An absolute file path to the module
    """
    # Convert module.name.here to module/name/here
    current = root
    for index, part in enumerate(module.split(".")):
        if not _VALID_MODULE_SEGMENT.fullmatch(part):
            raise ValueError(f"Invalid module segment at index {index}: {part!r}")
        # else:
        #     print(current, part)
        current /= part

    # Account for the two kinds of modules:
    # 1. arcade/module.py
    # 2. arcade/module/__init__.py
    as_package = current / "__init__.py"
    have_package = as_package.is_file()
    as_file = current.with_suffix(".py")
    have_file = as_file.is_file()

    # TODO: When 3.10 becomes our min Python, make this a match-case?
    if have_package and have_file:
        raise ValueError(f"Module conflict between {as_package} and {as_file}")
    elif have_package:
        current = as_package
    elif have_file:
        current = as_file
    else:
        raise ValueError(f"No folder package or file module detected for {module}")

    return current


__all__ = (
    "get_module_path",
    "SharedPaths",
    "EMPTY_TUPLE",
    "F",
    "NotExcludedBy",
    "VirtualFile",
    "Vfs",
    "build_import_tree",
)
