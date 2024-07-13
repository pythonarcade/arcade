from types import ModuleType
from copy import copy
import logging
import arcade
from arcade import *


def test_import():
    """Compare arcade.__all__ to the actual module contents"""
    import arcade
    global_names = set(k for k in globals() if not k.startswith('_'))
    arcade_names = set(k for k in arcade.__dict__ if not k.startswith('_'))

    # Get the common members
    common = global_names.intersection(arcade_names)
    remaining = arcade_names - common
    for name in copy(remaining):
        attr = getattr(arcade, name)
        if type(attr) is ModuleType:
            remaining.remove(name)
        elif not attr.__module__.startswith('arcade.'):
            remaining.remove(name)

    assert len(remaining) == 0


def test_logging():
    arcade.configure_logging(logging.WARNING)
    logger = logging.getLogger('arcade')
    assert logger.level == logging.WARNING
