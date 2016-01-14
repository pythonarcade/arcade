"""
This submodule has functions that control creating and managing windows.
"""

import sys

import pyglet
import pyglet.gl as GL
import pyglet.gl.glu as GLU

_left = -1
_right = 1
_bottom = -1
_top = 1

_window = None


def get_window():
    global _window
    return _window

def set_window(window):
    global _window
    _window = window

def set_viewport(left, right, bottom, top):
    """
    This sets what coordinates appear on the window.
    """
    global _left
    global _right
    global _bottom
    global _top

    _left = left
    _right = right
    _bottom = bottom
    _top = top

    # GL.glViewport(0, 800, 0, 800)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GL.glOrtho(left, right, bottom, top, -1, 1)


def open_window(window_title, width, height):
    """
    This function opens a window.

    Args:
        :window_title (str): Title of the window.
        :width (int): Width of the window.
        :height (int): Height of the window.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.pause(0.5)
    >>> arcade.close_window()
    """
    global _window

    window = pyglet.window.Window(width=width, height=height,
                                  caption=window_title)
    set_viewport(0, width, 0, height)
    window.invalid = False

    _window = window


def close_window():
    global _window

    _window.close()


def finish_render():
    """
    Swap buffers and display what has been drawn.

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
    >>> arcade.pause(0.5)
    >>> arcade.close_window()
    """
    global _window

    _window.flip()


def run():
    """ Run the main loop. """
    pyglet.app.run()


def start_render():
    """ Get set up to render. """
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glMatrixMode(GL.GL_MODELVIEW)


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
    >>> arcade.pause(0.5)
    >>> arcade.close_window()
    """

    GL.glClearColor(color[0]/255, color[1]/255, color[2]/255, 1)

