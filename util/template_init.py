"""
The Arcade Library

A Python simple, easy to use module for creating 2D games.
"""

# Note: DO NOT EDIT arcade/__init__.py
# Instead look at util/init_template.py and update_init.py

# Error out if we import Arcade with an incompatible version of Python.
import platform
import sys

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    sys.exit("The Arcade Library requires Python 3.6 or higher.")

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
