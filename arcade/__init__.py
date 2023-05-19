"""
The Arcade Library

A Python simple, easy to use module for creating 2D games.
"""
# flake8: noqa: E402

# Error out if we import Arcade with an incompatible version of Python.
import sys
import os
from typing import Optional

from pathlib import Path

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 7):
    sys.exit("The Arcade Library requires Python 3.7 or higher.")


def configure_logging(level: Optional[int] = None):
    """Set up basic logging.
    :param int level: The log level. Defaults to DEBUG.
    """
    import logging
    level = level or logging.DEBUG
    LOG = logging.getLogger(__name__)
    # Do not add a new handler if we already have one
    if not LOG.handlers:
        LOG.propagate = False
        LOG.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter('%(relativeCreated)s %(name)s %(levelname)s - %(message)s'))
        LOG.addHandler(ch)

# The following is used to load ffmpeg libraries.
# Currently Arcade is only shipping binaries for Mac OS
# as ffmpeg is not needed for support on Windows and Linux.
# However it is setup to load ffmpeg if the binaries are present
# on Windows and Linux. So if you need ffmpeg you can simply
# drop the binaries in the "lib" folder of Arcade
lib_location = Path(__file__).parent.absolute()
lib_location = lib_location / "lib"

if sys.platform == "darwin" or sys.platform.startswith("linux"):
    if "LD_LIBRARY_PATH" in os.environ:
        os.environ["LD_LIBRARY_PATH"] += ":" + str(lib_location)
    else:
        os.environ["LD_LIBRARY_PATH"] = str(lib_location)
else:
    os.environ["PATH"] += str(lib_location)

# noinspection PyPep8
import pyglet

# Env variable shortcut for headless mode
if os.environ.get('ARCADE_HEADLESS'):
    pyglet.options["headless"] = True

from arcade import utils

# Disable shadow window on macs and in headless mode.
if sys.platform == "darwin" or os.environ.get('ARCADE_HEADLESS') or utils.is_raspberry_pi():
    pyglet.options['shadow_window'] = False

# Use the old gdi fonts on windows until directwrite is fast/stable
# pyglet.options['win32_gdi_font'] = True

# Imports from modules that don't do anything circular
from .drawing_support import get_points_for_thick_line

# Complex imports with potential circularity
from .window_commands import close_window
from .window_commands import exit
from .window_commands import finish_render
from .window_commands import get_display_size
from .window_commands import get_window
from .window_commands import pause
from .window_commands import schedule
from .window_commands import run
from .window_commands import set_background_color
from .window_commands import set_viewport
from .window_commands import set_window
from .window_commands import start_render
from .window_commands import unschedule
from .window_commands import schedule_once

from .camera import SimpleCamera, Camera
from .sections import Section, SectionManager

from .application import MOUSE_BUTTON_LEFT
from .application import MOUSE_BUTTON_MIDDLE
from .application import MOUSE_BUTTON_RIGHT
from .application import NoOpenGLException
from .application import View
from .application import Window
from .application import get_screens
from .application import open_window

from .texture import Texture
from .texture import load_spritesheet
from .texture import load_texture
from .texture import load_texture_pair
from .texture import load_textures
from .texture import make_circle_texture
from .texture import make_soft_circle_texture
from .texture import make_soft_square_texture
from .texture import cleanup_texture_cache
from .texture import get_default_image
from .texture import get_default_texture

from .draw_commands import draw_arc_filled
from .draw_commands import draw_arc_outline
from .draw_commands import draw_circle_filled
from .draw_commands import draw_circle_outline
from .draw_commands import draw_ellipse_filled
from .draw_commands import draw_ellipse_outline
from .draw_commands import draw_line
from .draw_commands import draw_line_strip
from .draw_commands import draw_lines
from .draw_commands import draw_lrtb_rectangle_filled
from .draw_commands import draw_lrbt_rectangle_filled
from .draw_commands import draw_lrtb_rectangle_outline
from .draw_commands import draw_lrbt_rectangle_outline
from .draw_commands import draw_lrwh_rectangle_textured
from .draw_commands import draw_parabola_filled
from .draw_commands import draw_parabola_outline
from .draw_commands import draw_point
from .draw_commands import draw_points
from .draw_commands import draw_polygon_filled
from .draw_commands import draw_polygon_outline
from .draw_commands import draw_rectangle_filled
from .draw_commands import draw_rectangle_outline
from .draw_commands import draw_scaled_texture_rectangle
from .draw_commands import draw_texture_rectangle
from .draw_commands import draw_triangle_filled
from .draw_commands import draw_triangle_outline
from .draw_commands import draw_xywh_rectangle_filled
from .draw_commands import draw_xywh_rectangle_outline
from .draw_commands import get_image
from .draw_commands import get_pixel

