import pyglet.input


def get_joysticks():
    return pyglet.input.get_joysticks()

def get_game_controllers():
    return get_joysticks()
