"""
This submodule has functions that control opening, closing, rendering, and otherwise managing windows.
It also has commands for scheduling pauses and scheduling interval functions.
"""

import gc
import time
import os

import pyglet

from numbers import Number
from typing import (
    Callable,
    Optional,
    cast,
    Tuple,
    TYPE_CHECKING
)
from arcade.arcade_types import Color
from pyglet.math import Mat4

if TYPE_CHECKING:
    from arcade import Window


_window: Optional["Window"] = None


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


def get_projection() -> Mat4:
    """
    Returns the current projection matrix used by sprites and shapes in arcade.

    This is a shortcut for ```window.ctx.projection_2d_matrix``.

    :return: Projection matrix
    :rtype: Mat4
    """
    return get_window().ctx.projection_2d_matrix


def create_orthogonal_projection(
        left,
        right,
        bottom,
        top,
        near=1,
        far=-1,
) -> Mat4:
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
    :return: A projection matrix representing the specified orthogonal perspective.
    :rtype: Mat4

    .. seealso:: https://msdn.microsoft.com/en-us/library/dd373965(v=vs.85).aspx
    """
    return Mat4.orthogonal_projection(left, right, bottom, top, near, far)


def pause(seconds: Number) -> None:
    """
    Pause for the specified number of seconds. This is a convenience function that just calls time.sleep()

    :param float seconds: Time interval to pause in seconds.
    """
    time.sleep(cast(float, seconds))


def get_window() -> "Window":
    """
    Return a handle to the current window.

    :return: Handle to the current window.
    """
    if _window is None:
        raise RuntimeError("No window is active. Use set_window() to set an active window")

    return _window


def set_window(window: "Window") -> None:
    """
    Set a handle to the current window.

    :param Window window: Handle to the current window.
    """
    global _window
    _window = window


def get_scaling_factor(window: "Window" = None) -> float:
    """
    Gets the scaling factor of the given Window.
    This is the ratio between the window and framebuffer size.
    If no window is supplied the currently active window will be used.

    :param Window window: Handle to window we want to get scaling factor of.

    :return: Scaling factor. E.g., 2.0 would indicate the framebuffer
             width and height being 2.0 times the window width and height.
             This means one "window pixel" is actual a 2 x 2 square of pixels
             in the framebuffer.
    :rtype: float
    """
    if window:
        return window.get_pixel_ratio()
    else:
        return get_window().get_pixel_ratio()


def set_viewport(left: float, right: float, bottom: float, top: float) -> None:
    """
    This sets what coordinates the window will cover.

    .. tip:: Beginners will want to use :py:class:`~arcade.Camera`.
             It provides easy to use support for common tasks
             such as screenshake and movement to a destination.

    If you are making a game with complex control over the viewport,
    this function can help.

    By default, the lower left coordinate will be ``(0, 0)``, the top y
    coordinate will be the height of the window in pixels, and the right x
    coordinate will be the width of the window in pixels.

    .. warning:: Be careful of fractional or non-multiple values!

        It is recommended to only set the viewport to integer values that
        line up with the pixels on the screen. Otherwise, tiled pixel art
        may not line up well during render, creating rectangle artifacts.

    .. note:: ``Window.on_resize`` calls ``set_viewport`` by default.
              If you want to set your own custom viewport during the
              game, you may need to over-ride this function.

    **For more advanced users**: This functions sets the orthogonal projection
    used by shapes and sprites. It also updates the viewport to match the current
    screen resolution.
    ``window.ctx.projection_2d`` (:py:meth:`~arcade.ArcadeContext.projection_2d`)
    and ``window.ctx.viewport`` (:py:meth:`~arcade.gl.Context.viewport`)
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


def close_window() -> None:
    """
    Closes the current window, and then runs garbage collection. The garbage collection
    is necessary to prevent crashing when opening/closing windows rapidly (usually during
    unit tests).
    """
    global _window

    if _window is None:
        return

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
    get_window().static_display = True
    get_window().flip_count = 0
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
            window.on_update(1 / 60)
            window.on_draw()
    else:
        import sys
        if sys.platform != 'win32':
            # For non windows platforms, just do pyglet run
            pyglet.app.run()
        else:
            # Ok, some Windows platforms have a timer resolution > 15 ms. That can
            # drop our FPS to 32 FPS or so. This reduces resolution so we can keep
            # FPS up.
            import contextlib
            import ctypes
            from ctypes import wintypes

            winmm = ctypes.WinDLL('winmm')

            class TIMECAPS(ctypes.Structure):
                _fields_ = (('wPeriodMin', wintypes.UINT),
                            ('wPeriodMax', wintypes.UINT))

            def _check_time_err(err, func, args):
                if err:
                    raise WindowsError('%s error %d' % (func.__name__, err))
                return args

            winmm.timeGetDevCaps.errcheck = _check_time_err
            winmm.timeBeginPeriod.errcheck = _check_time_err
            winmm.timeEndPeriod.errcheck = _check_time_err

            @contextlib.contextmanager
            def timer_resolution(msecs=0):
                caps = TIMECAPS()
                winmm.timeGetDevCaps(ctypes.byref(caps), ctypes.sizeof(caps))
                msecs = min(max(msecs, caps.wPeriodMin), caps.wPeriodMax)
                winmm.timeBeginPeriod(msecs)
                yield
                winmm.timeEndPeriod(msecs)

            with timer_resolution(msecs=10):
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


def exit():
    """
    Exits the application.
    """
    pyglet.app.exit()


def start_render() -> None:
    """
    Clears the window. Can also be replaced with :py:meth:`~arcade.Window.clear`.
    """
    get_window().clear()


def set_background_color(color: Color) -> None:
    """
    Specifies the background color of the window. This value
    will persist for every future screen clears until changed.

    :param Color color: List of 3 or 4 bytes in RGB/RGBA format.
    """
    get_window().background_color = color


def schedule(function_pointer: Callable, interval: Number):
    """
    Schedule a function to be automatically called every ``interval``
    seconds. The function/callable needs to take a delta time argument
    similar to ``on_update``. This is a float representing the number
    of seconds since it was scheduled or called.

    A function can be scheduled multiple times, but this is not recommended.

    .. Warning:: Scheduled functions should **always** be unscheduled
                 using :py:func:`arcade.unschedule`. Having lingering
                 scheduled functions will lead to crashes.

    Example::

        def some_action(delta_time):
            print(delta_time)

        # Call the function every second
        arcade.schedule(some_action, 1)
        # Unschedule

    :param Callable function_pointer: Pointer to the function to be called.
    :param Number interval: Interval to call the function (float or integer)
    """
    pyglet.clock.schedule_interval(function_pointer, interval)


def unschedule(function_pointer: Callable):
    """
    Unschedule a function being automatically called.

    Example::

        def some_action(delta_time):
            print(delta_time)

        arcade.schedule(some_action, 1)
        arcade.unschedule(some_action)

    :param Callable function_pointer: Pointer to the function to be unscheduled.
    """
    pyglet.clock.unschedule(function_pointer)
