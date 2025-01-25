from __future__ import annotations

import re
import ast
import dataclasses
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

    Args:
        module: A module path in the project.
    Raises:
        ValueError: When a can't be computed.
    Returns:
        An absolute file path to the module
    """
    # Convert module.name.here to module/name/here
    current = root
    for index, part in enumerate(module.split('.')):
        if not _VALID_MODULE_SEGMENT.fullmatch(part):
            raise ValueError(
                f'Invalid module segment at index {index}: {part!r}')
        # else:
        #     print(current, part)
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


# Tools for resolving the lowest import of a member in Arcade.
# Members are imported in various `__init__` files and we want
# present. arcade.Sprite instead of arcade.sprite.Sprite as an example.
# Build a tree using the ast module looking at the __init__ files
# and recurse the tree to find the lowest import of a member.

@dataclasses.dataclass
class ImportNode:
    """A node in the import tree."""
    name: str
    parent: ImportNode | None = None
    children: list[ImportNode] = dataclasses.field(default_factory=list)
    imports: list[Import] = dataclasses.field(default_factory=list)
    level: int = 0

    def get_full_module_path(self) -> str:
        """Get the module path from the root to this node."""
        if self.parent is None:
            return self.name

        name = self.parent.get_full_module_path()
        if name:
            return f"{name}.{self.name}"
        return self.name

    def resolve(self, full_path: str) -> str:
        """Return the lowest import of a member in the tree."""
        name = full_path.split(".")[-1]

        # Find an import in this module likely to be the one we want.
        for imp in self.imports:
            if imp.name == name and imp.from_module in full_path:
                return f"{imp.module}.{imp.name}"

        # Move on to children
        for child in self.children:
            result = child.resolve(full_path)
            if result:
                return result

        # Return the full path if we can't find any relevant imports.
        # It means the member is in a sub-module and are not importer anywhere.
        return full_path

    def print_tree(self, depth=0):
        """Print the tree."""
        print(" " * depth * 4, "---", self.name)
        for imp in self.imports:
            print(" " * (depth + 1) * 4, f"-> {imp}")
        for child in self.children:
            child.print_tree(depth + 1)


@dataclasses.dataclass
class Import:
    """Unified representation of an import statement."""
    name: str  # name of the member
    module: str  # The module this import is from
    from_module: str  # The module the member was imported from


def build_import_tree(root: Path) -> ImportNode:
    """
    Build a tree of all the modules in a package.

    Args:
        root: The root of the package to build the tree from.
    Returns:
        The root node of the tree.
    """
    node = _parse_import_node_recursive(root, parent=None)
    if node is None:
        raise RuntimeError("No __init__.py found in root")
    return node


def _parse_import_node_recursive(
    path: Path,
    parent: ImportNode | None = None,
    depth=0,
) -> ImportNode | None:
    """Quickly gather import data using ast in a simplified/unified format.

    This is a recursive function that works itself down the directory tree
    looking for __init__.py files and parsing them for imports.
    """
    _file = path / "__init__.py"
    if not _file.exists():
        return None

    # Build the node
    name = _file.parts[-2]
    node = ImportNode(name, parent=parent)
    module = ast.parse(_file.read_text())

    full_module_path = node.get_full_module_path()

    for ast_node in ast.walk(module):
        if isinstance(ast_node, ast.Import):
            for alias in ast_node.names:
                if not alias.name.startswith("arcade."):
                    continue
                imp = Import(
                    name=alias.name.split(".")[-1],
                    module=full_module_path,
                    from_module=".".join(alias.name.split(".")[:-1])
                )
                node.imports.append(imp)
        elif isinstance(ast_node, ast.ImportFrom):
            if ast_node.level == 0 and not ast_node.module.startswith("arcade"):
                continue
            for alias in ast_node.names:
                imp = Import(alias.name, full_module_path, ast_node.module)
                node.imports.append(imp)

    # Recurse subdirectories
    for child_dir in path.iterdir():
        child = _parse_import_node_recursive(child_dir, parent=node, depth=depth + 1)
        if child:
            node.children.append(child)

    return node
