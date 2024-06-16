from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from .vfs import VirtualFile, Vfs, F


__all__ = (
    'get_module_path',
    'EMPTY_TUPLE',
    'F',
    'SharedPaths',
    'NotExcludedBy',
    'VirtualFile',
    'Vfs'
)


EMPTY_TUPLE = tuple()


class SharedPaths:
    """These are often used to set up a Vfs and open files."""
    REPO_UTILS_DIR = Path(__file__).parent.parent.resolve()
    REPO_ROOT = REPO_UTILS_DIR.parent
    ARCADE_ROOT = REPO_ROOT / "arcade"
    DOC_ROOT = REPO_ROOT / "doc"
    API_DOC_ROOT = DOC_ROOT / "api_docs"


class NotExcludedBy:
    """Helper predicate for exclusion.

    This is here because we may eventually define excludes at per-module
    level in our config below instead of a single list.
    """
    def __init__(self, collection: Iterable):
        self.items = set(collection)

    def __call__(self, item) -> bool:
        return item not in self.items


_VALID_MODULE_SEGMENT = re.compile(r"[_a-zA-Z][_a-z0-9]*")


def get_module_path(module: str, root = SharedPaths.REPO_ROOT) -> Path:
    """Quick-n-dirty module path estimation relative to the repo root.

    :param module: A module path in the project.
    :raises ValueError: When a can't be computed.
    :return: A
    """
    # Convert module.name.here to module/name/here
    current = root
    for index, part in enumerate(module.split('.')):
        if not _VALID_MODULE_SEGMENT.fullmatch(part):
            raise ValueError(
                f'Invalid module segment at index {index}: {part!r}')
        # else:
        #   print(current, part)
        current /= part

    # Account for the two kinds of modules:
    # 1. arcade/module.py
    # 2. arcade/module/__init__.py
    as_package = current / "__init__.py"
    have_package = as_package.is_file()
    as_file = current.with_suffix('.py')
    have_file = as_file.is_file()

    # TODO: When 3.10 becomes our min Python, make this a match-case?
    if have_package and have_file:
        raise ValueError(
            f"Module conflict between {as_package} and {as_file}")
    elif have_package:
        current = as_package
    elif have_file:
        current = as_file
    else:
        raise ValueError(
            f"No folder package or file module detected for "
            f"{module}")

    return current
