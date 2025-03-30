from pathlib import Path
from typing import Sequence
from arcade.exceptions import warning, ReplacementWarning

#: The absolute path to this directory
RESOURCE_DIR = Path(__file__).parent.resolve()

# The "system" resources common to Arcade
SYSTEM_PATH = RESOURCE_DIR / "system"
FONTS_PATH = SYSTEM_PATH / "fonts"
TTF_PATH = FONTS_PATH / "ttf"

# Basic resources in the :assets: handle
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

    If the path is a Path object it will :py:meth:`~pathlib.Path.resolve` it
    unless it's not absolute and return it.

    Example::

        resolve(":resources:images/cards/cardBack_blue1.png")
        resolve(":my_handle:music/combat.wav")

    Args:
        path: A Path or string
    """
    return resolve(path)


def resolve(path: str | Path) -> Path:
    """
    Attempts to resolve a path to a resource including resource handles.

    If the path is a string it tries to resolve it as a resource handle
    or convert it to a Path object.

    If the path is a Path object it will :py:meth:`~pathlib.Path.resolve` it
    unless it's not absolute and return it.

    Example::

        resolve(":resources:images/cards/cardBack_blue1.png")
        resolve(":my_handle:music/combat.wav")

    Args:
        path: A Path or string
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

    Args:
        handle: The name of the handle
        path: The absolute path to a directory
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

    Args:
        handle: The name of the handle
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

    Args:
        name: Include only assets that contain this string in the filename
        extensions: A tuple of file extensions to filter by
    Returns:
        A list of absolute paths to requested assets
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


def load_kenney_fonts() -> None:
    """Loads all the Kenney.nl fonts bundled with Arcade.

    .. tip:: This function is best for prototyping and experimenting!

         For best performance, you may want to switch to
         :py:class:`arcade.load_font` before release.

    Please see :ref:`resources-fonts-kenney` for previews and
    license information. The filename to load and ``font_name`` to use
    when drawing text are summarized below:

    .. might swap to this style for the resources listing once I figure out how to
    .. cleanly modify the file to use it.

    =========================================  =========================================================================
    ``font_name`` for :py:class:`arcade.Text`  :ref:`Resource handle <resource_handles>` for :py:func:`arcade.load_font`
    =========================================  =========================================================================
    ``"Kenney Blocks"``                        ``:resources:fonts/ttf/Kenney/Kenney_Blocks.ttf``
    ``"Kenney Future"``                        ``:resources:fonts/ttf/Kenney/Kenney_Future.ttf``
    ``"Kenney Future Narrow"``                 ``:resources:fonts/ttf/Kenney/Kenney_Future_Narrow.ttf``
    ``"Kenney High"``                          ``:resources:fonts/ttf/Kenney/Kenney_High.ttf``
    ``"Kenney High Square"``                   ``:resources:fonts/ttf/Kenney/Kenney_High_Square.ttf``
    ``"Kenney Mini"``                          ``:resources:fonts/ttf/Kenney/Kenney_Mini.ttf``
    ``"Kenney Mini Square"``                   ``:resources:fonts/ttf/Kenney/Kenney_Mini_Square.ttf``
    ``"Kenney Pixel"``                         ``:resources:fonts/ttf/Kenney/Kenney_Pixel.ttf``
    ``"Kenney Pixel Square"``                  ``:resources:fonts/ttf/Kenney/Kenney_Pixel_Square.ttf``
    ``"Kenney Rocket"``                        ``:resources:fonts/ttf/Kenney/Kenney_Rocket.ttf``
    ``"Kenney Rocket Square"``                 ``:resources:fonts/ttf/Kenney/Kenney_Rocket_Square.ttf``
    =========================================  =========================================================================

    """  # noqa: E501  # Silence ruff  # pending: better generation
    from arcade.text import load_font

    load_font(":system:fonts/ttf/Kenney/Kenney_Blocks.ttf")
    load_font(":system:fonts/ttf/Kenney/Kenney_Future.ttf")
    load_font(":system:fonts/ttf/Kenney/Kenney_Future_Narrow.ttf")
    load_font(":system:fonts/ttf/Kenney/Kenney_High.ttf")
    load_font(":system:fonts/ttf/Kenney/Kenney_High_Square.ttf")
    load_font(":system:fonts/ttf/Kenney/Kenney_Mini.ttf")
    load_font(":system:fonts/ttf/Kenney/Kenney_Mini_Square.ttf")
    load_font(":system:fonts/ttf/Kenney/Kenney_Pixel.ttf")
    load_font(":system:fonts/ttf/Kenney/Kenney_Pixel_Square.ttf")
    load_font(":system:fonts/ttf/Kenney/Kenney_Rocket.ttf")
    load_font(":system:fonts/ttf/Kenney/Kenney_Rocket_Square.ttf")


def load_liberation_fonts() -> None:
    """Loads all styles for generic Arial, Courier, and Times New Roman replacements.

    .. tip:: This function is best for prototyping and experimenting!

             For best performance, you may want to switch to
             :py:class:`arcade.load_font` before release.

    The Liberation fonts are proven, permissively-licensed fonts.[
    For previews and additional information, please see
    :ref:`resources-fonts-liberation`.

    .. list-table:: ``font_name`` values for :py:class:`arcade.Text`
       :header-rows: 1

       * - Proprietary Font(s)
         - Liberation Replacemetn

       * - ``"Courier"``
         - ``"Liberation Mono"``

       * - ``"Times New Roman"``, ``"Times"``
         - ``"Liberation Serif"``

       * - ``"Arial"``
         - ``"Liberation Sans"``

    """
    from arcade.text import load_font

    load_font(":system:fonts/ttf/Liberation/Liberation_Mono_BoldItalic.ttf")
    load_font(":system:fonts/ttf/Liberation/Liberation_Mono_Bold.ttf")
    load_font(":system:fonts/ttf/Liberation/Liberation_Mono_Italic.ttf")
    load_font(":system:fonts/ttf/Liberation/Liberation_Mono_Regular.ttf")
    load_font(":system:fonts/ttf/Liberation/Liberation_Sans_BoldItalic.ttf")
    load_font(":system:fonts/ttf/Liberation/Liberation_Sans_Bold.ttf")
    load_font(":system:fonts/ttf/Liberation/Liberation_Sans_Italic.ttf")
    load_font(":system:fonts/ttf/Liberation/Liberation_Sans_Regular.ttf")
    load_font(":system:fonts/ttf/Liberation/Liberation_Serif_BoldItalic.ttf")
    load_font(":system:fonts/ttf/Liberation/Liberation_Serif_Bold.ttf")
    load_font(":system:fonts/ttf/Liberation/Liberation_Serif_Italic.ttf")
    load_font(":system:fonts/ttf/Liberation/Liberation_Serif_Regular.ttf")
