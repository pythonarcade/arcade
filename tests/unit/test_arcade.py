from types import ModuleType
from copy import copy
import logging
import arcade
import inspect
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
        if type(attr) is ModuleType or not inspect.isroutine(attr):
            remaining.remove(name)
        # Extra awful trick because:
        # 1. attempting to get __module__ of bool members raises AttributeError
        # 2. inspect.isbuiltin(bool) does not return True for bool
        # 2. inspect.getmodule(bool) returns the builtins module
        elif not inspect.getmodule(attr).__name__.startswith('arcade.'):
            remaining.remove(name)

    assert len(remaining) == 0


def test_logging():
    arcade.configure_logging(logging.WARNING)
    logger = logging.getLogger('arcade')
    assert logger.level == logging.WARNING