# We don't have joysticks game controllers in headless mode
if not pyglet.options["headless"]:
    from .joysticks import get_game_controllers
    from .joysticks import get_joysticks
    from .controller import ControllerManager
    from .controller import get_controllers

from .sound import Sound
from .sound import load_sound
from .sound import play_sound
from .sound import stop_sound

from .sprite import FACE_DOWN
from .sprite import FACE_LEFT
from .sprite import FACE_RIGHT
from .sprite import FACE_UP
from .sprite import AnimatedTimeBasedSprite
from .sprite import load_animated_gif
from .sprite import AnimatedWalkingSprite
from .sprite import AnimationKeyframe
from .sprite import PyMunk
from .sprite import PymunkMixin
from .sprite import SpriteType
from .sprite import Sprite
from .sprite import BasicSprite
# from .sprite import SimpleSprite
from .sprite import SpriteCircle
from .sprite import SpriteSolidColor

from .sprite_list import SpriteList
from .sprite_list import check_for_collision
from .sprite_list import check_for_collision_with_list
from .sprite_list import check_for_collision_with_lists
from .sprite_list import get_closest_sprite
from .sprite_list import get_sprites_at_exact_point
from .sprite_list import get_sprites_at_point
from .sprite_list import get_distance_between_sprites
from .sprite_list import get_sprites_in_rect

from .sprite_list import SpatialHash

from .scene import Scene

from .physics_engines import PhysicsEnginePlatformer
from .physics_engines import PhysicsEngineSimple

from .tilemap import load_tilemap
from .tilemap import read_tmx
from .tilemap import TileMap

from .pymunk_physics_engine import PymunkPhysicsEngine
from .pymunk_physics_engine import PymunkPhysicsObject
from .pymunk_physics_engine import PymunkException

from .version import VERSION

from .paths import has_line_of_sight
from .paths import AStarBarrierList
from .paths import astar_calculate_path

from .context import ArcadeContext

from .texture_atlas import TextureAtlas
from .texture_atlas import load_atlas
from .texture_atlas import save_atlas

from .perf_info import enable_timings
from .perf_info import print_timings
from .perf_info import get_fps
from .perf_info import get_timings
from .perf_info import clear_timings
from .perf_info import timings_enabled
from .perf_info import disable_timings

from .perf_graph import PerfGraph

# Module imports
from arcade import color as color
from arcade import csscolor as csscolor
from arcade import key as key
from arcade import resources as resources
from arcade import types as types
from arcade import math as math
from arcade import shape_list as shape_list
from arcade import hitbox as hitbox
from arcade import experimental as experimental

from .text import (
    draw_text,
    load_font,
    create_text_sprite,
    Text,
)

