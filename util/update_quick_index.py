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

# Ensure we get funnily named utility modules first in imports
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from vfs import Vfs, SharedPaths

REPO_ROOT = SharedPaths.REPO_ROOT
ARCADE_ROOT = SharedPaths.ARCADE_ROOT
API_DOC_DIR = SharedPaths.API_DOC_ROOT
QUICK_INDEX_FILE_PATH = API_DOC_DIR / "quick_index.rst"


# Tries to be clever but stops half-way, leaving everything awful.
# Understandable since this was made very early on when the library
# was much smaller.
# arcade gets prepended to anything that isn't currently in the arcade
# source root dir for convenience.
titles = {

    # Core arcade items
    'types/__init__.py': ['Types', 'types.rst'],
    'types/numbers.py': ['Types', 'types.rst'],
    'types/vector_like.py': ['Types', 'types.rst'],
    'types/color.py': ['Types', 'types.rst'],
    'types/rect.py': ['Types', 'types.rst'],

    'draw_commands.py': ['Drawing - Primitives', 'drawing_primitives.rst'],

    # arcade.sprite.* - > Sprites, sprites.rst
    'sprite/__init__.py': ['Sprites', 'sprites.rst'],
    'sprite/base.py': ['Sprites', 'sprites.rst'],
    'sprite/sprite.py': ['Sprites', 'sprites.rst'],
    'sprite/simple.py': ['Sprites', 'sprites.rst'],
    'sprite/colored.py': ['Sprites', 'sprites.rst'],
    'sprite/mixins.py': ['Sprites', 'sprites.rst'],
    'sprite/animated.py': ['Sprites', 'sprites.rst'],
    'sprite/enums.py': ['Sprites', 'sprites.rst'],

    'sprite_list/__init__.py': ['Sprite Lists', 'sprite_list.rst'],
    'sprite_list/sprite_list.py': ['Sprite Lists', 'sprite_list.rst'],
    'sprite_list/spatial_hash.py': ['Sprite Lists', 'sprite_list.rst'],
    'sprite_list/collision.py': ['Sprite Lists', 'sprite_list.rst'],

    'text.py': ['Text', 'text.rst'],
    'camera/camera_2d.py': ['Camera 2D', 'camera_2d.rst'],

    'scene.py': ['Sprite Scenes', 'sprite_scenes.rst'],

    'tilemap/tilemap.py': ['Tiled Map Reader', 'tilemap.rst'],

    'texture/__init__.py': ['Texture Management', 'texture.rst'],
    'texture/texture.py': ['Texture Management', 'texture.rst'],
    'texture/loading.py': ['Texture Management', 'texture.rst'],
    'texture/generate.py': ['Texture Management', 'texture.rst'],
    'texture/manager.py': ['Texture Management', 'texture.rst'],
    'texture/solid_color.py': ['Texture Management', 'texture.rst'],
    'texture/spritesheet.py': ['Texture Management', 'texture.rst'],
    'texture/tools.py': ['Texture Management', 'texture.rst'],

    'texture/transforms.py': ['Texture Transforms', 'texture_transforms.rst'],
    'texture_atlas/__init__.py': ['Texture Atlas', 'texture_atlas.rst'],
    'texture_atlas/base.py': ['Texture Atlas', 'texture_atlas.rst'],
    'texture_atlas/atlas_2d.py': ['Texture Atlas', 'texture_atlas.rst'],

    'perf_info.py': ['Performance Information', 'perf_info.rst'],
    'perf_graph.py': ['Performance Information', 'perf_info.rst'],

    'physics_engines.py': ['Physics Engines', 'physics_engines.rst'],
    'pymunk_physics_engine.py': ['Physics Engines', 'physics_engines.rst'],

    'geometry.py': ['Geometry Support', 'geometry.rst'],
    'controller.py': ['Game Controller Support', 'game_controller.rst'],
    'joysticks.py': ['Joystick Support', 'joysticks.rst'],

    'application.py': ['Window and View', 'window.rst'],
    'sound.py': ['Sound', 'sound.rst'],
    'paths.py': ['Pathfinding', 'path_finding.rst'],
    'isometric.py': ['Isometric Map Support (incomplete)', 'isometric.rst'],
    'easing.py': ['Easing', 'easing.rst'],

    # GL
    "context.py": ['OpenGL Context', 'open_gl.rst'],

    # "OpenGL" / arcade.gl is not generated, but documented manually.
    # Find it at docs/api_docs/gl/*

    # ## Utility

    '__init__.py': ['Misc Utility Functions', 'utility.rst'],
    '__main__.py': ['Misc Utility Functions', 'utility.rst'],

    'shape_list.py': ['Shape Lists', 'drawing_batch.rst'],

    'math.py': ['Math', 'math.rst'],

    'earclip.py': ['Earclip', 'earclip.rst'],
    'tilemap/__init__.py': ['Loading TMX (Tiled Map Editor) Maps', 'tiled.rst'],
    'tilemap.py': ['Loading TMX (Tiled Map Editor) Maps', 'tiled.rst'],

    'utils.py': ['Misc Utility Functions', 'utility.rst'],
    'window_commands.py': ['Window and View', 'window.rst'],
    'sections.py': ['Window and View', 'window.rst'],

    'gui/__init__.py': ['GUI', 'gui.rst'],
    'gui/constructs.py': ['GUI', 'gui.rst'],
    'gui/mixins.py': ['GUI', 'gui.rst'],
    'gui/surface.py': ['GUI', 'gui.rst'],
    'gui/ui_manager.py': ['GUI', 'gui.rst'],
    'gui/nine_patch.py': ['GUI', 'gui.rst'],
    'gui/view.py': ['GUI', 'gui.rst'],

    'widgets/__init__.py': ['GUI Widgets', 'gui_widgets.rst'],
    'widgets/buttons.py': ['GUI Widgets', 'gui_widgets.rst'],
    'widgets/dropdown.py': ['GUI Widgets', 'gui_widgets.rst'],
    'widgets/layout.py': ['GUI Widgets', 'gui_widgets.rst'],
    'widgets/slider.py': ['GUI Widgets', 'gui_widgets.rst'],
    'widgets/text.py': ['GUI Widgets', 'gui_widgets.rst'],
    'widgets/toggle.py': ['GUI Widgets', 'gui_widgets.rst'],
    'widgets/image.py': ['GUI Widgets', 'gui_widgets.rst'],

    'gui/events.py': ['GUI Events', 'gui_events.rst'],
    'gui/property.py': ['GUI Properties', 'gui_properties.rst'],
    'gui/style.py': ['GUI Style', 'gui_style.rst'],

    'events/__init__.py': ['GUI Utility Functions', 'gui_utility.rst'],

    'experimental/password_input.py': ['GUI Experimental Features', 'gui_experimental.rst'],
    'experimental/scroll_area.py': ['GUI Experimental Features', 'gui_experimental.rst'],
}


