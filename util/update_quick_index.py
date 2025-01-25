"""Generate the API doc and quick index.

It's divided into the following sections:

1. Special rules & excludes
2. Doc structure
3. "Parsing" declaration names via regex
4. API File generation

Each of these sections has heading with the same name, but prefixed with
a # --- so you can skip between them in diffs or your favorite editor
via hotkeys.
"""
from __future__ import annotations

import re
import sys
from collections.abc import Mapping

from pathlib import Path
from textwrap import dedent
from typing import Generator

# Ensure we get utility & Arcade imports first
sys.path.insert(0, str(Path(__file__).parent.resolve()))


from doc_helpers import (
    SharedPaths,
    EMPTY_TUPLE,
    get_module_path,
    NotExcludedBy,
    Vfs,
    build_import_tree,
)


REPO_ROOT = SharedPaths.REPO_ROOT
ARCADE_ROOT = SharedPaths.ARCADE_ROOT
API_DOC_GENERATION_DIR = SharedPaths.API_DOC_ROOT / "api"
QUICK_INDEX_FILE_PATH = SharedPaths.API_DOC_ROOT / "quick_index.rst"
IMPORT_TREE = build_import_tree(ARCADE_ROOT)

# --- 1. Special rules & excludes ---

RULE_SHOW_INHERITANCE = (':show-inheritance:',)
RULE_INHERITED_MEMBERS = (':inherited-members:',)

MEMBER_SPECIAL_RULES = {
    "arcade.ArcadeContext" : RULE_SHOW_INHERITANCE + RULE_INHERITED_MEMBERS
}


# Module and class members to exclude
EXCLUDED_MEMBERS = [
    "load_atlas",
    "save_atlas",
]
# Helper callable which returns a bool. Use it with filter
member_not_excluded = NotExcludedBy(EXCLUDED_MEMBERS)


# --- 2. Doc structure ---

