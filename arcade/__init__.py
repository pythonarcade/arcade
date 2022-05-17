"""
The Arcade Library

A Python simple, easy to use module for creating 2D games.
"""
# flake8: noqa: E402

# Error out if we import Arcade with an incompatible version of Python.
import sys
import os

from pathlib import Path

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 7):
    sys.exit("The Arcade Library requires Python 3.7 or higher.")


def configure_logging(level: int = None):
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

# Disable shadow windows until issues with intel GPUs
# on Windows and elsewhere are better understood.
# Originally, this only disabled them for macs where
# the 2.1 shadow context cannot be upgrade to a 3.3+ core
pyglet.options['shadow_window'] = False
# Use the old gdi fonts on windows until directwrite is fast/stable
pyglet.options['win32_gdi_font'] = True

# HACK: Increase pyglet's glyph atlas size to minimize issues
# This was only needed with pyglet==2.0dev13 and earlier
# when we were chasing down a text glitch when new atlases
# were created (Creating new IndexedVertexDomains)
# if not getattr(sys, 'is_pyglet_doc_run', False):
#     pyglet.font.base.Font.texture_width = 4096
#     pyglet.font.base.Font.texture_height = 4096

# noinspection PyPep8
from arcade import color
# noinspection PyPep8
from arcade import csscolor
# noinspection PyPep8
from arcade import key
# noinspection PyPep8
from arcade import resources

# --- Generated imports ---
from .window_commands import close_window
from .window_commands import create_orthogonal_projection
from .window_commands import exit
from .window_commands import finish_render
from .window_commands import get_display_size
from .window_commands import get_projection
from .window_commands import get_scaling_factor
from .window_commands import get_viewport
from .window_commands import get_window
from .window_commands import pause
from .window_commands import run
from .window_commands import schedule
from .window_commands import set_background_color
from .window_commands import set_viewport
from .window_commands import set_window
from .window_commands import start_render
from .window_commands import unschedule

from .camera import Camera
from .sections import Section, SectionManager

from .application import MOUSE_BUTTON_LEFT
from .application import MOUSE_BUTTON_MIDDLE
from .application import MOUSE_BUTTON_RIGHT
from .application import NoOpenGLException
from .application import View
from .application import Window
from .application import get_screens
from .application import open_window

from .arcade_types import Color
from .arcade_types import NamedPoint
from .arcade_types import Point
from .arcade_types import PointList
from .arcade_types import RGB
from .arcade_types import RGBA
from .arcade_types import Rect
from .arcade_types import RectList
from .arcade_types import Vector
from .arcade_types import TiledObject

from .earclip_module import earclip

from .utils import lerp
from .utils import lerp_vec
from .utils import rand_angle_360_deg
from .utils import rand_angle_spread_deg
from .utils import rand_in_circle
from .utils import rand_in_rect
from .utils import rand_on_circle
from .utils import rand_on_line
from .utils import rand_vec_magnitude
from .utils import rand_vec_spread_deg
from .utils import generate_uuid_from_kwargs

from .geometry_generic import get_distance
from .geometry_generic import rotate_point
from .geometry_generic import clamp
from .geometry_generic import get_angle_degrees
from .geometry_generic import get_angle_radians

from .easing import EasingData
from .easing import linear
from .easing import smoothstep
from .easing import ease_in
from .easing import ease_out
from .easing import ease_in_out
from .easing import ease_out_elastic
from .easing import ease_out_bounce
from .easing import ease_in_back
from .easing import ease_out_back
from .easing import ease_in_sin
from .easing import ease_out_sin
from .easing import ease_in_out_sin
from .easing import easing
from .easing import ease_angle
from .easing import ease_angle_update
from .easing import ease_update
from .easing import ease_value
from .easing import ease_position

from .hitbox import calculate_hit_box_points_detailed
from .hitbox import calculate_hit_box_points_simple

from .drawing_support import get_four_byte_color
from .drawing_support import get_three_float_color
from .drawing_support import get_four_float_color
from .drawing_support import get_points_for_thick_line
from .drawing_support import make_transparent_color
from .drawing_support import uint24_to_three_byte_color
from .drawing_support import uint32_to_four_byte_color
from .drawing_support import color_from_hex_string
from .drawing_support import float_to_byte_color

from .texture import Texture
from .texture import cleanup_texture_cache
from .texture import load_spritesheet
from .texture import load_texture
from .texture import load_texture_pair
from .texture import load_textures
from .texture import make_circle_texture
from .texture import make_soft_circle_texture
from .texture import make_soft_square_texture
from .texture import trim_image

