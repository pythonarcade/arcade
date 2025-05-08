"""
The Arcade Library

A Python simple, easy to use module for creating 2D games.
"""

# flake8: noqa: E402
# Error out if we import Arcade with an incompatible version of Python.
import sys
import os
from typing import Final

from pathlib import Path

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 10):
    sys.exit("The Arcade Library requires Python 3.10 or higher.")


def configure_logging(level: int | None = None):
    """Set up basic logging.

    Args:
        level: The log level. Defaults to DEBUG.
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
        ch.setFormatter(
            logging.Formatter("%(relativeCreated)s %(name)s %(levelname)s - %(message)s")
        )
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

import pyglet

# Enable HiDPI support using stretch mode
if os.environ.get("ARCADE_TEST"):
    pyglet.options.dpi_scaling = "real"
else:
    pyglet.options.dpi_scaling = "stretch"

# Env variable shortcut for headless mode
headless: Final[bool] = bool(os.environ.get("ARCADE_HEADLESS"))
if headless:
    pyglet.options.headless = headless


# from arcade import utils
# Disable shadow window on macs and in headless mode.
# if sys.platform == "darwin" or os.environ.get("ARCADE_HEADLESS") or utils.is_raspberry_pi():
# NOTE: We always disable shadow window now to have consistent behavior across platforms.
pyglet.options.shadow_window = False

# Imports from modules that don't do anything circular

# Complex imports with potential circularity
from .window_commands import close_window
from .window_commands import exit
from .window_commands import finish_render
from .window_commands import get_display_size
from .window_commands import get_window
from .window_commands import schedule
from .window_commands import run
from .window_commands import set_background_color
from .window_commands import set_window
from .window_commands import start_render
from .window_commands import unschedule
from .window_commands import schedule_once

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
from .texture import TextureCacheManager
from .texture import SpriteSheet
from .texture import load_spritesheet
from .texture import load_texture
from .texture import load_image
from .texture import make_circle_texture
from .texture import make_soft_circle_texture
from .texture import make_soft_square_texture
from .texture import get_default_image
from .texture import get_default_texture

from .draw import get_points_for_thick_line
from .draw import draw_arc_filled
from .draw import draw_arc_outline
from .draw import draw_circle_filled
from .draw import draw_circle_outline
from .draw import draw_ellipse_filled
from .draw import draw_ellipse_outline
from .draw import draw_line
from .draw import draw_line_strip
from .draw import draw_lines
from .draw import draw_lrbt_rectangle_filled
from .draw import draw_lrbt_rectangle_outline
from .draw import draw_parabola_filled
from .draw import draw_parabola_outline
from .draw import draw_point
from .draw import draw_points
from .draw import draw_polygon_filled
from .draw import draw_polygon_outline
from .draw import draw_rect_filled
from .draw import draw_rect_outline
from .draw import draw_texture_rect
from .draw import draw_sprite
from .draw import draw_sprite_rect
from .draw import draw_triangle_filled
from .draw import draw_triangle_outline
from .draw import draw_lbwh_rectangle_filled
from .draw import draw_lbwh_rectangle_outline
from .screenshot import get_image
from .screenshot import get_pixel

# We don't have joysticks game controllers in headless mode
if not headless:
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
from .sprite import TextureAnimationSprite
from .sprite import load_animated_gif
from .sprite import AnimatedWalkingSprite
from .sprite import TextureAnimation
from .sprite import TextureKeyframe
from .sprite import PyMunk
from .sprite import PymunkMixin
from .sprite import SpriteType
from .sprite import SpriteType_co
from .sprite import Sprite
from .sprite import BasicSprite

# from .sprite import SimpleSprite
from .sprite import SpriteCircle
from .sprite import SpriteSolidColor

from .sprite_list import SpriteList
from .sprite_list import SpriteSequence
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
from .scene import SceneKeyError

from .physics_engines import PhysicsEnginePlatformer
from .physics_engines import PhysicsEngineSimple

from .tilemap import load_tilemap
from .tilemap import TileMap

from .pymunk_physics_engine import PymunkPhysicsEngine
from .pymunk_physics_engine import PymunkPhysicsObject
from .pymunk_physics_engine import PymunkException

from .version import VERSION

from .paths import has_line_of_sight
from .paths import AStarBarrierList
from .paths import astar_calculate_path

from .context import ArcadeContext

from .texture_atlas import DefaultTextureAtlas

from .perf_info import enable_timings
from .perf_info import print_timings
from .perf_info import get_fps
from .perf_info import get_timings
from .perf_info import clear_timings
from .perf_info import timings_enabled
from .perf_info import disable_timings

from .perf_graph import PerfGraph

from .camera import Camera2D

from .types.rect import Rect, LRBT, LBWH, XYWH

# Module imports
from arcade import color as color
from arcade import csscolor as csscolor
from arcade import uicolor as uicolor
from arcade import camera as camera
from arcade import key as key
from arcade import resources as resources
from arcade import types as types
from arcade import math as math
from arcade import shape_list as shape_list
from arcade import hitbox as hitbox
from arcade import experimental as experimental
from arcade.types import rect

# For ease of access for beginners
from pyglet.math import Vec2, Vec3, Vec4

from .text import (
    draw_text,
    load_font,
    create_text_sprite,
    Text,
)

__all__ = [
    "AStarBarrierList",
    "AnimatedWalkingSprite",
    "TextureAnimationSprite",
    "TextureAnimation",
    "TextureKeyframe",
    "ArcadeContext",
    "ControllerManager",
    "FACE_DOWN",
    "FACE_LEFT",
    "FACE_RIGHT",
    "FACE_UP",
    "MOUSE_BUTTON_LEFT",
    "MOUSE_BUTTON_MIDDLE",
    "MOUSE_BUTTON_RIGHT",
    "NoOpenGLException",
    "PerfGraph",
    "PhysicsEnginePlatformer",
    "PhysicsEngineSimple",
    "PyMunk",
    "PymunkException",
    "PymunkPhysicsEngine",
    "PymunkPhysicsObject",
    "Rect",
    "LBWH",
    "LRBT",
    "XYWH",
    "Section",
    "SectionManager",
    "Scene",
    "SceneKeyError",
    "Sound",
    "BasicSprite",
    "Sprite",
    "SpriteType",
    "SpriteType_co",
    "PymunkMixin",
    "SpriteCircle",
    "SpriteList",
    "SpriteSequence",
    "SpriteSolidColor",
    "Text",
    "Texture",
    "TextureCacheManager",
    "SpriteSheet",
    "DefaultTextureAtlas",
    "TileMap",
    "VERSION",
    "Vec2",
    "Vec3",
    "Vec4",
    "View",
    "Window",
    "astar_calculate_path",
    "check_for_collision",
    "check_for_collision_with_list",
    "check_for_collision_with_lists",
    "close_window",
    "disable_timings",
    "draw_arc_filled",
    "draw_arc_outline",
    "draw_circle_filled",
    "draw_circle_outline",
    "draw_ellipse_filled",
    "draw_ellipse_outline",
    "draw_line",
    "draw_line_strip",
    "draw_lines",
    "draw_lrbt_rectangle_filled",
    "draw_lrbt_rectangle_filled",
    "draw_lrbt_rectangle_outline",
    "draw_lrbt_rectangle_outline",
    "draw_parabola_filled",
    "draw_parabola_outline",
    "draw_point",
    "draw_points",
    "draw_polygon_filled",
    "draw_polygon_outline",
    "draw_rect_filled",
    "draw_rect_outline",
    "draw_text",
    "draw_texture_rect",
    "draw_sprite",
    "draw_sprite_rect",
    "draw_triangle_filled",
    "draw_triangle_outline",
    "draw_lbwh_rectangle_filled",
    "draw_lbwh_rectangle_outline",
    "enable_timings",
    "exit",
    "finish_render",
    "get_closest_sprite",
    "get_display_size",
    "get_distance_between_sprites",
    "get_sprites_in_rect",
    "get_controllers",
    "get_game_controllers",
    "get_image",
    "get_joysticks",
    "get_pixel",
    "get_points_for_thick_line",
    "get_screens",
    "get_sprites_at_exact_point",
    "get_sprites_at_point",
    "SpatialHash",
    "get_timings",
    "create_text_sprite",
    "clear_timings",
    "get_window",
    "get_fps",
    "has_line_of_sight",
    "load_animated_gif",
    "load_font",
    "load_sound",
    "load_spritesheet",
    "load_texture",
    "load_image",
    "make_circle_texture",
    "make_soft_circle_texture",
    "make_soft_square_texture",
    "open_window",
    "print_timings",
    "play_sound",
    "load_tilemap",
    "run",
    "schedule",
    "set_background_color",
    "set_window",
    "start_render",
    "stop_sound",
    "timings_enabled",
    "unschedule",
    "schedule_once",
    "get_default_texture",
    "get_default_image",
    "hitbox",
    "experimental",
    "rect",
    "color",
    "csscolor",
    "uicolor",
    "key",
    "resources",
    "types",
    "math",
    "shape_list",
    "Camera2D",
]

__version__ = VERSION

# Piggyback on pyglet's doc run detection
if not getattr(sys, "is_pyglet_doc_run", False):
    # Load additional game controller mappings to Pyglet
    if not headless:
        try:
            import pyglet.input.controller

            mappings_file = resources.resolve(":system:gamecontrollerdb.txt")
            # TODO: remove string conversion once fixed upstream
            pyglet.input.controller.add_mappings_from_file(str(mappings_file))
        except AssertionError:
            pass
