"""
This submodule has functions that control opening, closing, rendering, and otherwise managing windows.
It also has commands for scheduling pauses and scheduling interval functions.
"""

import gc
import time
import os

import pyglet
import numpy as np

from numbers import Number
from typing import (
    Callable,
    cast,
    Tuple,
    Union
)
from arcade.arcade_types import Color

_window = None


def get_display_size(screen_id: int = 0) -> Tuple[int, int]:
    """Return the width and height of a monitor.

    The size of the primary monitor is returned by default.

    :param int screen_id: The screen number
    :return: Tuple containing the width and height of the screen
    :rtype: tuple
    """
    display = pyglet.canvas.Display()
    screen = display.get_screens()[screen_id]
    return screen.width, screen.height


def get_projection():
    """
    Returns the current projection matrix used by sprites and shapes in arcade.

    This is a shortcut for ```window.ctx.projection_2d_matrix``.

    :return: Numpy array with projection.
    """
    return get_window().ctx.projection_2d_matrix


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

    :param float left: The left of the near plane relative to the plane's center.
    :param float right: The right of the near plane relative to the plane's center.
    :param float top: The top of the near plane relative to the plane's center.
    :param float bottom: The bottom of the near plane relative to the plane's center.
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
    ), dtype=dtype or 'f4')


def pause(seconds: Number):
    """
    Pause for the specified number of seconds. This is a convenience function that just calls time.sleep()

    :param float seconds: Time interval to pause in seconds.
    """
    time.sleep(cast(float, seconds))


def get_window() -> pyglet.window.Window:
    """
    Return a handle to the current window.

    :return: Handle to the current window.
    """
    if _window is None:
        raise RuntimeError("No window is active. Use set_window() to set an active window")

    return _window


def set_window(window: pyglet.window.Window):
    """
    Set a handle to the current window.

    :param Window window: Handle to the current window.
    """
    global _window
    _window = window


def get_scaling_factor(window=None) -> float:
    """
    Gets the scaling factor of the given Window.
    This is the ratio between the window and framebuffer size.
    If no window is supplied the currently active window will be used.

    :param Window window: Handle to window we want to get scaling factor of.

    :return: Scaling factor. E.g., 2 would indicate scaled up twice.
    :rtype: float
    """
    if window:
        return window.get_pixel_ratio()
    else:
        return get_window().get_pixel_ratio()


def set_viewport(left: float, right: float, bottom: float, top: float):
    """
    This sets what coordinates the window will cover.

    By default, the lower left coordinate will be ``(0, 0)`` and the top y
    coordinate will be the height of the window in pixels, and the right x
    coordinate will be the width of the window in pixels.

    If a program is making a game where the user scrolls around a larger
    world, this command can help out.

    Note: It is recommended to only set the view port to integer values that
    line up with the pixels on the screen. Otherwise if making a tiled game
    the blocks may not line up well, creating rectangle artifacts.

    Note: Window.on_resize will call set_viewport by default. If you set your
    own custom viewport, you may need to over-ride this method.

    For more advanced users: This functions sets the orthogonal projection
    used by shapes and sprites using the values passed in. it also
    updates the viewport to match the current screen resolution.
    ```window.ctx.projection_2d`` and ``window.ctx.viewport```
    can be used to set viewport and projection separately.

    :param Number left: Left-most (smallest) x value.
    :param Number right: Right-most (largest) x value.
    :param Number bottom: Bottom (smallest) y value.
    :param Number top: Top (largest) y value.
    """
    window = get_window()
    fbo = window.ctx.fbo
    # If the window framebuffer is active we should apply pixel scale
    if fbo.is_default:
        scaling = get_scaling_factor(window)
        fbo.viewport = 0, 0, int(window.width * scaling), int(window.height * scaling)
    # otherwise it's an offscreen framebuffer not needing pixel scale
    else:
        fbo.viewport = 0, 0, *fbo.size

    window.ctx.projection_2d = left, right, bottom, top


def get_viewport() -> Tuple[float, float, float, float]:
    """
    Get the current viewport settings.

    :return: Tuple of floats, with ``(left, right, bottom, top)``

    """
    return get_window().ctx.projection_2d


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
    get_window().flip()


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
            window.on_update(1/60)
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
    get_window().clear()


def set_background_color(color: Color):
    """
    Specifies the background color of the window. This value
    will persist for every future screen clears until changed.

    :param Color color: List of 3 or 4 bytes in RGB/RGBA format.
    """
    get_window().background_color = color


def schedule(function_pointer: Callable, interval: Number):
    """
    Schedule a function to be automatically called every ``interval``
    seconds.

    :param Callable function_pointer: Pointer to the function to be called.
    :param Number interval: Interval to call the function.
    """
    pyglet.clock.schedule_interval(function_pointer, interval)


def unschedule(function_pointer: Callable):
    """
    Unschedule a function being automatically called.

    :param Callable function_pointer: Pointer to the function to be unscheduled.
    """
    pyglet.clock.unschedule(function_pointer)
