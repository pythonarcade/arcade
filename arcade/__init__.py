"""
The Arcade Library

A Python simple, easy to use module for creating 2D games.
"""

# Error out if we import Arcade with an incompatible version of Python.
import sys
import os

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    sys.exit("The Arcade Library requires Python 3.6 or higher.")

try:
    import pyglet_ffmpeg2
except Exception as e:
    print("Unable to load the ffmpeg library. ", e)

import pyglet

pyglet.options['shadow_window'] = False

from arcade import color
from arcade import csscolor
from arcade import key
from arcade.application import *
from arcade.arcade_types import *
from arcade.utils import *
from arcade.draw_commands import *
from arcade.buffered_draw_commands import *
from arcade.geometry import *
from arcade.physics_engines import *
from arcade.emitter import *
from arcade.emitter_simple import *
from arcade.particle import *
from arcade.sound import *
from arcade.sprite import *
from arcade.sprite_list import *
from arcade.version import *
from arcade.window_commands import *
from arcade.joysticks import *
from arcade.read_tiled_map import *
from arcade.isometric import *
from arcade.text import draw_text
from arcade.text import create_text
from arcade.text import render_text