from .buffered_draw_commands import TShape
from .buffered_draw_commands import Shape
from .buffered_draw_commands import ShapeElementList
from .buffered_draw_commands import create_ellipse
from .buffered_draw_commands import create_ellipse_filled
from .buffered_draw_commands import create_ellipse_filled_with_colors
from .buffered_draw_commands import create_ellipse_outline
from .buffered_draw_commands import create_line
from .buffered_draw_commands import create_line_generic
from .buffered_draw_commands import create_line_generic_with_colors
from .buffered_draw_commands import create_line_loop
from .buffered_draw_commands import create_line_strip
from .buffered_draw_commands import create_lines
from .buffered_draw_commands import create_lines_with_colors
from .buffered_draw_commands import create_polygon
from .buffered_draw_commands import create_rectangle
from .buffered_draw_commands import create_rectangle_filled
from .buffered_draw_commands import create_rectangle_filled_with_colors
from .buffered_draw_commands import create_rectangle_outline
from .buffered_draw_commands import create_rectangles_filled_with_colors
from .buffered_draw_commands import create_triangles_filled_with_colors
from .buffered_draw_commands import get_rectangle_points

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
from .draw_commands import draw_lrtb_rectangle_outline
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

from .geometry import are_polygons_intersecting
from .geometry import is_point_in_polygon

from .isometric import create_isometric_grid_lines
from .isometric import isometric_grid_to_screen
from .isometric import screen_to_isometric_grid

# We don't have joysticks game controllers in headless mode
if not pyglet.options["headless"]:
    from .joysticks import get_game_controllers
    from .joysticks import get_joysticks

from .emitter import EmitBurst
from .emitter import EmitController
from .emitter import EmitInterval
from .emitter import EmitMaintainCount
from .emitter import Emitter
from .emitter import EmitterIntervalWithCount
from .emitter import EmitterIntervalWithTime

from .emitter_simple import make_burst_emitter
from .emitter_simple import make_interval_emitter

from .particle import FilenameOrTexture
from .particle import EternalParticle
from .particle import FadeParticle
from .particle import LifetimeParticle
from .particle import Particle

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
from .sprite import Sprite
from .sprite import SpriteCircle
from .sprite import SpriteSolidColor
from .sprite import get_distance_between_sprites

from .sprite_list import SpriteList
from .sprite_list import check_for_collision
from .sprite_list import check_for_collision_with_list
from .sprite_list import check_for_collision_with_lists
from .sprite_list import get_closest_sprite
from .sprite_list import get_sprites_at_exact_point
from .sprite_list import get_sprites_at_point

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
from .texture_atlas import AtlasRegion

from .perf_info import enable_timings
from .perf_info import print_timings
from .perf_info import get_fps
from .perf_info import get_timings
from .perf_info import clear_timings
from .perf_info import timings_enabled
from .perf_info import disable_timings

from .perf_graph import PerfGraph


# noinspection PyPep8
from arcade import experimental

from .text_pyglet import (
    draw_text,
    load_font,
    Text,
)
from .text_pillow import (
    create_text_sprite,
    create_text_image,
    DEFAULT_FONT_NAMES,
)


