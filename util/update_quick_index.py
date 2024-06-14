"""
Script used to create the quick index
"""
import os
import re
import sys
from functools import wraps

from pathlib import Path
from typing import Any, Callable, TypeVar, Iterable

# Ensure we get funnily named utility modules first in imports
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from vfs import Vfs, SharedPaths

REPO_ROOT = SharedPaths.REPO_ROOT
ARCADE_ROOT = SharedPaths.ARCADE_ROOT
API_DOC_DIR = SharedPaths.API_DOC_ROOT


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

    'drawing_support.py': ['Drawing - Utility', 'drawing_utilities.rst'],
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


def get_member_list(filepath):
    """
    Take a file, and return all the classes, functions, and data declarations in it
    """
    file_pointer = open(filepath, encoding="utf8")
    print("Processing: ", filepath)
    filename = filepath.name

    class_re = re.compile(r"^class ([A-Za-z0-9]+[^\(:]*)")
    function_re = re.compile("^def ([a-z][a-z0-9_]*)")
    type_re = re.compile("^([A-Za-z][A-Za-z0-9_]*) = ")

    class_list = []
    function_list = []
    type_list = []

    for line_no, line in enumerate(file_pointer, start=1):
        try:
            class_names = class_re.findall(line)
            for class_name in class_names:
                class_list.append(class_name)

            function_names = function_re.findall(line)
            for method_name in function_names:
                function_list.append(method_name)

            type_names = type_re.findall(line)
            for type_name in type_names:
                if type_name not in ['LOG']:
                    type_list.append(type_name)

        except Exception as e:
            print(f"Exception processing {filename} on line {line_no}: {e}")
            break

    class_list.sort()
    function_list.sort()
    type_list.sort()
    return type_list, class_list, function_list


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


def process_directory(directory: Path, quick_index_file):
    """
    Take a directory and process all immediate children in it

    This is definitely rushed code. Instead of using inspect, ast, or any
    3rd party module like griffe... it's badly reassembling the module name
    from a collection of tables and unnamed sequences.

    :param directory: A directory to process
    :param quick_index_file: The destination for a file
    """
    # print()
    # print(f"Processing directory {directory}")

    file_list = tuple(directory.glob('*.py'))

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

        type_list, class_list, function_list = get_member_list(path)

        # -- Reconstruct package name --

        package = FILE_MAPPING.get(path.name, None) or DIR_MAPPING.get(directory.name, None)

        # Reconstruct on-disk path for the package name
        path_name = prepend + path.name
        # print(f"    {package=!r}, {path.name=!r}, {path_name=!r}")

        # If it's a known file and we have members
        if path_name in titles and (len(type_list) > 0 or len(class_list) > 0 or len(function_list) > 0):
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
            for rule in CLASS_SPECIAL_RULES.get(full_class_name, []):
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


table_header_arcade = """
.. list-table::
   :widths: 50 50
   :header-rows: 1
   :name: quickapi
   :class: display

   * - Name
     - Group"""


vfs = Vfs()


def main():
    # Delete the API directory files
    vfs.request_culling_unwritten(API_DOC_DIR, '*.rst')

    with vfs.open_ctx(API_DOC_DIR / "quick_index.rst", "w") as text_file:
        text_file.include_file(
            REPO_ROOT /  'util' / 'template_quick_index.rst')

        text_file.write("The arcade module\n")
        text_file.write("-----------------\n\n")

        text_file.write(table_header_arcade)

        process_directory(ARCADE_ROOT, text_file)
        process_directory(ARCADE_ROOT / "types", text_file)
        process_directory(ARCADE_ROOT / "sprite_list", text_file)
        process_directory(ARCADE_ROOT / "geometry", text_file)
        process_directory(ARCADE_ROOT / "sprite", text_file)
        process_directory(ARCADE_ROOT / "texture", text_file)
        process_directory(ARCADE_ROOT / "texture_atlas", text_file)
        # process_directory(ARCADE_ROOT / "gl", text_file)
        process_directory(ARCADE_ROOT / "text", text_file)
        process_directory(ARCADE_ROOT / "gui", text_file)
        process_directory(ARCADE_ROOT / "gui/widgets", text_file)
        process_directory(ARCADE_ROOT / "gui/property", text_file)
        process_directory(ARCADE_ROOT / "gui/experimental", text_file)
        process_directory(ARCADE_ROOT / "tilemap", text_file)

    vfs.write()

    print("Done creating quick_index.rst")


main()
