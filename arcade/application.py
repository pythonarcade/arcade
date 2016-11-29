"""
The main window class that all object-oriented applications should
derive from.
"""
from typing import Tuple

import pyglet

MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_MIDDLE = 2
MOUSE_BUTTON_RIGHT = 4


class Window(pyglet.window.Window):
    """
    Window class

    """

    def __init__(self, width: float, height: float,
                 title: str = 'Arcade Window',
                 resizable: bool = False):
        super().__init__(width=width, height=height, caption=title,
                         resizable=resizable)

        self.set_update_rate(1 / 80)
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

    def set_min_size(self, width: float, height: float):
        """ Wrap the Pyglet window call to set minimum size

        Args:
            :width: width in pixels.
            :height: height in pixels.
        Returns:
            None
        Raises:
            ValueError

        Example:

        >>> import arcade
        >>> window = arcade.Window(200, 100, resizable=True)
        >>> window.set_min_size(200, 200)
        >>> window.close()
        """

        if self.resizable:
            super().set_minimum_size(width, height)
        else:
            raise ValueError('Cannot set min size on non-resizable window')

    def set_max_size(self, width: float, height: float):
        """ Wrap the Pyglet window call to set maximum size

        Args:
            :width: width in pixels.
            :height: height in pixels.
        Returns:
            None
        Raises:
            ValueError

        Example:

        >>> import arcade
        >>> window = arcade.Window(200, 100, resizable=True)
        >>> window.set_max_size(200, 200)
        >>> window.close()

        """

        if self.resizable:
            super().set_maximum_size(width, height)
        else:
            raise ValueError('Cannot set max size on non-resizable window')

    def set_size(self, width: float, height: float):
        """ Ignore the resizable flag and set the size """

        super().set_size(width, height)

    def get_location(self) -> Tuple[int, int]:
        """ Return the X/Y coordinates of the window """

        return super().get_location()
