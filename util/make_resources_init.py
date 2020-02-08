"""
Getting duplicate name errors:

Warning: There is a duplicate resource variable name (image_ladder_mid).
Warning: There is a duplicate resource variable name (image_ladder_top).
Warning: There is a duplicate resource variable name (sound_laser1).
Warning: There is a duplicate resource variable name (sound_laser1).
Warning: There is a duplicate resource variable name (sound_phase_jump1).
Warning: There is a duplicate resource variable name (sound_rock_hit2).
"""

import pathlib
from typing import List


def main() -> None:
    """Creates __init__.py in the arcade/resources directory."""
    media_types = ['.png', '.wav', '.tmx', '.tsx', '.wav', '.mp3', '.ogg']
    parent = pathlib.Path(__file__).parent.parent / "arcade/resources"

    used_variable_names: List[str] = []

    with open(parent.as_posix() + "/__init__.py", 'w') as f:
        for item in parent.glob('**/*'):
            if item.suffix in media_types:

                relative_path = item.relative_to(parent)
                stem = item.stem
                pythonic_stem = make_camel_case_pythonic(stem)

                prefix = get_prefix(relative_path)

                variable_name = f"{prefix}_{pythonic_stem}"

                if variable_name in used_variable_names:
                    print(f"Warning: There is a duplicate resource variable name ({variable_name}).")
                used_variable_names.append(variable_name)

                resource_path = ":resources:/" + relative_path.as_posix()

                f.write(f"{variable_name} = '{resource_path}'\n")


def get_prefix(path: pathlib.Path) -> str:
    path_str = path.as_posix()
    if "gui" in path_str:
        return "gui"
    elif "sound" in path_str:
        return "sound"
    elif "image" in path_str:
        return "image"
    elif "tmx_map" in path_str:
        return "map"
    return ""


def make_camel_case_pythonic(name: str) -> str:
    pythonic_name = ""
    for i, c in enumerate(name):
        if i != 0 and c.isalpha() and c == c.upper() and name[i-1] != "_":
            pythonic_name += "_"
        pythonic_name += c.lower()
    return pythonic_name


def test_functions():
    assert make_camel_case_pythonic("dirtCliffAlt_left") == "dirt_cliff_alt_left"
    assert make_camel_case_pythonic("playerShip1_orange") == "player_ship1_orange"
    assert make_camel_case_pythonic("Clicked") == "clicked"
    assert make_camel_case_pythonic("stone_E") == "stone_e"
    assert make_camel_case_pythonic("Stone_E_") == "stone_e_"
    assert make_camel_case_pythonic("Stone1") == "stone1"

    path = pathlib.Path('/testing/gui/abc')
    assert get_prefix(path) == "gui"
    path = pathlib.Path('sounds/123')
    assert get_prefix(path) == "sound"


if __name__ == "__main__":
    # test_functions()
    main()
