"""
This submodule has functions that control creating and managing windows.
"""

import sys
import time
import gc

import pyglet

import pyglet.gl as GL
import pyglet.gl.glu as GLU

_left = -1
_right = 1
_bottom = -1
_top = 1

_window = None


def pause(seconds):
    """
    Pause for the specified number of seconds.

    >>> import arcade
    >>> arcade.pause(0.25) # Pause 1/2 second

    """
    time.sleep(seconds)


def get_window():
    """
    Return a handle to the current window.

    Args:
        None
    Returns:
        :window: Handle to the current window.
    Raises:
        None
    """
    global _window
    return _window


def set_window(window):
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


def set_viewport(left, right, bottom, top):
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

    # GL.glViewport(0, 0, _window.height, _window.height)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GL.glOrtho(_left, _right, _bottom, _top, -1, 1)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()


def open_window(window_title, width, height):
    """
    This function opens a window.

    Args:
        :window_title: Title of the window.
        :width: Width of the window.
        :height: Height of the window.
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
                                  caption=window_title)
    set_viewport(0, width, 0, height)
    window.invalid = False

    _window = window


def close_window():
    """
    Closes the current window, and then runs garbage collection.

    Args:
        None
    Returns:
        None
    Raises:
        None

    Example:
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

    Args:
        None
    Returns:
        None
    Raises:
        None

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

    Args:
        None
    Returns:
        None
    Raises:
        None

    Example:
    """
    pyglet.app.run()


def _close(dt):
    close_window()


def quick_run(time_to_pause):
    """
    Only run the app for the specified time in seconds.
    Useful for testing.

    Args:
        :time_to_pause: Number of seconds to pause before automatically
         closing.
    Returns:
        None
    Raises:
        None

    Example:
    """
    # pyglet.clock.schedule_once(_close, time_to_pause)
    # pyglet.app.run()
    pause(time_to_pause)
    close_window()


def start_render():
    """
    Get set up to render. Required to be called before drawing anything to the
    screen.

    Args:
        None
    Returns:
        None
    Raises:
        None
    """
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)


def set_background_color(color):
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

    GL.glClearColor(color[0]/255, color[1]/255, color[2]/255, 1)


def schedule(function_pointer, interval):
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
