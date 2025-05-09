"""
Controller API. This is basically just an alias to Pyglet's controller API.

For more info on this API, see
https://pyglet.readthedocs.io/en/latest/programming_guide/input.html#using-controllers
"""

import pyglet.input

__all__ = ["get_controllers", "ControllerManager"]


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
