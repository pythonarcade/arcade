"""
Generates arcade/resources/__init__.py by looking for
media types in arcade/resources.
"""
import arcade
from pathlib import Path
from typing import List

IGNORE_MEDIA_TYPES = arcade.resources._resource_list_skip_extensions
IGNORE_PATHS = arcade.resources._resource_list_ignore_paths
RESOURCE_ROOT = Path(__file__).parent.parent / "arcade/resources"


def main() -> None:
    """Creates __init__.py in the arcade/resources directory."""
    ignore_count = 0
    skip_count = 0
    used_variable_names: List[str] = []

    lines = get_module_lines()

    for item in RESOURCE_ROOT.glob('**/*'):
        if item.is_dir():
            continue
        if item.suffix in IGNORE_MEDIA_TYPES:
            skip_count += 1
            # print("Skipping (extension)", item)
            continue
        if is_path_ignored(item):
            ignore_count += 1
            print("Ignoring", item)
            continue

        relative_path = item.relative_to(RESOURCE_ROOT)
        stem = item.stem
        pythonic_stem = pythonic_name(stem)
        prefix = get_prefix(relative_path)
        variable_name = f"{prefix}_{pythonic_stem}"

        if variable_name in used_variable_names:
            print(f"Warning: There is a duplicate resource variable name ({variable_name}).")
        used_variable_names.append(variable_name)

        # Optimize paths for assets and system
        if relative_path.parts[0] == "assets":
            handle = "assets"
            relative_path = relative_path.relative_to("assets")
        elif relative_path.parts[0] == "system":
            handle = "system"
            relative_path = relative_path.relative_to("system")
        else:
            raise ValueError(f"Cannot determine handle for: {relative_path}")

        resource_path = f":{handle}:{relative_path.as_posix()}"

        lines.append(f"{variable_name} = '{resource_path}'")

    with open(RESOURCE_ROOT / "__init__.py", 'w') as f:
        f.write("\n".join(lines))

    print(f"Skipped {skip_count} files.")
    print(f"Ignored {ignore_count} files.")


def get_prefix(path: Path) -> str:
    """Get the python variable prefix for a given path."""
    path_str = path.as_posix()
    if "gui" in path_str:
        return "gui"
    elif "sound" in path_str:
        return "sound"
    elif "image" in path_str:
        return "image"
    elif "tmx_map" in path_str or "tiled_map" in path_str:
        return "map"
    elif "music" in path_str:
        return "music"
    else:
        raise ValueError(f"No prefix configured for: {path}")


def is_path_ignored(path: Path) -> bool:
    """Return True if the path should be ignored."""
    for ignore_path in IGNORE_PATHS:
        if path.is_relative_to(ignore_path):
            return True
    return False


def pythonic_name(name: str) -> str:
    pythonic_name = ""
    for i, c in enumerate(name):
        if i != 0 and c.isalpha() and c == c.upper() and name[i-1].isalpha():
            pythonic_name += "_"
        pythonic_name += c.lower()
    return pythonic_name.replace("-", "_")


def get_module_lines() -> List[str]:
    """Get initial lines of the module up to the resource listing"""
    lines = []
    with open(RESOURCE_ROOT / "__init__.py", 'r') as f:
        content = f.readlines()
        for line in content:
            line = line.rstrip()
            if line.startswith("# RESOURCE LIST"):
                lines.append(line)
                return lines
            lines.append(line)

    raise ValueError("No resource list found in __init__.py")


def test_functions():
    assert pythonic_name("dirtCliffAlt_left") == "dirt_cliff_alt_left"
    assert pythonic_name("playerShip1_orange") == "player_ship1_orange"
    assert pythonic_name("Clicked") == "clicked"
    assert pythonic_name("stone_E") == "stone_e"
    assert pythonic_name("Stone_E_") == "stone_e_"
    assert pythonic_name("Stone1") == "stone1"
    assert pythonic_name("Stone-Blue") == "stone_blue"

    path = Path('/testing/gui/abc')
    assert get_prefix(path) == "gui"
    path = Path('sounds/123')
    assert get_prefix(path) == "sound"


if __name__ == "__main__":
    # test_functions()
    main()
