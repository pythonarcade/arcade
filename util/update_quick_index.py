"""
Script used to create the quick index
"""
from __future__ import annotations

import os
import re
import sys
from collections.abc import Mapping

from pathlib import Path
from textwrap import dedent
from typing import Iterable


# Ensure we get utility & arcade imports first
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from vfs import Vfs, SharedPaths

REPO_ROOT = SharedPaths.REPO_ROOT
ARCADE_ROOT = SharedPaths.ARCADE_ROOT
API_DOC_GENERATION_DIR = SharedPaths.API_DOC_ROOT / "api"
QUICK_INDEX_FILE_PATH = API_DOC_GENERATION_DIR / "quick_index.rst"


API_FILE_TO_TITLE_AND_MODULES = {
    "types.rst": {
        "title": "Types",
        "use_declarations_in": [
            "arcade.types",
            "arcade.types.numbers",
            "arcade.types.vector_like",
            "arcade.types.color",
            "arcade.types.rect"
        ]
    },
    "drawing_primitives.rst": {
        "title": "Drawing - Primitives",
        "use_declarations_in": [
            "arcade.draw_commands"
        ]
    },
    "sprites.rst": {
        "title": "Sprites",
        "use_declarations_in": [
            "arcade.sprite",
            "arcade.sprite.base",
            "arcade.sprite.sprite",
            "arcade.sprite.simple",
            "arcade.sprite.colored",
            "arcade.sprite.mixins",
            "arcade.sprite.animated",
            "arcade.sprite.enums"
        ]
    },
    "sprite_list.rst": {
        "title": "Sprite Lists",
        "use_declarations_in": [
            "arcade.sprite_list",
            "arcade.sprite_list.sprite_list",
            "arcade.sprite_list.spatial_hash",
            "arcade.sprite_list.collision"
        ]
    },
    "text.rst": {
        "title": "Text",
        "use_declarations_in": [
            "arcade.text"
        ]
    },
    "camera_2d.rst": {
        "title": "Camera 2D",
        "use_declarations_in": [
            "arcade.camera.camera_2d"
        ]
    },
    "sprite_scenes.rst": {
        "title": "Sprite Scenes",
        "use_declarations_in": [
            "arcade.scene"
        ]
    },
    "tilemap.rst": {
        "title": "Tiled Map Reader",
        "use_declarations_in": [
            "arcade.tilemap.tilemap"
        ]
    },
    "texture.rst": {
        "title": "Texture Management",
        "use_declarations_in": [
            "arcade.texture",
            "arcade.texture.texture",
            "arcade.texture.loading",
            "arcade.texture.generate",
            "arcade.texture.manager",
            "arcade.texture.spritesheet",
            "arcade.texture.tools"
        ]
    },
    "texture_transforms.rst": {
        "title": "Texture Transforms",
        "use_declarations_in": [
            "arcade.texture.transforms"
        ]
    },
    "texture_atlas.rst": {
        "title": "Texture Atlas",
        "use_declarations_in": [
            "arcade.texture_atlas",
            "arcade.texture_atlas.base",
            "arcade.texture_atlas.atlas_2d"
        ]
    },
    "perf_info.rst": {
        "title": "Performance Information",
        "use_declarations_in": [
            "arcade.perf_info",
            "arcade.perf_graph"
        ]
    },
    "physics_engines.rst": {
        "title": "Physics Engines",
        "use_declarations_in": [
            "arcade.physics_engines",
            "arcade.pymunk_physics_engine"
        ]
    },
    "geometry.rst": {
        "title": "Geometry Support",
        "use_declarations_in": [
            "arcade.geometry"
        ]
    },
    "game_controller.rst": {
        "title": "Game Controller Support",
        "use_declarations_in": [
            "arcade.controller"
        ]
    },
    "joysticks.rst": {
        "title": "Joystick Support",
        "use_declarations_in": [
            "arcade.joysticks"
        ]
    },
    "window.rst": {
        "title": "Window and View",
        "use_declarations_in": [
            "arcade.application",
            "arcade.window_commands",
            "arcade.sections"
        ]
    },
    "sound.rst": {
        "title": "Sound",
        "use_declarations_in": [
            "arcade.sound"
        ]
    },
    "path_finding.rst": {
        "title": "Pathfinding",
        "use_declarations_in": [
            "arcade.paths"
        ]
    },
    "isometric.rst": {
        "title": "Isometric Map Support (incomplete)",
        "use_declarations_in": [
            "arcade.isometric"
        ]
    },
    "easing.rst": {
        "title": "Easing",
        "use_declarations_in": [
            "arcade.easing"
        ]
    },
    "utility.rst": {
        "title": "Misc Utility Functions",
        "use_declarations_in": [
            "arcade",
            "arcade.__main__",
            "arcade.utils"
        ]
    },
    "drawing_batch.rst": {
        "title": "Shape Lists",
        "use_declarations_in": [
            "arcade.shape_list"
        ]
    },
    "open_gl.rst": {
        "title": "OpenGL Context",
        "use_declarations_in": [
            "arcade.context"
        ]
    },
    "math.rst": {
        "title": "Math",
        "use_declarations_in": [
            "arcade.math"
        ]
    },
    "earclip.rst": {
        "title": "Earclip",
        "use_declarations_in": [
            "arcade.earclip"
        ]
    },
    "gui.rst": {
        "title": "GUI",
        "use_declarations_in": [
            "arcade.gui",
            "arcade.gui.constructs",
            "arcade.gui.mixins",
            "arcade.gui.surface",
            "arcade.gui.ui_manager",
            "arcade.gui.nine_patch",
            "arcade.gui.view"
        ]
    },
    "gui_widgets.rst": {
        "title": "GUI Widgets",
        "use_declarations_in": [
            "arcade.gui.widgets",
            "arcade.gui.widgets.buttons",
            "arcade.gui.widgets.dropdown",
            "arcade.gui.widgets.layout",
            "arcade.gui.widgets.slider",
            "arcade.gui.widgets.text",
            "arcade.gui.widgets.toggle",
            "arcade.gui.widgets.image"
        ]
    },
    "gui_events.rst": {
        "title": "GUI Events",
        "use_declarations_in": [
            "arcade.gui.events"
        ]
    },
    "gui_properties.rst": {
        "title": "GUI Properties",
        "use_declarations_in": [
            "arcade.gui.property"
        ]
    },
    "gui_style.rst": {
        "title": "GUI Style",
        "use_declarations_in": [
            "arcade.gui.style"
        ]
    },
    "gui_experimental.rst": {
        "title": "GUI Experimental Features",
        "use_declarations_in": [
            "arcade.gui.experimental.password_input",
            "arcade.gui.experimental.scroll_area"
        ]
    }
}


