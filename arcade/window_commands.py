"""
This submodule has functions that control opening, closing, rendering, and otherwise managing windows.
It also has commands for scheduling pauses and scheduling interval functions.
"""

import gc
import time

import pyglet

import pyglet.gl as gl

from numbers import Number
from typing import Callable
from typing import List
from typing import Union

_left = -1
_right = 1
_bottom = -1
_top = 1

_window = None


def pause(seconds: Number):
    """
    Pause for the specified number of seconds. This is a convenience function that just calls time.sleep()

    :param float seconds: Time interval to pause in seconds.
    :return: None
    :raises: None

    >>> import arcade
    >>> arcade.pause(0.25) # Pause 1/2 second

    """
    time.sleep(seconds)


def get_window() -> Union[pyglet.window.Window, None]:
    """
    Return a handle to the current window.

    :param: None
    :return window: Handle to the current window.
    :raises: None

    """
    global _window
    return _window


def set_window(window: pyglet.window.Window):
    """
    Set a handle to the current window.

    Args:
        :window: Handle to the current window.
    Returns:
        None
    Raises:
        None
    """
    global _window
    _window = window


def set_viewport(left: Number, right: Number, bottom: Number, top: Number):
    """
    This sets what coordinates the window will cover.

    By default, the lower left coordinate will be (0, 0) and the top y
    coordinate will be the height of the window in pixels, and the right x
    coordinate will be the width of the window in pixels.

    If a program is making a game where the user scrolls around a larger
    world, this command can help out.

    Note: It is recommended to only set the view port to integer values that
    line up with the pixels on the screen. Otherwise if making a tiled game
    the blocks may not line up well, creating rectangle artifacts.

    Args:
        :left: Left-most (smallest) x value.
        :right: Right-most (largest) x value.
        :bottom: Bottom (smallest) y value.
        :top: Top (largest) y value.
    Returns:
        None
    Raises:
        None

    :Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> set_viewport(-1, 1, -1, 1)
    >>> arcade.quick_run(0.25)

    """
    global _left
    global _right
    global _bottom
    global _top

    _left = left
    _right = right
    _bottom = bottom
    _top = top

    # gl.glViewport(0, 0, _window.height, _window.height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(_left, _right, _bottom, _top, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()


def open_window(window_title: str, width: Number, height: Number, resizable: bool = False):
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
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.quick_run(0.25)
    """
    global _window

    window = pyglet.window.Window(width=width, height=height,
                                  caption=window_title,
                                  resizable=resizable)
    set_viewport(0, width, 0, height)
    window.invalid = False

    _window = window


def close_window():
    """
    Closes the current window, and then runs garbage collection. The garbage collection
    is necessary to prevent crashing when opening/closing windows rapidly (usually during
    unit tests).

    :param: None
    :return: None
    :raises: None

    """
    global _window

    _window.close()
    _window = None

    # Have to do a garbage collection or Python will crash
    # if we do a lot of window open and closes. Like for
    # unit tests.
    gc.collect()


def finish_render():
    """
    Swap buffers and displays what has been drawn.
    If programs use derive from the Window class, this function is
    automatically called.

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.RED)
    >>> arcade.start_render()
    >>> # All the drawing commands go here
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    global _window

    _window.flip()


def run():
    """
    Run the main loop.
    After the window has been set up, and the event hooks are in place, this is usually one of the last
    commands on the main program.
    """
    pyglet.app.run()


def quick_run(time_to_pause: Number):
    """
    Only run the application for the specified time in seconds.
    Useful for unit testing or continuous integration (CI) testing
    where there is no user interaction.

    Args:
        :time_to_pause: Number of seconds to pause before automatically
         closing.
    Returns:
        None
    Raises:
        None

    Example:
    """
    pause(time_to_pause)
    close_window()


def start_render():
    """
    Get set up to render. Required to be called before drawing anything to the
    screen.
    """
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)


def set_background_color(color: List[int]):
    """
    This specifies the background color of the window.

    Args:
        :color (tuple): List of 3 or 4 bytes in RGB/RGBA format.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.RED)
    >>> arcade.start_render()
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    gl.glClearColor(color[0]/255, color[1]/255, color[2]/255, 1)


def schedule(function_pointer: Callable, interval: Number):
    """
    Schedule a function to be automatically called every ``interval``
    seconds.

    Args:
        :function_pointer: Pointer to the function to be called.
        :interval: Interval to call the function.
    Returns:
        None
    Raises:
        None
    """
    pyglet.clock.schedule_interval(function_pointer, interval)
