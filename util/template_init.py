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


# noinspection PyPep8
import pyglet

# Disable shadow windows until issues with intel GPUs
# on Windows and elsewhere are better understood.
# Originally, this only disabled them for macs where
# the 2.1 shadow context cannot be upgrade to a 3.3+ core
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
$imports

# noinspection PyPep8
from arcade import experimental

# --- Generated __all__ ---
$all