API_FILE_TO_TITLE_AND_MODULES = {
    "types.rst": {
        "title": "Types",
        "use_declarations_in": [
            "arcade.types",
            "arcade.types.numbers",
            "arcade.types.vector_like",
            "arcade.types.color",
            "arcade.types.rect",
            "arcade.types.box"
        ]
    },
    "resources.rst": {
        "title": "Resources",
        "use_declarations_in": [
            "arcade.resources",
        ],
    },
    "drawing_primitives.rst": {
        "title": "Primitives",
        "use_declarations_in": [
            "arcade.draw.arc",
            "arcade.draw.circle",
            "arcade.draw.helpers",
            "arcade.draw.line",
            "arcade.draw.parabola",
            "arcade.draw.point",
            "arcade.draw.polygon",
            "arcade.draw.rect",
            "arcade.draw.triangle",
        ]
    },
    "sprites.rst": {
        "title": "Sprites",
        "use_declarations_in": [
            "arcade.sprite",
            "arcade.sprite.base",
            "arcade.sprite.sprite",
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
    "clock.rst": {
        "title": "Clock",
        "use_declarations_in": [
            "arcade.clock",
        ],
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
    "hitbox.rst": {
        "title": "Hitbox",
        "use_declarations_in": [
            "arcade.hitbox",
            "arcade.hitbox.base",
            "arcade.hitbox.bounding_box",
            "arcade.hitbox.simple",
            "arcade.hitbox.pymunk",
        ],
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
            "arcade.texture_atlas.atlas_default",
            "arcade.texture_atlas.region",
            "arcade.texture_atlas.uv_data",
            "arcade.texture_atlas.ref_counters",
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
        "title": "Game Controller",
        "use_declarations_in": [
            "arcade.controller"
        ]
    },
    "joysticks.rst": {
        "title": "Joystick",
        "use_declarations_in": [
            "arcade.joysticks"
        ]
    },
    "window.rst": {
        "title": "Window and View",
        "use_declarations_in": [
            "arcade.application",
            "arcade.window_commands",
            "arcade.sections",
            "arcade.screenshot",
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
        "title": "Isometric Map (incomplete)",
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
            "arcade.gui.experimental.scroll_area",
            "arcade.gui.experimental.typed_text_input"
        ]
    },
    "advanced_cameras.rst": {
       "title": "Advanced Camera Features",
       "use_declarations_in": [
           "arcade.camera.data_types",
           "arcade.camera.projection_functions",
           "arcade.camera.orthographic",
           "arcade.camera.perspective",
           "arcade.camera.default",
           "arcade.camera.static"
       ]
    },
    "exceptions.rst": {
         "title": "Exceptions",
            "use_declarations_in": [
                "arcade.exceptions"
            ],
    },
    "start_finish_render.rst": {
        "title": "Start/Finish Render",
        "use_declarations_in": [
            "arcade.start_finish_data",
        ],
    },
    "cache.rst": {
        "title": "Cache",
        "use_declarations_in": [
            "arcade.cache",
            "arcade.cache.hit_box",
            "arcade.cache.texture",
            "arcade.cache.image_data",
        ],
    },
    "future.rst": {
       "title": "Future Features",
       "use_declarations_in": [
           "arcade.future.texture_render_target",
           "arcade.future.input.inputs",
           "arcade.future.input.manager",
           "arcade.future.input.input_mapping",
           "arcade.future.input.raw_dicts",
           "arcade.future.background.background_texture",
           "arcade.future.background.background",
           "arcade.future.background.groups",
           "arcade.future.light.lights",
           "arcade.future.video.video_player"
       ]
    },
}


# --- 3. "Parsing" declaration names via regex ---

# Return structure of parsing looks like this
DeclarationsDict = dict[
    str,  # "kind" name or "*"
    list[str]  # A list of member names
]

# Patterns + default config dict
CLASS_RE = re.compile(r"^class ([A-Za-z0-9]+[^\(:]*)")
# Yes, the capital letters in this pattern are intentional. They
# capture type instantiation helpers which act like type init calls
# in the rect, box, and other modules.
FUNCTION_RE = re.compile("^def ([a-zA-Z][a-zA-Z0-9_]*)")
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
    dependencies. The core behavior hasn't changed much aside from the
    return value being a dict with a '*' key instead of a tuple.
    re.Pattern instances are applied in the same order as passed
    in kind_to_regex.

    Args:
        filepath:
            A file path to read.
        kind_to_regex:
            An mapping of kind names to the re.Pattern
            instances used to parse each.
    """

    # print("Parsing: ", filepath)
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



# --- 4. API file generation ---
def generate_api_file(api_file_name: str, vfs: Vfs):
    """
    Take a directory and process all immediate children in it

    This is definitely rushed code. Instead of using inspect, ast, or any
    3rd party module like griffe... it's badly reassembling the module name
    from a collection of tables and unnamed sequences.

    Args:
        api_file_name:
            The name of the file in the API directory
        vfs:
            The vfs object to use
    """
    page_config = API_FILE_TO_TITLE_AND_MODULES.get(api_file_name, None)

    if not page_config:
        print(f"ERROR: No config defined for API file {api_file_name!r}")
        return

    try:
        full_api_file_name = API_DOC_GENERATION_DIR / api_file_name
        title = page_config.get('title')
        use_declarations_in = page_config.get('use_declarations_in', EMPTY_TUPLE)
        # print(f"API filename {api_file_name} gets {title=} with {use_declarations_in=}")

    except Exception as e:
        print(f"ERROR: Unintelligible config data for {api_file_name!r}: {e}")
        return

    # Open in "a" mode to append
    quick_index_file = vfs.open(QUICK_INDEX_FILE_PATH, "a")
    quick_index_file.write("\n")

    # print(f"Generating API ref file {str(full_api_file_name)!r} titled {title!r}")
    underline = "-" * len(title)

    api_file = vfs.open(full_api_file_name, "w")
    api_file.write(f".. _{api_file_name[:-4]}_api:\n")
    # api_file.write(f".. py:module:: arcade\n")
    api_file.write(f".. py:currentmodule:: arcade\n")
    api_file.write(f"\n")
    api_file.write(f"{title}\n")
    api_file.write(f"{underline}\n\n")

    # HACK: Completely override auto-generated module
    #       Use when experimenting with autodoc
    # if api_file_name == "types.rst":
    #     api_file.write(dedent(
    #         """
    #         .. automodule:: arcade.types
    #            :members: RGB, RGBA
    #            :imported-members: RGB, RGBA
    #            :ignore-module-all:
    #            :undoc-members:
    #            :private-members:
    #         """
    #         #    :undoc-members:
    #         #    :imported-members:
    #     ))
    #     api_file.close()
    #     return

    for module_name in use_declarations_in:
        # Did we ever have tests in the path name? What?
        if "test" in module_name:
            print(
                f"WARNING: {module_name!r} appears to contain tests."
                f"Those belong in the 'tests/' directory!")
            continue

        # TODO: Figure out how to reliably parse & render types?
        module_path = get_module_path(module_name)
        member_lists = get_file_declarations(module_path)

        # Skip a file if we got no imports
        if not len(member_lists['*']):
            print(
                f"WARNING: No members parsed for {module_name!r} with"
                f" inferred path {module_path!r}. Check & update your"
                f"config?")
            continue

        def iter_declarations(
                kind: str
        ) -> Generator[tuple[str, str], None, None]:
            kind_list = member_lists[kind]
            for name in filter(member_not_excluded, kind_list):
                yield name, IMPORT_TREE.resolve(f"{module_name}.{name}")

        # Classes
        for name, full_name in iter_declarations('class'):
            quick_index_file.write(f"   * - :py:class:`{full_name}`\n")
            quick_index_file.write(f"     - {title}\n")

            # Write the entry to the file
            api_file.write(f".. autoclass:: {full_name}\n")
            api_file.write(f"   :members:\n")
            # api_file.write(f"    :member-order: groupwise\n")

            # Apply special per-class addenda
            for rule in MEMBER_SPECIAL_RULES.get(full_name, EMPTY_TUPLE):
                api_file.write(f"    {rule}\n")

            api_file.write("\n")

            # print(f"  Class {item}")
            # text_file.write(f"     - Class\n")
            # text_file.write(f"     - {path_name}\n")

        # Functions
        for name, full_name in iter_declarations('function'):
            quick_index_file.write(f"   * - :py:func:`{full_name}`\n")
            quick_index_file.write(f"     - {title}\n")

            api_file.write(f".. autofunction:: {full_name}\n\n")

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

        # text_file.write("The Arcade module\n")
        # text_file.write("-----------------\n\n")

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
