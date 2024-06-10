"""
Script used to create the quick index
"""
import os
import re
from pathlib import Path
import sys

from vfs import Vfs

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))

REPO_ROOT = HERE.parent.resolve()
ARCADE_ROOT = REPO_ROOT / "arcade"
API_DOC_DIR = REPO_ROOT / "doc/api_docs/api"


titles = {
    'application.py': ['Window and View', 'window.rst'],
    'shape_list.py': ['Shape Lists', 'drawing_batch.rst'],
    'context.py': ['OpenGL Context', 'open_gl.rst'],
    'draw_commands.py': ['Drawing - Primitives', 'drawing_primitives.rst'],
    'geometry.py': ['Geometry Support', 'geometry.rst'],
    'isometric.py': ['Isometric Map Support (incomplete)', 'isometric.rst'],
    'controller.py': ['Game Controller Support', 'game_controller.rst'],
    'joysticks.py': ['Joystick Support', 'joysticks.rst'],
    'paths.py': ['Pathfinding', 'path_finding.rst'],
    'perf_info.py': ['Performance Information', 'perf_info.rst'],
    'perf_graph.py': ['Performance Information', 'perf_info.rst'],
    'physics_engines.py': ['Physics Engines', 'physics_engines.rst'],
    'pymunk_physics_engine.py': ['Physics Engines', 'physics_engines.rst'],
    'sound.py': ['Sound', 'sound.rst'],
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
    'texture/__init__.py': ['Texture Management', 'texture.rst'],
    'texture/texture.py': ['Texture Management', 'texture.rst'],
    'texture/loading.py': ['Texture Management', 'texture.rst'],
    'texture/generate.py': ['Texture Management', 'texture.rst'],
    'texture/manager.py': ['Texture Management', 'texture.rst'],
    'texture/solid_color.py': ['Texture Management', 'texture.rst'],
    'texture/spritesheet.py': ['Texture Management', 'texture.rst'],
    'texture/tools.py': ['Texture Management', 'texture.rst'],
    'texture/transforms.py': ['Texture Transforms', 'texture_transforms.rst'],
    'camera/camera_2d.py': ['Camera 2D', 'camera_2d.rst'],
    'texture_atlas/__init__.py': ['Texture Atlas', 'texture_atlas.rst'],
    'texture_atlas/base.py': ['Texture Atlas', 'texture_atlas.rst'],
    'texture_atlas/atlas_2d.py': ['Texture Atlas', 'texture_atlas.rst'],
    'math.py': ['Math', 'math.rst'],

    'types/__init__.py': ['Types', 'types.rst'],
    'types/numbers.py': ['Types', 'types.rst'],
    'types/vector_like.py' : ['Types', 'types.rst'],
    'types/color.py': ['Types', 'types.rst'],
    'types/rect.py': ['Types', 'types.rst'],

    'easing.py': ['Easing', 'easing.rst'],
    'earclip.py': ['Earclip', 'earclip.rst'],
    'tilemap/__init__.py': ['Loading TMX (Tiled Map Editor) Maps', 'tiled.rst'],
    'tilemap.py': ['Loading TMX (Tiled Map Editor) Maps', 'tiled.rst'],
    '__init__.py': ['Misc Utility Functions', 'utility.rst'],
    '__main__.py': ['Misc Utility Functions', 'utility.rst'],
    'utils.py': ['Misc Utility Functions', 'utility.rst'],
    'window_commands.py': ['Window and View', 'window.rst'],
    'sections.py': ['Window and View', 'window.rst'],
    'scene.py': ['Sprite Scenes', 'sprite_scenes.rst'],

    'tilemap/tilemap.py': ['Tiled Map Reader', 'tilemap.rst'],

    'gui/__init__.py': ['GUI', 'gui.rst'],
    'gui/constructs.py': ['GUI', 'gui.rst'],
    'gui/events.py': ['GUI Events', 'gui_events.rst'],
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
    'gui/property.py': ['GUI Properties', 'gui_properties.rst'],
    'gui/style.py': ['GUI Style', 'gui_style.rst'],
    'experimental/password_input.py': ['GUI Experimental Features', 'gui_experimental.rst'],
    'experimental/scroll_area.py': ['GUI Experimental Features', 'gui_experimental.rst'],

    'events/__init__.py': ['GUI Utility Functions', 'gui_utility.rst'],
    'gl/buffer.py': ['OpenGL Buffer', 'open_gl.rst'],
    'gl/context.py': ['OpenGL Context', 'open_gl.rst'],
    'gl/enums.py': ['OpenGL Enums', 'open_gl.rst'],
    'gl/exceptions.py': ['OpenGL Exceptions', 'open_gl.rst'],
    'gl/framebuffer.py': ['OpenGL FrameBuffer', 'open_gl.rst'],
    'gl/geometry.py': ['OpenGL Geometry', 'open_gl.rst'],
    'gl/program.py': ['OpenGL Program', 'open_gl.rst'],
    'gl/glsl.py': ['OpenGL GLSL', 'open_gl.rst'],
    'gl/types.py': ['OpenGL Types', 'open_gl.rst'],
    'gl/uniform.py': ['OpenGL Uniform Data', 'open_gl.rst'],
    'gl/utils.py': ['OpenGL Utils', 'open_gl.rst'],
    'gl/query.py': ['OpenGL Query', 'open_gl.rst'],
    'gl/texture.py': ['Texture Management', 'open_gl.rst'],
    'gl/vertex_array.py': ['OpenGL Vertex Array (VAO)', 'open_gl.rst'],
}
excluded_modules = [
    'version.py',
    'texture_atlas/atlas_array.py',
    'texture_atlas/atlas_bindless.py',
    'texture_atlas/helpers.py',
    'experimental/__init__.py' # Ugly fix for experimental gui features
]

