"""
Script used to create the quick index
"""
import re
import os
from pathlib import Path
titles = {
    'arcade_types.py': ['Arcade Data Types', 'arcade_types.rst'],
    'application.py': ['Window and View', 'window.rst'],
    'buffered_draw_commands.py': ['Drawing - Batch', 'drawing_batch.rst'],
    'camera.py': ['Camera', 'camera.rst'],
    'context.py': ['OpenGL Context', 'open_gl.rst'],
    'drawing_support.py': ['Drawing - Utility', 'drawing_utilities.rst'],
    'draw_commands.py': ['Drawing - Primitives', 'drawing_primitives.rst'],
    'earclip_module.py': ['Geometry Support', 'geometry.rst'],
    'emitter.py': ['Particles', 'particle_emitter.rst'],
    'emitter_simple.py': ['Particles', 'particle_emitter.rst'],
    'geometry.py': ['Geometry Support', 'geometry.rst'],
    'geometry_generic.py': ['Geometry Support', 'geometry.rst'],
    'easing.py': ['Geometry Support', 'geometry.rst'],
    'geometry_shapely.py': ['Geometry Support', 'geometry.rst'],
    'hitbox.py': ['Geometry Support', 'geometry.rst'],
    'isometric.py': ['Isometric Map Support (incomplete)', 'isometric.rst'],
    'joysticks.py': ['Game Controller Support', 'game_controller.rst'],
    'particle.py': ['Particles', 'particle_emitter.rst'],
    'paths.py': ['Pathfinding', 'path_finding.rst'],
    'paths_python.py': ['Pathfinding', 'path_finding.rst'],
    'paths_shapely.py': ['Pathfinding', 'path_finding.rst'],
    'perf_info.py': ['Performance Information', 'perf_info.rst'],
    'perf_graph.py': ['Performance Information', 'perf_info.rst'],
    'physics_engines.py': ['Physics Engines', 'physics_engines.rst'],
    'pymunk_physics_engine.py': ['Physics Engines', 'physics_engines.rst'],
    'sound.py': ['Sound', 'sound.rst'],
    'sprite.py': ['Sprites', 'sprites.rst'],
    'sprite_list/__init__.py': ['Sprite Lists', 'sprite_list.rst'],
    'sprite_list/sprite_list.py': ['Sprite Lists', 'sprite_list.rst'],
    'sprite_list/spatial_hash.py': ['Sprite Lists', 'sprite_list.rst'],
    'text.py': ['Text', 'text.rst'],
    'text_pillow.py': ['Text - Image/Pillow based', 'text_image.rst'],
    'text_pyglet.py': ['Text - Pyglet/Glyph based', 'text_pyglet.rst'],
    'texture.py': ['Texture Management', 'texture.rst'],
    'tilemap/__init__.py': ['Loading TMX (Tiled Map Editor) Maps', 'tiled.rst'],
    'tilemap.py': ['Loading TMX (Tiled Map Editor) Maps', 'tiled.rst'],
    '__init__.py': ['Misc Utility Functions', 'utility.rst'],
    '__main__.py': ['Misc Utility Functions', 'utility.rst'],
    'utils.py': ['Misc Utility Functions', 'utility.rst'],
    'version.py': ['Arcade Version Number', 'version.rst'],
    'window_commands.py': ['Window and View', 'window.rst'],
    'sections.py': ['Window and View', 'window.rst'],
    'texture_atlas.py': ['Texture Atlas', 'texture_atlas.rst'],
    'scene.py': ['Sprite Scenes', 'sprite_scenes.rst'],

    'tilemap/tilemap.py': ['Tiled Map Reader', 'tilemap.rst'],

    'gui/__init__.py': ['GUI', 'gui.rst'],
    'gui/_property.py': ['GUI', 'gui.rst'],
    'gui/constructs.py': ['GUI', 'gui.rst'],
    'gui/events.py': ['GUI Events', 'gui_events.rst'],
    'gui/mixins.py': ['GUI', 'gui.rst'],
    'gui/surface.py': ['GUI', 'gui.rst'],
    'gui/ui_manager.py': ['GUI', 'gui.rst'],
    'gui/widgets.py': ['GUI Widgets', 'gui_widgets.rst'],

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



def get_member_list(filepath):
    """
    Take a file, and return all the classes, functions, and data declarations in it
    """
    file_pointer = open(filepath, encoding="utf8")
    filename = filepath.name

    class_re = re.compile("^class ([A-Za-z0-9]+[^\(:]*)")
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


def process_directory(directory, quick_index_file):
    """
    Take a directory and process all the files in it.
    """
    # print()
    # print(f"Processing directory {directory}")

    file_list = directory.glob('*.py')

    quick_index_file.write(f"\n")

    if directory.name == "arcade":
        prepend = ""
    else:
        prepend = directory.name + "/"

    for path in file_list:
        if "test" in path.name:
            continue

        if "math.py" in path.name:
            continue

        if "geometry_python.py" in path.name:
            continue

        if "geometry.py" in path.name:
            continue

        if "paths_python.py" in path.name:
            continue

        if not path.exists():
            print(f"Error, can't find file: '{path.name}'")
            continue
        # else:
        #     print(f"Processing: {path.name}")

        type_list, class_list, function_list = get_member_list(path)

        mapping = {"arcade": "arcade",
                   "sprite_list": "arcade",
                   "text": "arcade",
                   "gui": "arcade.gui",
                   "tilemap": "arcade.tilemap",
                   }
        package = mapping[directory.name]

        path_name = prepend + path.name

        if path_name in titles and (len(type_list) > 0 or len(class_list) > 0 or len(function_list) > 0):

            # Print title
            title = titles[path_name][0]
            api_file_name = titles[path_name][1]
        elif path_name not in titles:
            title = f"ERR: `{path_name}`"
            api_file_name = "zzz.rst"
            print(f"No title for '{path_name}'.")
        else:
            continue

        full_api_file_name = "../doc/api/" + api_file_name

        new_api_file = True
        if os.path.isfile(full_api_file_name):
            new_api_file = False

        api_file = open(full_api_file_name, "a")

        if new_api_file:
            api_file.write(f".. _{api_file_name[:-4]}_api:")
            api_file.write(f"\n\n")
            api_file.write(f"{title}\n")
            underline = "-" * len(title)
            api_file.write(f"{underline}\n\n")

        # Classes
        if len(class_list) > 0:
            for item in class_list:
                full_class_name = f"{package}.{item}"
                quick_index_file.write(f"   * - :py:class:`{full_class_name}`\n")
                quick_index_file.write(f"     - {title}\n")

                api_file.write(f"{full_class_name}\n")
                underline = "^" * len(full_class_name)
                api_file.write(f"{underline}\n\n")

                api_file.write(f".. autoclass:: {full_class_name}\n")
                api_file.write(f"    :members:\n")
                # api_file.write(f"    :member-order: groupwise\n")

                # Include inherited members
                if full_class_name in ("arcade.ArcadeContext",):
                    api_file.write(f"    :show-inheritance:\n")
                    api_file.write(f"    :inherited-members:\n")

                api_file.write("\n")

                if "UIMockup" in full_class_name:
                    print(f"AAAAA {full_api_file_name}")

                # print(f"  Class {item}")
                # text_file.write(f"     - Class\n")
                # text_file.write(f"     - {path_name}\n")

        # Functions
        if len(function_list) > 0:
            for item in function_list:
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
    with open('template_quick_index.rst', 'r') as content_file:
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

table_header_gui = """
.. list-table::
   :widths: 50 50
   :header-rows: 1
   :name: quickapigui
   :class: display

   * - Name
     - Group"""

table_header_tiled = """
.. list-table::
   :widths: 50 50
   :header-rows: 1
   :name: quickapitiled
   :class: display

   * - Name
     - Group"""


def clear_api_directory():
    """
    Delete the API files and make new ones
    """
    directory = Path("../doc/api/")
    file_list = directory.glob('*.rst')
    for file in file_list:
        os.remove(file)


def main():
    clear_api_directory()

    text_file = open("../doc/quick_index.rst", "w")
    include_template(text_file)

    text_file.write(f"The arcade module\n")
    text_file.write(f"-----------------\n\n")

    text_file.write(table_header_arcade)

    process_directory(Path("../arcade"), text_file)
    process_directory(Path("../arcade/sprite_list"), text_file)
    process_directory(Path("../arcade/text"), text_file)

    # text_file.write(f"The ``arcade.gl`` module\n")
    # text_file.write(f"-------------------------\n\n")
    # process_directory(Path("../arcade/gl"), text_file)

    text_file.write(f"\n\n")
    text_file.write(f"The arcade.gui module\n")
    text_file.write(f"---------------------\n\n")

    text_file.write(table_header_gui)

    process_directory(Path("../arcade/gui"), text_file)
    process_directory(Path("../arcade/gui/elements"), text_file)
    process_directory(Path("../arcade/gui/events"), text_file)
    process_directory(Path("../arcade/gui/layouts"), text_file)

    text_file.write(f"\n\n")
    text_file.write(f"The arcade.tilemap module\n")
    text_file.write(f"-------------------------\n\n")

    text_file.write(table_header_tiled)

    process_directory(Path("../arcade/tilemap"), text_file)

    text_file.close()
    print("Done creating quick_index.rst")


main()
