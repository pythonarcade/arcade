"""
The main window class that all object-oriented applications should
derive from.
"""
from typing import Tuple
from numbers import Number

from arcade.window_commands import set_viewport
from arcade.window_commands import get_viewport
from arcade.window_commands import set_window

import pyglet
import pyglet.gl as gl
from pyglet.gl import gl_info

MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_MIDDLE = 2
MOUSE_BUTTON_RIGHT = 4


class Window(pyglet.window.Window):
    """
    Window class
    """

    def __init__(self, width: float = 800, height: float = 600,
                 title: str = 'Arcade Window', fullscreen: bool = False,
                 resizable: bool = False, update_rate=1/60):
        config = pyglet.gl.Config(major_version=3, minor_version=3, double_buffer=True)

        super().__init__(width=width, height=height, caption=title,
                         resizable=resizable, config=config)

        if update_rate:
            from pyglet import compat_platform
            if compat_platform == 'darwin':
                # Set vsync to false, or we'll be limited to a 1/30 sec update rate possibly
                self.context.set_vsync(False)

            self.set_update_rate(1/60)

        super().set_fullscreen(fullscreen)
        self.invalid = False
        set_window(self)
        set_viewport(0, self.width, 0, self.height)

    def update(self, delta_time: float):
        """
        Move everything. For better consistency in naming, use ``on_update`` instead.

        Args:
            :dt (float): Time interval since the last time the function was called.

        """
        pass

    def on_update(self, delta_time: float):
        """
        Move everything.

        Args:
            :dt (float): Time interval since the last time the function was called.

        """
        pass

    def set_update_rate(self, rate: float):
        """
        Set how often the screen should be updated.
        For example, self.set_update_rate(1 / 20) will set the update rate to 60 fps
        """
        pyglet.clock.unschedule(self.update)
        pyglet.clock.schedule_interval(self.update, rate)
        pyglet.clock.unschedule(self.on_update)
        pyglet.clock.schedule_interval(self.on_update, rate)

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

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        """ User moves the scroll wheel. """
        pass

    def set_mouse_visible(self, visible=True):
        """ If true, user can see the mouse cursor while it is over the window. Set false,
        the mouse is not visible. Default is true. """
        super().set_mouse_visible(visible)

    def on_key_press(self, symbol: int, modifiers: int):
        """ Override this function to add key press functionality. """
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        """ Override this function to add key release functionality. """
        pass

    def on_draw(self):
        """ Override this function to add your custom drawing code. """
        pass

    def on_resize(self, width, height):
        """ Override this function to add custom code to be called any time the window
        is resized. """
        viewport = self.get_viewport_size()
        width = max(1, viewport[0])
        height = max(1, viewport[1])
        gl.glViewport(0, 0, width, height)

    def set_min_size(self, width: float, height: float):
        """ Wrap the Pyglet window call to set minimum size

        Args:
            :width: width in pixels.
            :height: height in pixels.
        """

        if self._resizable:
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

        """

        if self._resizable:
            super().set_maximum_size(width, height)
        else:
            raise ValueError('Cannot set max size on non-resizable window')

    def set_size(self, width: float, height: float):
        """ Ignore the resizable flag and set the size """

        super().set_size(width, height)

    def get_size(self):
        """ Get the size of the window. """

        return super().get_size()

    def get_location(self) -> Tuple[int, int]:
        """ Return the X/Y coordinates of the window """

        return super().get_location()

    def set_visible(self, visible=True):
        """ Set if the window is visible or not. Normally, a program's window is visible.  """
        super().set_visible(visible)

    def set_viewport(self, left: Number, right: Number, bottom: Number, top: Number):
        """ Set the viewport. (What coordinates we can see.
        Used to scale and/or scroll the screen.) """
        set_viewport(left, right, bottom, top)

    def get_viewport(self) -> (float, float, float, float):
        """ Get the viewport. (What coordinates we can see.) """
        return get_viewport()

    def test(self, frames=10):
        """
        Used by unit test cases. Runs the event loop twice.
        :return:
        """
        for i in range(frames):
            self.switch_to()
            self.dispatch_events()
            self.dispatch_event('on_draw')
            self.flip()
            self.update(1/60)


def open_window(width: Number, height: Number, window_title: str, resizable: bool = False) -> pyglet.window.Window:
    """
    This function opens a window. For ease-of-use we assume there will only be one window, and the
    programmer does not need to keep a handle to the window. This isn't the best architecture, because
    the window handle is stored in a global, but it makes things easier for programmers if they don't
    have to track a window pointer.

    Args:
        :window_title: Title of the window.
        :width: Width of the window.
        :height: Height of the window.
        :resizable: Whether the window can be user-resizable.

    Returns:
        pyglet.window.Window
    """

    global _window
    _window = Window(width, height, window_title, resizable, update_rate=None)
    return _window