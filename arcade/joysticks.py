import pyglet.input
from typing import List
from pyglet.input import Joystick


def get_joysticks() -> List[Joystick]:
    """
    Get a list of all the game controllers

    This is an alias of ``get_game_controllers``, which is better worded.

    :return: List of game controllers
    """
    return pyglet.input.get_joysticks()


def get_game_controllers() -> List[Joystick]:
    """
    Get a list of all the game controllers

    :return: List of game controllers
    """
    return get_joysticks()
