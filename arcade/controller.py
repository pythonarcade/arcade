"""
Controller API. This is basically just an alias to Pyglet's controller API.

For more info on this API, see
https://pyglet.readthedocs.io/en/latest/programming_guide/input.html#using-controllers
"""

import sys

import pyglet.input
import pyglet.input.controller

from arcade import resources

__all__ = ["get_controllers", "ControllerManager"]

# Load additional game controller mappings to pyglet. Piggyback on
# pyglet's doc run detection.
if not getattr(sys, "is_pyglet_doc_run", False):
    try:
        mappings_file = resources.resolve(":system:gamecontrollerdb.txt")
        # TODO: remove string conversion once fixed upstream
        pyglet.input.controller.add_mappings_from_file(str(mappings_file))
    except AssertionError:
        pass


def get_controllers():
    """
    This returns a list of controllers, it is synonymous with calling
    ``pyglet.input.get_controllers()``
    """
    return pyglet.input.get_controllers()


class ControllerManager(pyglet.input.ControllerManager):
    """A ControllerManager provides an interface for handling connect/disconnect events.

    Please see Pyglet docs:
    https://pyglet.readthedocs.io/en/latest/programming_guide/input.html#controllermanager
    """

    pass
