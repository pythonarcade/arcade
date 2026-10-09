import pyglet.input
from pyglet.input import Joystick

__all__ = ["get_joysticks"]


def get_joysticks() -> list[Joystick]:
    """
    Get a list of all the joysticks.

    These are pyglet :py:class:`~pyglet.input.Joystick` objects, which give
    raw access to the axes and buttons. For game controllers with named
    buttons and sticks, use :py:func:`arcade.get_controllers` instead.
    """
    return pyglet.input.get_joysticks()  # type: ignore  # pending https://github.com/pyglet/pyglet/issues/842