EMPTY_TUPLE = tuple()


class NotExcludedBy:

    def __init__(self, collection: Iterable):
        self.items = set(collection)

    def __call__(self, item) -> bool:
        return item not in self.items


# Module and class members to exclude
EXCLUDED_MEMBERS = [
    "ImageData",
    "FakeImage",
    "load_atlas",
    "save_atlas",
    "ImageDataRefCounter",
    "UVData",
]
member_not_excluded = NotExcludedBy(EXCLUDED_MEMBERS)


SHOW_INHERITANCE = (':show-inheritance:',)
INHERITED_MEMBERS = (':inherited-members:',)
CLASS_SPECIAL_RULES = {
    "arcade.ArcadeContext" : SHOW_INHERITANCE + INHERITED_MEMBERS
}

# "Parsing" declaration names via regex
DeclarationsDict = dict[str, list[str]]

# Patterns + default config dict
CLASS_RE = re.compile(r"^class ([A-Za-z0-9]+[^\(:]*)")
FUNCTION_RE = re.compile("^def ([a-z][a-z0-9_]*)")
TYPE_RE = re.compile("^(?!LOG =)([A-Za-z][A-Za-z0-9_]*) =")
DEFAULT_EXPRESSIONS =  {
    'class': CLASS_RE,
    'function': FUNCTION_RE,
    # 'type': TYPE_RE
}


def get_file_declarations(
        filepath: Path,
        kind_to_regex: Mapping[str, re.Pattern] = DEFAULT_EXPRESSIONS
) -> DeclarationsDict:
    """Use a mapping of kind names to regex to get declarations.

    The returned dict will have a list for each name in kind_to_regex,
    plus a '*' key which retains all values in their original ordering.

    For module names, see the get_module_declarations function below.

    IMPORTANT: Parsing behavior is still limited to single lines!

    This is intentional. It's an incremental change which focuses on
    being more readable and configurable without adding external
    dependencies. The core behavior hasn't changed much aside form the
    return value being a dict instead of a tuple. Expressions are applied
    in the same order as in kind_to_regex.

    :param filepath: A file path to read.
    :param kind_to_regex: An mapping of kind names to the re.Pattern
        instances used to parse each.
    """

    print("Parsing: ", filepath)
    filename = filepath.name

    # Set up our return value dict
    parsed_values = {'*':[]}
    for kind_name, exp in kind_to_regex.items():
        # print(f"  ...with {group_name} expression {e.pattern!r}")
        parsed_values[kind_name] = []

    try:
        with open(filepath, encoding="utf8") as file_pointer:
            for line_no, line in enumerate(file_pointer, start=1):
                try:
                    for kind, exp in kind_to_regex.items():
                        parsed_raw = exp.findall(line)
                        parsed_values[kind].extend(parsed_raw)
                        parsed_values['*'].extend(parsed_raw)

                except Exception as e:
                    print(f"Exception processing {filename} on line {line_no}: {e}")
                    break
    except Exception as e:
        print(f"Failed to open {filepath}: {e}")

    return parsed_values


