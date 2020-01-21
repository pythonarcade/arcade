"""
The Arcade Library

A Python simple, easy to use module for creating 2D games.
"""

# Note: DO NOT EDIT arcade/__init__.py
# Instead look at util/init_template.py and update_init.py

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

