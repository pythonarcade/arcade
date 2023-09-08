"""
Validate the resources module.
* Check that all resources are listed in the __init__.py file
* Check that all resources listed actually exists
"""
import arcade


def get_referenced_resources():
    """
    Find all the resources listed in the __init__.py file.
    """
    resources = []
    for name in dir(arcade.resources):
        member = getattr(arcade.resources, name)
        if isinstance(member, str) and member.startswith(":"):
            resources.append(arcade.resources.resolve(member))
    return resources


def test_resource_listing_exists():
    """
    Find all the resources listed in the __init__.py file and check for their existence.
    """
    paths = get_referenced_resources()
    assert len(paths) > 100, "Not enough resources listed in __init__.py?"
    # This is probably not needed, but the behavior of resolve() might change
    for path in paths:
        assert path.exists(), f"Resource not found: {path}"


def test_resource_listing_is_complete():
    """
    Have the resource listing been updated?
    """
    paths_in_module = set(get_referenced_resources())

    skip_extensions = arcade.resources._resource_list_skip_extensions
    skip_paths = arcade.resources._resource_list_ignore_paths

    paths_in_resources = set()
    # Check that all files in the resources directory are listed
    for path in arcade.resources.RESOURCE_DIR.rglob("*"):
        if path.is_dir():
            continue
        if path.suffix in skip_extensions:
            continue
        if any(str(path).startswith(str(skip_path)) for skip_path in skip_paths):
        # if any(path.is_relative_to(skip_path) for skip_path in skip_paths): # Python 3.9+
            continue
        paths_in_resources.add(path)

    # Temporarily ignore the following files. This is a problem with duplicate variable names
    # created by the make_resources_init.py script and should be resolved in the future.
    # - sounds: These exist in several formats
    paths_in_resources.remove(arcade.resources.RESOURCE_DIR / "assets" / "sounds" / "laser1.mp3")
    paths_in_resources.remove(arcade.resources.RESOURCE_DIR / "assets" / "sounds" / "laser1.ogg")
    paths_in_resources.remove(arcade.resources.RESOURCE_DIR / "assets" / "sounds" / "rockHit2.ogg")
    paths_in_resources.remove(arcade.resources.RESOURCE_DIR / "assets" / "sounds" / "phaseJump1.ogg")
    # - images: These exist in two locations
    paths_in_resources.remove(arcade.resources.RESOURCE_DIR / "assets" / "images" / "items" / "ladderTop.png")
    paths_in_resources.remove(arcade.resources.RESOURCE_DIR / "assets" / "images" / "items" / "ladderMid.png")

    assert paths_in_module - paths_in_resources == set(), "Some resources are not listed in __init__.py"
    assert paths_in_resources - paths_in_module == set(), "Some resources are listed in __init__.py, but not in folder"