__all__ = [
    'AStarBarrierList',
    'AnimatedTimeBasedSprite',
    'AnimatedWalkingSprite',
    'AnimationKeyframe',
    'ArcadeContext',
    'Camera',
    'SimpleCamera',
    'ControllerManager',
    'FACE_DOWN',
    'FACE_LEFT',
    'FACE_RIGHT',
    'FACE_UP',
    'MOUSE_BUTTON_LEFT',
    'MOUSE_BUTTON_MIDDLE',
    'MOUSE_BUTTON_RIGHT',
    'NoOpenGLException',
    'PerfGraph',
    'PhysicsEnginePlatformer',
    'PhysicsEngineSimple',
    'PyMunk',
    'PymunkException',
    'PymunkPhysicsEngine',
    'PymunkPhysicsObject',
    'Section',
    'SectionManager',
    'Scene',
    'Sound',
    'BasicSprite',
    'Sprite',
    'SpriteType',
    'PymunkMixin',
    'SpriteCircle',
    'SpriteList',
    'SpriteSolidColor',
    'Text',
    'Texture',
    'TextureAtlas',
    'load_atlas',
    'save_atlas',
    'TileMap',
    'VERSION',
    'View',
    'Window',
    'astar_calculate_path',
    'check_for_collision',
    'check_for_collision_with_list',
    'check_for_collision_with_lists',
    'close_window',
    'disable_timings',
    'draw_arc_filled',
    'draw_arc_outline',
    'draw_circle_filled',
    'draw_circle_outline',
    'draw_ellipse_filled',
    'draw_ellipse_outline',
    'draw_line',
    'draw_line_strip',
    'draw_lines',
    'draw_lrtb_rectangle_filled',
    'draw_lrbt_rectangle_filled',
    'draw_lrtb_rectangle_outline',
    'draw_lrbt_rectangle_outline',
    'draw_lrwh_rectangle_textured',
    'draw_parabola_filled',
    'draw_parabola_outline',
    'draw_point',
    'draw_points',
    'draw_polygon_filled',
    'draw_polygon_outline',
    'draw_rectangle_filled',
    'draw_rectangle_outline',
    'draw_scaled_texture_rectangle',
    'draw_text',
    'draw_texture_rectangle',
    'draw_triangle_filled',
    'draw_triangle_outline',
    'draw_xywh_rectangle_filled',
    'draw_xywh_rectangle_outline',
    'enable_timings',
    'exit',
    'finish_render',
    'get_closest_sprite',
    'get_display_size',
    'get_distance_between_sprites',
    'get_sprites_in_rect',
    'get_controllers',
    'get_game_controllers',
    'get_image',
    'get_joysticks',
    'get_pixel',
    'get_points_for_thick_line',
    'get_screens',
    'get_sprites_at_exact_point',
    'get_sprites_at_point',
    'SpatialHash',
    'get_timings',
    'create_text_sprite',
    'clear_timings',
    'get_window',
    'get_fps',
    'has_line_of_sight',
    'load_animated_gif',
    'load_font',
    'load_sound',
    'load_spritesheet',
    'load_texture',
    'load_texture_pair',
    'load_textures',
    'make_circle_texture',
    'make_soft_circle_texture',
    'make_soft_square_texture',
    'open_window',
    'pause',
    'print_timings',
    'play_sound',
    'read_tmx',
    'load_tilemap',
    'run',
    'schedule',
    'set_background_color',
    'set_viewport',
    'set_window',
    'start_render',
    'stop_sound',
    'timings_enabled',
    'unschedule',
    'schedule_once',
    'cleanup_texture_cache',
    'get_default_texture',
    'get_default_image',
    'hitbox',
    'experimental',
    'color',
    'csscolor',
    'key',
    'resources',
    'types',
    'math',
    'shape_list',
]

__version__ = VERSION

# Piggyback on pyglet's doc run detection
if not getattr(sys, 'is_pyglet_doc_run', False):
    # Auto load fonts
    load_font(":system:fonts/ttf/Kenney_Blocks.ttf")
    load_font(":system:fonts/ttf/Kenney_Future.ttf")
    load_font(":system:fonts/ttf/Kenney_Future_Narrow.ttf")
    load_font(":system:fonts/ttf/Kenney_High.ttf")
    load_font(":system:fonts/ttf/Kenney_High_Square.ttf")
    load_font(":system:fonts/ttf/Kenney_Mini.ttf")
    load_font(":system:fonts/ttf/Kenney_Mini_Square.ttf")
    load_font(":system:fonts/ttf/Kenney_Pixel.ttf")
    load_font(":system:fonts/ttf/Kenney_Pixel_Square.ttf")
    load_font(":system:fonts/ttf/Kenney_Rocket.ttf")
    load_font(":system:fonts/ttf/Kenney_Rocket_Square.ttf")

    # Load additional game controller mappings to Pyglet
    if not pyglet.options['headless']:
        try:
            import pyglet.input.controller
            mappings_file = resources.resolve(":system:gamecontrollerdb.txt")
            pyglet.input.controller.add_mappings_from_file(mappings_file)
        except AssertionError:
            pass
