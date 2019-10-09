"""
The Arcade Library

A Python simple, easy to use module for creating 2D games.
"""

# Error out if we import Arcade with an incompatible version of Python.
import sys

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    sys.exit("The Arcade Library requires Python 3.6 or higher.")

try:
    import pyglet_ffmpeg2
except Exception as e:
    print("Unable to load the ffmpeg library. ", e)

# noinspection PyPep8
import pyglet

pyglet.options['shadow_window'] = False

# noinspection PyPep8
from arcade import color
# noinspection PyPep8
from arcade import csscolor
# noinspection PyPep8
from arcade import key
# noinspection PyPep8
from arcade.application import *
# noinspection PyPep8
from arcade.arcade_types import *
# noinspection PyPep8
from arcade.utils import *
# noinspection PyPep8
from arcade.draw_commands import *
# noinspection PyPep8
from arcade.buffered_draw_commands import *
# noinspection PyPep8
from arcade.geometry import *
# noinspection PyPep8
from arcade.physics_engines import *
# noinspection PyPep8
from arcade.emitter import *
# noinspection PyPep8
from arcade.emitter_simple import *
# noinspection PyPep8
from arcade.particle import *
# noinspection PyPep8
from arcade.sound import *
# noinspection PyPep8
from arcade.sprite import *
# noinspection PyPep8
from arcade.sprite_list import *
# noinspection PyPep8
from arcade.version import *
# noinspection PyPep8
from arcade.window_commands import *
# noinspection PyPep8
from arcade.joysticks import *
# noinspection PyPep8
from arcade.read_tiled_map import *
# noinspection PyPep8
from arcade.isometric import *
# noinspection PyPep8
from arcade.text import draw_text
# noinspection PyPep8,PyDeprecation
from arcade.text import create_text
# noinspection PyPep8,PyDeprecation
from arcade.text import render_text
# noinspection PyPep8
from arcade import tilemap
# noinspection PyPep8
from arcade.gui import TextButton