_VALID_MODULE_SEGMENT = re.compile(r"[_a-zA-Z][_a-z0-9]*")


def get_module_path(module: str) -> Path:
    """Quick-n-dirty module path estimation relative to the repo root.

    :param module: A module path in the project.
    :raises ValueError: When a can't be computed.
    :return: A
    """
    # Convert module.name.here to module/name/here
    current = REPO_ROOT
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


def generate_api_file(api_file_name: str, vfs: Vfs):
    """
    Take a directory and process all immediate children in it

    This is definitely rushed code. Instead of using inspect, ast, or any
    3rd party module like griffe... it's badly reassembling the module name
    from a collection of tables and unnamed sequences.

    :param api_file_name: The name of the file in the API directory
    :param vfs: The vfs object to use
    """
    page_config = API_FILE_TO_TITLE_AND_MODULES.get(api_file_name, None)

    if not page_config:
        print(f"ERROR: No config defined for API file {api_file_name!r}")
        return

    try:
        full_api_file_name = API_DOC_GENERATION_DIR / api_file_name
        title = page_config.get('title')
        use_declarations_in = page_config.get('use_declarations_in', [])
        print(f"API filename {api_file_name} gets {title=} with {use_declarations_in=}")

    except Exception as e:
        print(f"ERROR: Unintelligible config data for {api_file_name!r}: {e}")
        return

    # Open in "a" mode to append
    quick_index_file = vfs.open(QUICK_INDEX_FILE_PATH, "a")
    quick_index_file.write("\n")

    print(f"Generating API ref file {str(full_api_file_name)!r} titled {title!r}")
    underline = "-" * len(title)

    api_file = vfs.open(full_api_file_name, "w")
    api_file.write(f".. _{api_file_name[:-4]}_api:")
    api_file.write(f"\n\n")
    api_file.write(f"{title}\n")
    api_file.write(f"{underline}\n\n")


    for module_name in use_declarations_in:
        # Did we ever have tests in the path name? What?
        if "test" in module_name:
            print(
                f"WARNING: {module_name!r} appears to contain tests."
                f"Those belong in the 'tests/' directory!")
            continue

        module_path = get_module_path(module_name)
        member_lists = get_file_declarations(module_path)

        # TODO: Figure out how to reliably parse & render types?
        # type_list = member_lists.get('type')
        class_list = member_lists.get('class')
        function_list = member_lists.get('function')

        if not len(member_lists['*']):
            print(
                f"WARNING: No members parsed for {module_name!r} with"
                f" inferred path {module_path!r}. Check & update your"
                f"config?")
            continue

        # Classes
        for item in filter(member_not_excluded, class_list):
            full_class_name = f"{module_name}.{item}"

            quick_index_file.write(f"   * - :py:class:`{full_class_name}`\n")
            quick_index_file.write(f"     - {title}\n")

            # Write the entry to the file
            api_file.write(f".. autoclass:: {full_class_name}\n")
            api_file.write("    :members:\n")
            # api_file.write(f"    :member-order: groupwise\n")

            # Apply special per-class addenda
            for rule in CLASS_SPECIAL_RULES.get(full_class_name, EMPTY_TUPLE):
                api_file.write(f"    {rule}\n")

            api_file.write("\n")

            # print(f"  Class {item}")
            # text_file.write(f"     - Class\n")
            # text_file.write(f"     - {path_name}\n")

        # Functions
        for item in filter(member_not_excluded, function_list):
            full_class_name = f"{module_name}.{item}"
            quick_index_file.write(f"   * - :py:func:`{full_class_name}`\n")
            quick_index_file.write(f"     - {title}\n")

            api_file.write(f".. autofunction:: {full_class_name}\n\n")

            # print(f"  Function {item}")
            # text_file.write(f"     - Func\n")
            # text_file.write(f"     - {path_name}\n")

        api_file.close()


def main():
    vfs = Vfs()

    # Delete the API directory files
    vfs.request_culling_unwritten(API_DOC_GENERATION_DIR, '*.rst')

    # Open in "w" mode to clear
    with vfs.open_ctx(QUICK_INDEX_FILE_PATH, "w") as text_file:
        text_file.include_file(
            REPO_ROOT /  'util' / 'template_quick_index.rst')

        text_file.write("The arcade module\n")
        text_file.write("-----------------\n\n")

        text_file.write(dedent(
            """
            .. list-table::
               :widths: 50 50
               :header-rows: 1
               :name: quickapi
               :class: display

               * - Name
                 - Group
            """
        ))

    for filename in API_FILE_TO_TITLE_AND_MODULES.keys():
        generate_api_file(filename, vfs)

    vfs.write()

    print("Done creating quick_index.rst")


if __name__ == "__main__":
    main()
