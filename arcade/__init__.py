"""
The Arcade Library

A Python simple, easy to use module for creating 2D games.
"""

# Note: DO NOT EDIT arcade/__init__.py
# Instead look at util/init_template.py and update_init.py

# Error out if we import Arcade with an incompatible version of Python.
import platform
import sys
import os

from pathlib import Path

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    sys.exit("The Arcade Library requires Python 3.6 or higher.")


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

# On OS X we need to disable the shadow context
# because the 2.1 shadow context cannot be upgrade to a 3.3+ core
if platform.system() == 'Darwin':
    pyglet.options['shadow_window'] = False

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
from .window_commands import finish_render
from .window_commands import get_display_size
from .window_commands import get_projection
from .window_commands import get_scaling_factor
from .window_commands import get_viewport
from .window_commands import get_window
from .window_commands import pause
from .window_commands import quick_run
from .window_commands import run
from .window_commands import schedule
from .window_commands import set_background_color
from .window_commands import set_viewport
from .window_commands import set_window
from .window_commands import start_render
from .window_commands import unschedule

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

from .drawing_support import calculate_hit_box_points_detailed
from .drawing_support import calculate_hit_box_points_simple
from .drawing_support import get_four_byte_color
from .drawing_support import get_four_float_color
from .drawing_support import get_points_for_thick_line
from .drawing_support import make_transparent_color
from .drawing_support import rotate_point

from .texture import Matrix3x3
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
from .geometry import get_distance
from .geometry import is_point_in_polygon

from .isometric import create_isometric_grid_lines
from .isometric import isometric_grid_to_screen
from .isometric import screen_to_isometric_grid

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
from .particle import clamp

from .sound import Sound
from .sound import load_sound
from .sound import play_sound
from .sound import stop_sound

from .sprite import FACE_DOWN
from .sprite import FACE_LEFT
from .sprite import FACE_RIGHT
from .sprite import FACE_UP
from .sprite import AnimatedTimeBasedSprite
from .sprite import AnimatedTimeSprite
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
from .sprite_list import get_closest_sprite
from .sprite_list import get_sprites_at_exact_point
from .sprite_list import get_sprites_at_point

from .physics_engines import PhysicsEnginePlatformer
from .physics_engines import PhysicsEngineSimple

from .text import DEFAULT_FONT_NAMES
from .text import CreateText
from .text import Text
from .text import create_text
from .text import draw_text
from .text import draw_text_2
from .text import get_text_image
from .text import render_text

from .tilemap import get_tilemap_layer
from .tilemap import process_layer
from .tilemap import read_tmx

from .pymunk_physics_engine import PymunkPhysicsEngine
from .pymunk_physics_engine import PymunkPhysicsObject

from .version import VERSION

from .paths import AStarBarrierList
from .paths import astar_calculate_path
from .paths import has_line_of_sight

from .context import ArcadeContext



# noinspection PyPep8
from arcade import experimental

# --- Generated __all__ ---

__all__ = ['AStarBarrierList',
           'AnimatedTimeBasedSprite',
           'AnimatedTimeSprite',
           'AnimatedWalkingSprite',
           'AnimationKeyframe',
           'ArcadeContext',
           'Color',
           'CreateText',
           'DEFAULT_FONT_NAMES',
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
           'Matrix3x3',
           'NamedPoint',
           'NoOpenGLException',
           'Particle',
           'PhysicsEnginePlatformer',
           'PhysicsEngineSimple',
           'Point',
           'PointList',
           'PyMunk',
           'PymunkPhysicsEngine',
           'PymunkPhysicsObject',
           'RGB',
           'RGBA',
           'Rect',
           'RectList',
           'Shape',
           'ShapeElementList',
           'Sound',
           'Sprite',
           'SpriteCircle',
           'SpriteList',
           'SpriteSolidColor',
           'TShape',
           'Text',
           'Texture',
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
           'clamp',
           'cleanup_texture_cache',
           'close_window',
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
           'create_text',
           'create_triangles_filled_with_colors',
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
           'draw_text',
           'draw_text_2',
           'draw_texture_rectangle',
           'draw_triangle_filled',
           'draw_triangle_outline',
           'draw_xywh_rectangle_filled',
           'draw_xywh_rectangle_outline',
           'earclip',
           'finish_render',
           'get_closest_sprite',
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
           'get_text_image',
           'get_tilemap_layer',
           'get_viewport',
           'get_window',
           'has_line_of_sight',
           'is_point_in_polygon',
           'isometric_grid_to_screen',
           'lerp',
           'lerp_vec',
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
           'play_sound',
           'process_layer',
           'quick_run',
           'rand_angle_360_deg',
           'rand_angle_spread_deg',
           'rand_in_circle',
           'rand_in_rect',
           'rand_on_circle',
           'rand_on_line',
           'rand_vec_magnitude',
           'rand_vec_spread_deg',
           'read_tmx',
           'render_text',
           'rotate_point',
           'run',
           'schedule',
           'screen_to_isometric_grid',
           'set_background_color',
           'set_viewport',
           'set_window',
           'start_render',
           'stop_sound',
           'trim_image',
           'unschedule',
           ]

__version__ = VERSION