# Module and class members to exclude
EXCLUDED_MEMBERS = [
    "ImageData",
    "FakeImage",
    "load_atlas",
    "save_atlas",
    "ImageDataRefCounter",
    "UVData",
]

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

    line_no = 0
    try:
        for line in file_pointer:
            line_no += 1

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

    class_list.sort()
    function_list.sort()
    type_list.sort()
    return type_list, class_list, function_list


def process_directory(directory: Path, quick_index_file):
    """
    Take a directory and process all the files in it.
    """
    # print()
    # print(f"Processing directory {directory}")

    file_list = directory.glob('*.py')

    quick_index_file.write("\n")

    if directory.name == "arcade":
        prepend = ""
    else:
        prepend = directory.name + "/"

    for path in file_list:
        if "test" in path.name:
            continue

        if not path.exists():
            print(f"Error, can't find file: '{path.name}'")
            continue
        # else:
        #     print(f"Processing: {path.name}")

        type_list, class_list, function_list = get_member_list(path)

        # Map directory names to their package
        dir_mapping = {
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
        }
        # Map file names to their package
        file_mapping = {
            "geometry.py": "arcade.geometry",
            "transforms.py": "arcade.texture.transforms",
            "isometric.py": "arcade.isometric",
            "particles": "arcade.particles",
            "utils.py": "arcade.utils",
            "easing.py": "arcade.easing",
            "math.py": "arcade.math",
            "earclip.py": "arcade.earclip",
            "shape_list.py": "arcade.shape_list"
        }
        package = file_mapping.get(path.name, None) or dir_mapping.get(directory.name, None)

        path_name = prepend + path.name
        # print(f"    {package=!r}, {path.name=!r}, {path_name=!r}")

        if path_name in titles and (len(type_list) > 0 or len(class_list) > 0 or len(function_list) > 0):
            title = titles[path_name][0]
            api_file_name = titles[path_name][1]
        elif path_name not in titles and path_name not in excluded_modules:
            title = f"ERR: `{path_name}`"
            api_file_name = "zzz.rst"
            print(f"No title for '{path_name}'.")
        else:
            continue

        full_api_file_name = API_DOC_DIR / api_file_name

        # print(package, title, api_file_name, full_api_file_name)

        new_api_file = not vfs.exists(full_api_file_name)

        api_file = vfs.open(full_api_file_name, "a")

        if new_api_file:
            api_file.write(f".. _{api_file_name[:-4]}_api:")
            api_file.write(f"\n\n")
            api_file.write(f"{title}\n")
            underline = "-" * len(title)
            api_file.write(f"{underline}\n\n")

        # Classes
        if len(class_list) > 0:
            for item in class_list:
                if item in EXCLUDED_MEMBERS:
                    continue
                full_class_name = f"{package}.{item}"
                quick_index_file.write(f"   * - :py:class:`{full_class_name}`\n")
                quick_index_file.write(f"     - {title}\n")

                api_file.write(f".. autoclass:: {full_class_name}\n")
                api_file.write("    :members:\n")
                # api_file.write(f"    :member-order: groupwise\n")

                # Include inherited members
                if full_class_name in ("arcade.ArcadeContext",):
                    api_file.write("    :show-inheritance:\n")
                    api_file.write("    :inherited-members:\n")

                api_file.write("\n")

                # print(f"  Class {item}")
                # text_file.write(f"     - Class\n")
                # text_file.write(f"     - {path_name}\n")

        # Functions
        if len(function_list) > 0:
            for item in function_list:
                if item in EXCLUDED_MEMBERS:
                    continue
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


def clear_api_directory():
    """
    Delete the API files and make new ones
    """
    vfs.delete_glob(str(API_DOC_DIR), '*.rst')

vfs = Vfs()

def main():
    clear_api_directory()

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
