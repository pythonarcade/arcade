from .window_commands import *

import pyglet


class Window(pyglet.window.Window):
    """
    Window class

    >>> import arcade
    >>> window = arcade.Window(800, 600)
    >>> window.animate(0.25)
    >>> window.close()
    """
    def __init__(self, width, height):
        super().__init__(width=width, height=height)
        self.set_update_rate(1/80)
        # set_viewport(0, self.width, 0, self.height)

    def animate(self, dt):
        """
        Move everything.

        Args:
            :dt (float): Time interval since the last time the function
            was called.

        """
        pass

    def set_update_rate(self, rate):
        pyglet.clock.schedule_interval(self.animate, rate)