__all__ = ['AStarBarrierList',
           'AnimatedTimeBasedSprite',
           'AnimatedWalkingSprite',
           'AnimationKeyframe',
           'ArcadeContext',
           'AtlasRegion',
           'Camera',
           'Color',
           'DEFAULT_FONT_NAMES',
           'EasingData',
           'EmitBurst',
           'EmitController',
           'EmitInterval',
           'EmitMaintainCount',
           'Emitter',
           'EmitterIntervalWithCount',
           'EmitterIntervalWithTime',
           'EternalParticle',
           'FACE_DOWN',
           'FACE_LEFT',
           'FACE_RIGHT',
           'FACE_UP',
           'FadeParticle',
           'FilenameOrTexture',
           'LifetimeParticle',
           'MOUSE_BUTTON_LEFT',
           'MOUSE_BUTTON_MIDDLE',
           'MOUSE_BUTTON_RIGHT',
           'NamedPoint',
           'NoOpenGLException',
           'Particle',
           'PerfGraph',
           'PhysicsEnginePlatformer',
           'PhysicsEngineSimple',
           'Point',
           'PointList',
           'PyMunk',
           'PymunkException',
           'PymunkPhysicsEngine',
           'PymunkPhysicsObject',
           'RGB',
           'RGBA',
           'Rect',
           'RectList',
           'Section',
           'SectionManager',
           'Scene',
           'Shape',
           'ShapeElementList',
           'Sound',
           'Sprite',
           'SpriteCircle',
           'SpriteList',
           'SpriteSolidColor',
           'TShape',
           'TiledObject',
           'Text',
           'Texture',
           'TextureAtlas',
           'TileMap',
           'VERSION',
           'Vector',
           'View',
           'Window',
           'are_polygons_intersecting',
           'astar_calculate_path',
           'calculate_hit_box_points_detailed',
           'calculate_hit_box_points_simple',
           'check_for_collision',
           'check_for_collision_with_list',
           'check_for_collision_with_lists',
           'clamp',
           'cleanup_texture_cache',
           'close_window',
           'color_from_hex_string',
           'create_ellipse',
           'create_ellipse_filled',
           'create_ellipse_filled_with_colors',
           'create_ellipse_outline',
           'create_isometric_grid_lines',
           'create_line',
           'create_line_generic',
           'create_line_generic_with_colors',
           'create_line_loop',
           'create_line_strip',
           'create_lines',
           'create_lines_with_colors',
           'create_orthogonal_projection',
           'create_polygon',
           'create_rectangle',
           'create_rectangle_filled',
           'create_rectangle_filled_with_colors',
           'create_rectangle_outline',
           'create_rectangles_filled_with_colors',
           'create_text_image',
           'create_text_sprite',
           'create_triangles_filled_with_colors',
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
           'draw_lrtb_rectangle_outline',
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
           'create_text',
           'draw_text',
           'draw_texture_rectangle',
           'draw_triangle_filled',
           'draw_triangle_outline',
           'draw_xywh_rectangle_filled',
           'draw_xywh_rectangle_outline',
           'ease_angle',
           'ease_value',
           'ease_position',
           'easing',
           'ease_in',
           'ease_in_out',
           'ease_out_elastic',
           'ease_out_bounce',
           'ease_in_back',
           'ease_out_back',
           'ease_in_sin',
           'ease_out_sin',
           'ease_in_out_sin',
           'ease_out',
           'smoothstep',
           'linear',
           'ease_angle_update',
           'ease_update',
           'ease_position',
           'earclip',
           'enable_timings',
           'exit',
           'finish_render',
           'float_to_byte_color',
           'generate_uuid_from_kwargs',
           'get_closest_sprite',
           'get_angle_degrees',
           'get_angle_radians',
           'get_display_size',
           'get_distance',
           'get_distance_between_sprites',
           'get_four_byte_color',
           'get_four_float_color',
           'get_game_controllers',
           'get_image',
           'get_joysticks',
           'get_pixel',
           'get_points_for_thick_line',
           'get_projection',
           'get_rectangle_points',
           'get_scaling_factor',
           'get_screens',
           'get_sprites_at_exact_point',
           'get_sprites_at_point',
           'get_timings',
           'get_three_float_color',
           'clear_timings',
           'create_text_image',
           'get_viewport',
           'get_window',
           'get_fps',
           'has_line_of_sight',
           'is_point_in_polygon',
           'isometric_grid_to_screen',
           'lerp',
           'lerp_vec',
           'load_animated_gif',
           'load_font',
           'load_sound',
           'load_spritesheet',
           'load_texture',
           'load_texture_pair',
           'load_textures',
           'make_burst_emitter',
           'make_circle_texture',
           'make_interval_emitter',
           'make_soft_circle_texture',
           'make_soft_square_texture',
           'make_transparent_color',
           'open_window',
           'pause',
           'print_timings',
           'play_sound',
           'rand_angle_360_deg',
           'rand_angle_spread_deg',
           'rand_in_circle',
           'rand_in_rect',
           'rand_on_circle',
           'rand_on_line',
           'rand_vec_magnitude',
           'rand_vec_spread_deg',
           'read_tmx',
           'load_tilemap',
           'rotate_point',
           'run',
           'schedule',
           'screen_to_isometric_grid',
           'set_background_color',
           'set_viewport',
           'set_window',
           'start_render',
           'stop_sound',
           'timings_enabled',
           'trim_image',
           'uint24_to_three_byte_color',
           'uint32_to_four_byte_color',
           'unschedule',
           ]


__version__ = VERSION

# Piggyback on pyglet's doc run detection
if not getattr(sys, 'is_pyglet_doc_run', False):
    # Auto load fonts
    load_font(":resources:fonts/ttf/Kenney Blocks.ttf")
    load_font(":resources:fonts/ttf/Kenney Future.ttf")
    load_font(":resources:fonts/ttf/Kenney Future Narrow.ttf")
    load_font(":resources:fonts/ttf/Kenney High.ttf")
    load_font(":resources:fonts/ttf/Kenney High Square.ttf")
    load_font(":resources:fonts/ttf/Kenney Mini.ttf")
    load_font(":resources:fonts/ttf/Kenney Mini Square.ttf")
    load_font(":resources:fonts/ttf/Kenney Pixel.ttf")
    load_font(":resources:fonts/ttf/Kenney Pixel Square.ttf")
    load_font(":resources:fonts/ttf/Kenney Rocket.ttf")
    load_font(":resources:fonts/ttf/Kenney Rocket Square.ttf")
