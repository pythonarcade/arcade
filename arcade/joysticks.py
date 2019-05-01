import pyglet.input


def get_joysticks():
    """
    Get a list of all the game controllers

    This is an alias of ``get_game_controllers``, which is better worded.

    :return: List of game controllers
    """
    return pyglet.input.get_joysticks()


def get_game_controllers():
    """
    Get a list of all the game controllers

    :return: List of game controllers
    """
    return get_joysticks()
