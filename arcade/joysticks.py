from __future__ import annotations

import pyglet.input
from typing import List
from pyglet.input import Joystick

__all__ = [
    "get_joysticks",
    "get_game_controllers"
]


def get_joysticks() -> List[Joystick]:
    """
    Get a list of all the game controllers

    This is an alias of ``get_game_controllers``, which is better worded.

    :return: List of game controllers
    """
    return pyglet.input.get_joysticks() # type: ignore  # pending https://github.com/pyglet/pyglet/issues/842


def get_game_controllers() -> List[Joystick]:
    """
    Get a list of all the game controllers

    :return: List of game controllers
    """
    return get_joysticks()
