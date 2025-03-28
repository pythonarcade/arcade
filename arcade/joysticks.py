import pyglet.input
from pyglet.input import Joystick

__all__ = ["get_joysticks", "get_game_controllers"]


def get_joysticks() -> list[Joystick]:
    """
    Get a list of all the game controllers

    This is an alias of :func:`get_game_controllers`, which is better worded.
    """
    return pyglet.input.get_joysticks()  # type: ignore  # pending https://github.com/pyglet/pyglet/issues/842


def get_game_controllers() -> list[Joystick]:
    """
    Get a list of all the game controllers
    """
    return get_joysticks()
