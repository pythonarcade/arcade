"""
This submodule has functions that control opening, closing, rendering, and otherwise managing windows.
It also has commands for scheduling pauses and scheduling interval functions.
"""

import gc
import time
import os

import pyglet
import pyglet.gl as gl
from arcade.monkey_patch_pyglet import *

import numpy as np

from numbers import Number
from typing import Callable
from typing import Union
from arcade.arcade_types import Color

_left = -1
_right = 1
_bottom = -1
_top = 1
_scaling = None

_window = None

_projection = None
_opengl_context = None


def get_projection():
    """
    Returns the current projection.

    :return: Numpy array with projection.

    """
    return _projection


def create_orthogonal_projection(
        left,
        right,
        bottom,
        top,
        near,
        far,
        dtype=None
):
    """
    Creates an orthogonal projection matrix. Used internally with the
    OpenGL shaders.

    :param float left: The left of the near plane relative to the plane's centre.
    :param float right: The right of the near plane relative to the plane's centre.
    :param float top: The top of the near plane relative to the plane's centre.
    :param float bottom: The bottom of the near plane relative to the plane's centre.
    :param float near: The distance of the near plane from the camera's origin.
                       It is recommended that the near plane is set to 1.0 or above to avoid
                       rendering issues at close range.
    :param float far: The distance of the far plane from the camera's origin.
    :param dtype:
    :return: A projection matrix representing the specified orthogonal perspective.
    :rtype: numpy.array

    .. seealso:: http://msdn.microsoft.com/en-us/library/dd373965(v=vs.85).aspx
    """

    rml = right - left
    tmb = top - bottom
    fmn = far - near

    a = 2. / rml
    b = 2. / tmb
    c = -2. / fmn
    tx = -(right + left) / rml
    ty = -(top + bottom) / tmb
    tz = -(far + near) / fmn

    return np.array((
        (a, 0., 0., 0.),
        (0., b, 0., 0.),
        (0., 0., c, 0.),
        (tx, ty, tz, 1.),
    ), dtype=dtype)


def pause(seconds: Number):
    """
    Pause for the specified number of seconds. This is a convenience function that just calls time.sleep()

    :param float seconds: Time interval to pause in seconds.
    """
    time.sleep(seconds)


def get_window() -> Union[pyglet.window.Window, None]:
    """
    Return a handle to the current window.

    :return: Handle to the current window.
    """
    global _window
    return _window


def set_window(window: pyglet.window.Window):
    """
    Set a handle to the current window.

    :param Window window: Handle to the current window.
    """
    global _window
    _window = window

def get_scaling_factor(window):
    """
    Tries to get the scaling factor of the given Window. Currently works
    on MacOS only. Useful in figuring out what's going on with Retina and
    high-res displays.

    :param Window window: Handle to window we want to get scaling factor of.

    :return: Scaling factor. E.g., 2 would indicate scaled up twice.
    :rtype: int

    """
    from pyglet import compat_platform
    if compat_platform == 'darwin':
        from pyglet.libs.darwin.cocoapy import NSMakeRect
        view = window.context._nscontext.view()
        content_rect = NSMakeRect(0, 0, window._width, window._height)  # Get size, possibly scaled
        bounds = view.convertRectFromBacking_(content_rect)  # Convert to actual pixel sizes
        return int(content_rect.size.width / bounds.size.width)
    else:
        return 1

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

    :param Number left: Left-most (smallest) x value.
    :param Number right: Right-most (largest) x value.
    :param Number bottom: Bottom (smallest) y value.
    :param Number top: Top (largest) y value.
    """
    global _left
    global _right
    global _bottom
    global _top
    global _projection
    global _scaling

    _left = left
    _right = right
    _bottom = bottom
    _top = top

    # Needed for sprites
    if _scaling is None:
        _scaling = get_scaling_factor(_window)
    gl.glViewport(0, 0, _window.width * _scaling, _window.height * _scaling)

    # Needed for drawing
    # gl.glMatrixMode(gl.GL_PROJECTION)
    # gl.glLoadIdentity()
    # gl.glOrtho(_left, _right, _bottom, _top, -1, 1)
    # gl.glMatrixMode(gl.GL_MODELVIEW)
    # gl.glLoadIdentity()

    _projection = create_orthogonal_projection(left=_left, right=_right,
                                               bottom=_bottom, top=_top,
                                               near=-1000, far=100, dtype=np.float32)


def get_viewport() -> (float, float, float, float):
    """
    Get the current viewport settings.

    :return: Tuple of floats, with left, right, bottom, top

    """
    return _left, _right, _bottom, _top


def close_window():
    """
    Closes the current window, and then runs garbage collection. The garbage collection
    is necessary to prevent crashing when opening/closing windows rapidly (usually during
    unit tests).
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
    """
    global _window

    _window.flip()


def run():
    """
    Run the main loop.
    After the window has been set up, and the event hooks are in place, this is usually one of the last
    commands on the main program.
    """
    if 'ARCADE_TEST' in os.environ and os.environ['ARCADE_TEST'].upper() == "TRUE":
        # print("Testing!!!")
        window = get_window()
        if window:
            window.update(1/60)
            window.on_draw()
    else:
        pyglet.app.run()


def quick_run(time_to_pause: Number):
    """
    Only run the application for the specified time in seconds.
    Useful for unit testing or continuous integration (CI) testing
    where there is no user interaction.

    :param Number time_to_pause: Number of seconds to pause before automatically
         closing.

    """
    pause(time_to_pause)
    close_window()


def start_render():
    """
    Get set up to render. Required to be called before drawing anything to the
    screen.
    """
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    # gl.glMatrixMode(gl.GL_MODELVIEW)
    # gl.glEnableClientState(gl.GL_VERTEX_ARRAY)


def set_background_color(color: Color):
    """
    This specifies the background color of the window.

    :param Color color: List of 3 or 4 bytes in RGB/RGBA format.
    """

    gl.glClearColor(color[0]/255, color[1]/255, color[2]/255, 1)


def schedule(function_pointer: Callable, interval: Number):
    """
    Schedule a function to be automatically called every ``interval``
    seconds.

    :param Callable function_pointer: Pointer to the function to be called.
    :param Number interval: Interval to call the function.
    """
    pyglet.clock.schedule_interval(function_pointer, interval)
