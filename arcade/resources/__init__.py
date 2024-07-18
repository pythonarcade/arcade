from __future__ import annotations

from pathlib import Path
from typing import Sequence
from arcade.utils import warning, ReplacementWarning

#: The absolute path to this directory
RESOURCE_DIR = Path(__file__).parent.resolve()
SYSTEM_PATH = RESOURCE_DIR / "system"
ASSET_PATH = RESOURCE_DIR / "assets"

handles: dict[str, list[Path]] = {
    "resources": [SYSTEM_PATH, ASSET_PATH],
    "assets": [ASSET_PATH],
    "system": [SYSTEM_PATH],
}

__all__ = [
    "resolve_resource_path",
    "resolve",
    "add_resource_handle",
    "get_resource_handle_paths",
]


@warning(warning_type=ReplacementWarning, new_name="resolve")
def resolve_resource_path(path: str | Path) -> Path:
    """
    Attempts to resolve a path to a resource including resource handles.

    If the path is a string it tries to resolve it as a resource handle
    or convert it to a Path object.

    If the path is a Path object it will ``Path.resolve()`` it
    unless it's not absolute and return it.

    Example::

        resolve(":resources:images/cards/cardBack_blue1.png")
        resolve(":my_handle:music/combat.wav")

    :param str | pathlib.Path path: A Path or string
    """
    return resolve(path)


def resolve(path: str | Path) -> Path:
    """
    Attempts to resolve a path to a resource including resource handles.

    If the path is a string it tries to resolve it as a resource handle
    or convert it to a Path object.

    If the path is a Path object it will ``Path.resolve()`` it
    unless it's not absolute and return it.

    Example::

        resolve(":resources:images/cards/cardBack_blue1.png")
        resolve(":my_handle:music/combat.wav")

    :param str | pathlib.Path] path: A Path or string
    """
    # Convert to a Path object and resolve resource handle
    if isinstance(path, str):
        path = path.strip()  # Allow for silly mistakes with extra spaces

        # If the path starts with a colon, it's a resource handle
        if path.startswith(":"):
            path = path[1:]
            try:
                handle, resource = path.split(":")
            except ValueError:
                raise ValueError(f"Invalid resource handle '{path}'")

            while resource.startswith("/") or resource.startswith("\\"):
                resource = resource[1:]

            # Iterate through the paths in reverse order to find the first
            # match. This allows for overriding of resources.
            paths = get_resource_handle_paths(handle)
            for handle_path in reversed(paths):
                path = handle_path / resource
                if path.exists():
                    break
            else:
                searched_paths = "\n".join(f"-> {p}" for p in reversed(paths))
                raise FileNotFoundError(
                    (
                        f"Cannot locate resource '{resource}' using handle "
                        f"'{handle}' in any of the following paths:\n"
                        f"{searched_paths}"
                    )
                )

            # Always convert into a Path object
            path = Path(handle_path / resource)
        else:
            path = Path(path)

    try:
        path = Path(path.resolve(strict=True))
    except AttributeError:
        # WARNING: This is due to an issue caused by Nuitka overriding strings
        #          into janky path object
        path = Path(path.absolute())

    # Always return absolute paths
    # Check for the existence of the file and provide useful feedback to
    # avoid deep stack trace into pathlib
    try:
        # If the path is absolute, just return it. We assume it's valid and resolved.
        if path.is_absolute():
            return path
        return path.resolve(strict=True)
    except FileNotFoundError:
        raise FileNotFoundError(f"Cannot locate resource : {path}")


def add_resource_handle(handle: str, path: str | Path) -> None:
    """
    Add a resource handle or path to an existing handle.

    A handle can point to multiple paths. If a resource is not found in
    the first path, it will look in the next path, and so on. The search
    is done in reverse order, so the last path added is searched first.

    :param handle: The name of the handle
    :param str | pathlib.Path] path: The absolute path to a directory
    """
    if isinstance(path, str):
        path = Path(path)
    elif isinstance(path, Path):
        path = path
    else:
        raise TypeError("Path for resource handle must be a string or Path object")

    if not path.is_absolute():
        raise RuntimeError(
            f"Path for resource handle must be absolute, not relative ('{path}'). "
            "See https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve"
        )

    if not path.exists():
        raise FileNotFoundError(f"Directory '{path}' for handle '{handle}' does not exist")

    paths = handles.setdefault(handle, [])
    # Don't allow duplicate paths
    if path not in paths:
        paths.append(path)


def get_resource_handle_paths(handle: str) -> list[Path]:
    """
    Returns the paths for a resource handle.

    :param handle: The name of the handle
    """
    try:
        return handles[handle]
    except KeyError:
        raise KeyError(f'Unknown resource handle "{handle}"')


def list_built_in_assets(
    *, name: str | None = None, extensions: Sequence[str] | None = None
) -> list[Path]:
    """
    List built in assets in arcade.

    This will traverse the assets directory returning a list of resources
    optionally filtered by name and file extensions.

    Example::

        # Get all assets
        list_built_in_assets()

        # Only get .png files
        list_built_in_assets(extensions=(".png",))

        # Get all card images
        list_built_in_assets(name="card", extensions=(".png", ".jpg"))

    :param name: Include only assets that contain this string in the filename
    :param extensions: A tuple of file extensions to filter by
    :return: A list of absolute paths to requested assets
    """
    all_paths = ASSET_PATH.glob("**/*")
    if extensions is None and name is None:
        return list(all_paths)

    if name:
        name = name.lower()

    filtered_paths: list[Path] = []
    for path in all_paths:
        if extensions and path.suffix not in extensions:
            continue
        if name and name not in path.name.lower():
            continue

        filtered_paths.append(path)

    return filtered_paths


def load_system_fonts() -> None:
    """Loads all the fonts in arcade's system directory.

    Currently this is only the Kenney fonts::

        Kenney_Blocks.ttf
        Kenney_Future.ttf
        Kenney_Future_Narrow.ttf
        Kenney_High.ttf
        Kenney_High_Square.ttf
        Kenney_Mini.ttf
        Kenney_Mini_Square.ttf
        Kenney_Pixel.ttf
        Kenney_Pixel_Square.ttf
        Kenney_Rocket.ttf
        Kenney_Rocket_Square.ttf
    """
    from arcade.text import load_font

    load_font(":system:fonts/ttf/Kenney_Blocks.ttf")
    load_font(":system:fonts/ttf/Kenney_Future.ttf")
    load_font(":system:fonts/ttf/Kenney_Future_Narrow.ttf")
    load_font(":system:fonts/ttf/Kenney_High.ttf")
    load_font(":system:fonts/ttf/Kenney_High_Square.ttf")
    load_font(":system:fonts/ttf/Kenney_Mini.ttf")
    load_font(":system:fonts/ttf/Kenney_Mini_Square.ttf")
    load_font(":system:fonts/ttf/Kenney_Pixel.ttf")
    load_font(":system:fonts/ttf/Kenney_Pixel_Square.ttf")
    load_font(":system:fonts/ttf/Kenney_Rocket.ttf")
    load_font(":system:fonts/ttf/Kenney_Rocket_Square.ttf")
