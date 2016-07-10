"""
The main window class that all object-oriented applications should
derive from.
"""

import pyglet


MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_MIDDLE = 2
MOUSE_BUTTON_RIGHT = 4


class Window(pyglet.window.Window):
    """
    Window class

    >>> import arcade
    >>> window = arcade.Window(800, 600)
    >>> window.animate(0.25)
    >>> window.close()
    """
    def __init__(self, width: float, height: float,
                 title: str='Arcade Window'):
        # This is nicer, but Python 3.x only
        # super().__init__(width=width, height=height, caption=title)
        pyglet.window.Window.__init__(self, width=width, height=height,
                                      caption=title)

        self.set_update_rate(1/80)
        # set_viewport(0, self.width, 0, self.height)

    def animate(self, delta_time: float):
        """
        Move everything.

        Args:
            :dt (float): Time interval since the last time the function was \
called.

        """
        pass

    def set_update_rate(self, rate: float):
        """
        Set how often the screen should be updated.
        """
        pyglet.clock.schedule_interval(self.animate, rate)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ Override this function to add mouse functionality. """
        pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """ Override this function to add mouse button functionality. """
        pass

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        """ Override this function to add mouse button functionality. """
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Override this function to add mouse button functionality. """
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def on_draw(self):
        pass