EMPTY_TUPLE = tuple()


class NotExcludedBy:

    def __init__(self, collection: Iterable):
        self.items = set(collection)

    def __call__(self, item) -> bool:
        return item not in self.items


EXCLUDED_MODULES = [
    'version.py',
    'texture_atlas/atlas_array.py',
    'texture_atlas/atlas_bindless.py',
    'texture_atlas/helpers.py',
    'experimental/__init__.py' # Ugly fix for experimental gui features
]
module_not_excluded = NotExcludedBy(EXCLUDED_MODULES)


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

CLASS_RE = re.compile(r"^class ([A-Za-z0-9]+[^\(:]*)")
FUNCTION_RE = re.compile("^def ([a-z][a-z0-9_]*)")
TYPE_RE = re.compile("^(?!LOG =)([A-Za-z][A-Za-z0-9_]*) =")


def get_member_list(
        filepath: Path,
        member_expressions: Mapping[str, re.Pattern] = {
            'class': CLASS_RE,
            'function': FUNCTION_RE,
            'type': TYPE_RE
        }
) -> dict[str, list[str]]:
    """Use regex to do a quick and dirty parse of a file.

    This is very limited. Don't expect anything fancy. It uses the
    passed mapping of kinds and corresponding expressions to immediate
    module declarations. Expressions are applied on a per-line basis,
    so don't bother with multi-line expressions.

    :param filepath: A path to search.
    :param member_expressions: An mapping of kind names to the
        re.Pattern objects to parse each.
    """

    print("Parsing: ", filepath)
    filename = filepath.name

    # Set up our return value dict
    parsed_values = dict(all=[])
    for kind_name, exp in member_expressions.items():
        # print(f"  ...with {group_name} expression {e.pattern!r}")
        parsed_values[kind_name] = []


    with open(filepath, encoding="utf8") as file_pointer:
        for line_no, line in enumerate(file_pointer, start=1):
            try:
                for kind, exp in member_expressions.items():
                    parsed_raw = exp.findall(line)
                    parsed_values[kind].extend(parsed_raw)

            except Exception as e:
                print(f"Exception processing {filename} on line {line_no}: {e}")
                break

    return parsed_values


# Map dirs to their effective display package file
DIR_MAPPING = {
    "arcade": "arcade",
    "sprite": "arcade",
    "texture": "arcade",
    "texture_atlas": "arcade.texture_atlas",
    "sprite_list": "arcade",
    "text": "arcade",
    "gui": "arcade.gui",
    "experimental": "arcade.gui.experimental",
    "property": "arcade.gui.property",
    "widgets": "arcade.gui",
    "tilemap": "arcade.tilemap",
    "camera": "arcade.camera",
    "types": "arcade.types",
    "particles": "arcade.particles",
}

