from __future__ import annotations

import ast
import dataclasses
from pathlib import Path


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

    def resolve(self, full_path: str, level=0) -> str | None:
        """Return the lowest import of a member in the tree."""
        name = full_path.split(".")[-1]
        modules = full_path.split(".")

        # Find an import in this module likely to be the one we want.
        for imp in self.imports:
            if imp.name == name and imp.from_module in full_path:
                # print(f"Found: {imp.name} in {imp.module}")
                return f"{imp.module}.{imp.name}"

        # Move on to children
        module = modules[level + 1]
        for child in self.children:
            if child.name == module:
                # print(f"Checking child: {child.name}")
                result = child.resolve(full_path, level + 1)
                if result:
                    return result

        # We're back from recursing and didn't find anything.
        if level == 0:
            return full_path

        # Nothing was found in this subtree.
        return None

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


if __name__ == "__main__":
    # Basic testing. cwd: util/
    root = build_import_tree(Path(__file__).parent.parent.parent.resolve() / "arcade")

    # Check paths
    path = root.resolve("arcade.sprite.Sprite")
    print(path)
    path = root.resolve("arcade.camera.Camera2D")
    print(path)
    path = root.resolve("arcade.camera.data_types.Projector")
    print(path)
