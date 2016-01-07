"""
This submodule has functions that control creating and managing windows.
"""

import sys

import OpenGL.GL as GL
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT

_left = -1
_right = 1
_bottom = -1
_top = 1

def set_resize_window_function(function_pointer):
    GLUT.glutReshapeFunc(function_pointer)


def default_resize_window_function(width, height):
    """ Called when the window is resized. """
    GL.glViewport(0, 0, width, height)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    ratio = width / height
    GL.glOrtho(_left * ratio, _right * ratio, _bottom, _top, -1, 1)
    print("resize({}, {}, {}, {})".format(_left * ratio, _right * ratio, _bottom, _top, -1, 1))


def set_ortho(left, right, bottom, top):
    global _left
    global _right
    global _bottom
    global _top

    _left = left
    _right = right
    _bottom = bottom
    _top = top
    print("set_ortho({}, {}, {}, {})".format(_left, _right, _bottom, _top, -1, 1))

def set_render_function(function_pointer):
    GLUT.glutDisplayFunc(function_pointer)


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
    >>> # Enable the following to keep the window up after running
    >>> # arcade.run()
    """
    GLUT.glutInit(sys.argv)
    GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE |
                             GLUT.GLUT_DEPTH)
    GLUT.glutInitWindowSize(width, height)
    GLUT.glutInitWindowPosition(0, 0)

    GLUT.glutCreateWindow(str.encode(window_title))

    GL.glClearColor(0.0, 0.0, 0.0, 0.0)
    GL.glClearDepth(1.0)
    GL.glDepthFunc(GL.GL_LEQUAL)
    GL.glEnable(GL.GL_DEPTH_TEST)

    # This will hopefully be replaced by something better later.
    GLUT.glutDisplayFunc(start_render)


def swap_buffers():
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
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running
    >>> # arcade.run()
    """

    GLUT.glutSwapBuffers()


def redisplay():
    """ Flag the screen that it needs to updated. """
    GLUT.glutPostRedisplay()


def run():
    """ Run the main loop. """
    GLUT.glutMainLoop()


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
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running
    >>> # arcade.run()
    """
    if len(color) == 4:
        alpha = color[3]
    elif len(color) == 3:
        alpha = 255

    GL.glClearColor(color[0]/255, color[1]/255, color[2]/255, alpha/255)