# Map file names to their package
FILE_MAPPING = {
    "geometry.py": "arcade.geometry",
    "transforms.py": "arcade.texture.transforms",
    "isometric.py": "arcade.isometric",
    "utils.py": "arcade.utils",
    "easing.py": "arcade.easing",
    "math.py": "arcade.math",
    "earclip.py": "arcade.earclip",
    "shape_list.py": "arcade.shape_list"
}


def process_directory(directory: Path, vfs: Vfs):
    """
    Take a directory and process all immediate children in it

    This is definitely rushed code. Instead of using inspect, ast, or any
    3rd party module like griffe... it's badly reassembling the module name
    from a collection of tables and unnamed sequences.

    :param directory: A directory to process
    :param vfs: The vfs object to use
    """
    # print()
    # print(f"Processing directory {directory}")

    file_list = tuple(directory.glob('*.py'))

    # Open in "a" mode to append
    quick_index_file = vfs.open(QUICK_INDEX_FILE_PATH, "a")

    print("Processing directory: ", f"{directory=}", f"{quick_index_file=}")
    for dir_member in  file_list:
        print(f"  {dir_member}")

    quick_index_file.write("\n")

    # Part of reassembling a full file path for the table above
    if directory.name == "arcade":
        prepend = ""
    else:
        prepend = directory.name + "/"

    for path in file_list:
        # Did we ever have tests in the path name? What?
        if "test" in path.name:
            continue

        if not path.exists():
            print(f"Error, can't find file: '{path.name}'")
            continue
        # else:
        #     print(f"Processing: {path.name}")

        member_lists = get_member_list(path)
        # type_list, class_list, function_list = member_lists
        type_list = member_lists.get('type')
        class_list = member_lists.get('class')
        function_list = member_lists.get('function')

        file_has_members = bool(sum(map(
            len, member_lists.values())))

        # -- Reconstruct package name --

        package = FILE_MAPPING.get(path.name, None) or DIR_MAPPING.get(directory.name, None)

        # Reconstruct on-disk path for the package name
        path_name = prepend + path.name
        # print(f"    {package=!r}, {path.name=!r}, {path_name=!r}")

        # If it's a known file and we have members
        if path_name in titles and file_has_members:
            title, api_file_name = titles[path_name]

        # If it's not a known file (this is would be gone if we invert structuring)
        elif path_name not in titles and path_name not in EXCLUDED_MODULES:
            title = f"ERR: `{path_name}`"
            api_file_name = "zzz.rst"
            print(f"No title for '{path_name}'.")
        else:
            # Could be an early return?
            continue

        # Where will this API file go, and is it new?
        full_api_file_name = API_DOC_DIR / api_file_name
        new_api_file = not vfs.exists(full_api_file_name)
        # print(package, title, api_file_name, full_api_file_name)

        # Start writing it
        api_file = vfs.open(full_api_file_name, "a")

        # Write the title if it's a new file
        if new_api_file:
            api_file.write(f".. _{api_file_name[:-4]}_api:")
            api_file.write(f"\n\n")
            api_file.write(f"{title}\n")
            underline = "-" * len(title)
            api_file.write(f"{underline}\n\n")

        # Classes
        for item in filter(member_not_excluded, class_list):
            full_class_name = f"{package}.{item}"

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
            full_class_name = f"{package}.{item}"
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
    vfs.request_culling_unwritten(API_DOC_DIR, '*.rst')

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

    process_directory(ARCADE_ROOT, vfs)
    process_directory(ARCADE_ROOT / "types", vfs)
    process_directory(ARCADE_ROOT / "sprite_list", vfs)
    process_directory(ARCADE_ROOT / "geometry", vfs)
    process_directory(ARCADE_ROOT / "sprite", vfs)
    process_directory(ARCADE_ROOT / "texture", vfs)
    process_directory(ARCADE_ROOT / "texture_atlas", vfs)
    # process_directory(ARCADE_ROOT / "gl", vfs)
    process_directory(ARCADE_ROOT / "text", vfs)
    process_directory(ARCADE_ROOT / "gui", vfs)
    process_directory(ARCADE_ROOT / "gui/widgets", vfs)
    process_directory(ARCADE_ROOT / "gui/property", vfs)
    process_directory(ARCADE_ROOT / "gui/experimental", vfs)
    process_directory(ARCADE_ROOT / "tilemap", vfs)

    vfs.write()

    print("Done creating quick_index.rst")


if __name__ == "__main__":
    main()
