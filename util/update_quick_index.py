"""
Script used to create the quick index
"""
import os
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.resolve()))
from vfs import Vfs

# The project root
ROOT = Path(__file__).parent.parent.resolve()

titles = {
    'application.py': ['Window and View', 'window.rst'],
    'shape_list.py': ['Shape Lists', 'drawing_batch.rst'],
    'camera.py': ['Camera', 'camera.rst'],
    'context.py': ['OpenGL Context', 'open_gl.rst'],
    'drawing_support.py': ['Drawing - Utility', 'drawing_utilities.rst'],
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
    'texture/solid_color.py': ['Texture Management', 'texture.rst'],
    'texture/tools.py': ['Texture Management', 'texture.rst'],
    'texture/transforms.py': ['Texture Transforms', 'texture_transforms.rst'],
    'math.py': ['Math', 'math.rst'],
    'types.py': ['Types', 'types.rst'],
    'easing.py': ['Easing', 'easing.rst'],
    'earclip.py': ['Earclip', 'earclip.rst'],
    'tilemap/__init__.py': ['Loading TMX (Tiled Map Editor) Maps', 'tiled.rst'],
    'tilemap.py': ['Loading TMX (Tiled Map Editor) Maps', 'tiled.rst'],
    '__init__.py': ['Misc Utility Functions', 'utility.rst'],
    '__main__.py': ['Misc Utility Functions', 'utility.rst'],
    'utils.py': ['Misc Utility Functions', 'utility.rst'],
    'window_commands.py': ['Window and View', 'window.rst'],
    'sections.py': ['Window and View', 'window.rst'],
    'texture_atlas/__init__.py': ['Texture Atlas', 'texture_atlas.rst'],
    'texture_atlas/base.py': ['Texture Atlas', 'texture_atlas.rst'],
    'texture_atlas/helpers.py': ['Texture Atlas', 'texture_atlas.rst'],
    'scene.py': ['Sprite Scenes', 'sprite_scenes.rst'],

    'tilemap/tilemap.py': ['Tiled Map Reader', 'tilemap.rst'],

    'gui/__init__.py': ['GUI', 'gui.rst'],
    'gui/constructs.py': ['GUI', 'gui.rst'],
    'gui/events.py': ['GUI Events', 'gui_events.rst'],
    'gui/mixins.py': ['GUI', 'gui.rst'],
    'gui/surface.py': ['GUI', 'gui.rst'],
    'gui/ui_manager.py': ['GUI', 'gui.rst'],
    'gui/nine_patch.py': ['GUI', 'gui.rst'],
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
    'version.py'
]

# Module and class members to exclude
EXCLUDED_MEMBERS = [
    "ImageData",
    "AtlasRegion",
    "ImageDataRefCounter",
    "FakeImage",
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

        mapping = {
            "arcade": "arcade",
            "sprite": "arcade",
            "texture": "arcade",
            "texture_atlas": "arcade",
            "sprite_list": "arcade",
            "text": "arcade",
            "gui": "arcade.gui",
            "property": "arcade.gui.property",
            "widgets": "arcade.gui",
            "tilemap": "arcade.tilemap",
            "geometry.py": "arcade.geometry",
            "transforms.py": "arcade.texture.transforms",
            "isometric.py": "arcade.isometric",
            "particles": "arcade.particles",
            "types.py": "arcade.types",
            "utils.py": "arcade.utils",
            "easing.py": "arcade.easing",
            "math.py": "arcade.math",
            "earclip.py": "arcade.earclip",
            "shape_list.py": "arcade.shape_list",
        }
        package = mapping.get(path.name, None) or mapping.get(directory.name, None)

        path_name = prepend + path.name

        if path_name in titles and (len(type_list) > 0 or len(class_list) > 0 or len(function_list) > 0):
            title = titles[path_name][0]
            api_file_name = titles[path_name][1]
        elif path_name not in titles and path_name not in excluded_modules:
            title = f"ERR: `{path_name}`"
            api_file_name = "zzz.rst"
            print(f"No title for '{path_name}'.")
        else:
            continue

        full_api_file_name = ROOT / "doc/api_docs/api/" / api_file_name

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

                api_file.write(f"{full_class_name}\n")
                underline = "^" * len(full_class_name)
                api_file.write(f"{underline}\n\n")

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

                api_file.write(f"{full_class_name}\n")
                underline = "^" * len(full_class_name)
                api_file.write(f"{underline}\n\n")

                api_file.write(f".. autofunction:: {full_class_name}\n\n")

                # print(f"  Function {item}")
                # text_file.write(f"     - Func\n")
                # text_file.write(f"     - {path_name}\n")

        api_file.close()


def include_template(text_file):
    with open(ROOT / 'util' / 'template_quick_index.rst', 'r') as content_file:
        quick_index_content = content_file.read()

    text_file.write(quick_index_content)


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
    directory = ROOT / "doc/api_docs/api"
    vfs.delete_glob(str(directory), '*.rst')

vfs = Vfs()

def main():
    clear_api_directory()

    text_file = vfs.open(ROOT / "doc/api_docs/api/quick_index.rst", "w")
    include_template(text_file)

    text_file.write("The arcade module\n")
    text_file.write("-----------------\n\n")

    text_file.write(table_header_arcade)

    process_directory(ROOT / "arcade", text_file)
    process_directory(ROOT / "arcade/sprite_list", text_file)
    process_directory(ROOT / "arcade/geometry", text_file)
    process_directory(ROOT / "arcade/sprite", text_file)
    process_directory(ROOT / "arcade/texture", text_file)
    process_directory(ROOT / "arcade/texture_atlas", text_file)
    process_directory(ROOT / "arcade/text", text_file)
    # process_directory(Path("../arcade/gl"), text_file)
    process_directory(ROOT / "arcade/gui", text_file)
    process_directory(ROOT / "arcade/gui/widgets", text_file)
    process_directory(ROOT / "arcade/gui/property", text_file)
    process_directory(ROOT / "arcade/tilemap", text_file)

    text_file.close()

    vfs.write()

    print("Done creating quick_index.rst")


main()
