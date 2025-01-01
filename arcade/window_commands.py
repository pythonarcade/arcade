"""
This submodule has functions that control opening, closing, rendering,
and otherwise managing windows.
It also has commands for scheduling pauses and scheduling interval functions.
"""

from __future__ import annotations

import gc
import os
from typing import TYPE_CHECKING, Callable

import pyglet

from arcade.types import RGBA255, Color

if TYPE_CHECKING:
    from arcade import Window
    from arcade.application import View

_window: Window | None = None

__all__ = [
    "get_display_size",
    "get_window",
    "set_window",
    "close_window",
    "run",
    "exit",
    "start_render",
    "finish_render",
    "set_background_color",
    "schedule",
    "unschedule",
    "schedule_once",
]


def get_display_size(screen_id: int = 0) -> tuple[int, int]:
    """
    Return the width and height of a monitor.

    The size of the primary monitor is returned by default.

    Args:
        screen_id: The screen number
    Returns:
        Tuple containing the width and height of the screen
    """
    display = pyglet.display.Display()  # type: ignore  # pending: pyglet fixes import tricks
    screen = display.get_screens()[screen_id]
    return screen.width, screen.height


def get_window() -> "Window":
    """
    Return a handle to the current window.

    :return: Handle to the current window.
    """
    if _window is None:
        raise RuntimeError(
            ("No window is active. " "It has not been created yet, or it was closed.")
        )

    return _window


def set_window(window: Window | None) -> None:
    """
    Set a handle to the current window.

    Args:
        window: Handle to the current window.
    """
    global _window
    _window = window


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


def run(view: View | None = None) -> None:
    """
    Run the main loop. Optionally start with a specified view.

    After the window has been set up, and the event hooks are in place,
    this is usually one of the last commands on the main program.
    This is a blocking function starting pyglet's event loop meaning
    it will start to dispatch events such as ``on_draw`` and ``on_update``.

    Args:
        view: The view to display when starting the run. Defaults to None.
    """
    window = get_window()

    if view is not None:
        window.show_view(view)

    # Used in some unit test
    if os.environ.get("ARCADE_TEST"):
        window.on_update(1.0 / 60.0)
        window.on_draw()
    elif window.headless:
        # We are entering headless more an will emulate an event loop
        import time

        # Ensure the initial delta time is not 0 to be
        # more in line with how a normal window works.
        delta_time = window._draw_rate
        last_time = time.perf_counter()

        # As long as we have a context --
        while window.context:
            # Select active view or window
            active = window.current_view or window

            active.on_update(delta_time)
            if window.context:
                active.on_draw()

            # windwow could be closed in on_draw
            if window.context:
                window.flip()

            now = time.perf_counter()
            delta_time, last_time = now - last_time, now
    else:
        import sys

        if sys.platform != "win32":
            # For non windows platforms, just do pyglet run
            pyglet.app.run(window._draw_rate)
        else:
            # Ok, some Windows platforms have a timer resolution > 15 ms. That can
            # drop our FPS to 32 FPS or so. This reduces resolution so we can keep
            # FPS up.
            import contextlib
            import ctypes
            from ctypes import wintypes

            winmm = ctypes.WinDLL("winmm")

            class TIMECAPS(ctypes.Structure):
                _fields_ = (("wPeriodMin", wintypes.UINT), ("wPeriodMax", wintypes.UINT))

            def _check_time_err(err, func, args):
                if err:
                    raise WindowsError("%s error %d" % (func.__name__, err))
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
                pyglet.app.run(window._draw_rate)


def exit() -> None:
    """
    Exits the application.
    """
    pyglet.app.exit()


def start_render(pixelated=False, blend=True) -> None:
    """
    Start recording drawing functions into an offscreen buffer.
    Call :py:func:`arcade.finish_render` to stop recording. The
    start_render/finish_render calls can only be called once.

    When running Arcade this buffer will be presented to the screen.

    A few configuration options are available in this function.

    Args:
        pixelated:
            If True, the buffer will be be pixelated when resized.
            Otherwise, it will be smooth.
        blend:
            If alpha blending
    """
    from arcade.start_finish_data import StartFinishRenderData

    window = get_window()
    if window._start_finish_render_data is not None:
        raise RuntimeError(
            (
                "start_render() can only be called once during the application's lifetime "
                "and should only be used when calling draw functions at module level in "
                "a simple script to produce a static image. If you are seeing this error "
                "you likely intended to call clear() instead."
            )
        )

    window._start_finish_render_data = StartFinishRenderData(pixelated=pixelated, blend=blend)
    window._start_finish_render_data.begin()


def finish_render() -> None:
    """
    Stop recording drawing functions into an offscreen buffer.
    :py:func:`arcade.start_render` should be called before this function.

    :py:func:`arcade.run` can be called after this function to present the buffer.
    """
    window = get_window()
    if window._start_finish_render_data is None:
        raise RuntimeError("finish_render() was called without a matching start_render() call.")

    if window._start_finish_render_data.completed:
        raise RuntimeError("finish_render() was called more than once.")

    window._start_finish_render_data.end()


def set_background_color(color: RGBA255) -> None:
    """
    Set the color :py:meth:`arcade.Window.clear()` will use
    when clearing the window. This only needs to be called
    when the background color changes.

    .. Note::

        A shorter and faster way to set background color
        is using :py:attr:`arcade.Window.background_color`.

    Examples::

        # Use Arcade's built in color values
        arcade.set_background_color(arcade.color.AMAZON)

        # Specify RGB value directly (red)
        arcade.set_background_color((255, 0, 0))

    Args:
        color: List of 3 or 4 values in RGB/RGBA format.
    """
    get_window().background_color = Color.from_iterable(color)


def schedule(function_pointer: Callable, interval: float):
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

    Args:
        function_pointer:
            Pointer to the function to be called.
        interval:
            Interval to call the function (float or integer)
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

    Args:
        function_pointer: Pointer to the function to be unscheduled.
    """
    pyglet.clock.unschedule(function_pointer)


def schedule_once(function_pointer: Callable, delay: float):
    """
    Schedule a function to be automatically called once after ``delay``
    seconds. The function/callable needs to take a delta time argument
    similar to ``on_update``. This is a float representing the number
    of seconds since it was scheduled or called.

    Example::

        def some_action(delta_time):
            print(delta_time)

        # Call the function once after 1 second
        arcade.schedule_one(some_action, 1)

    Args:
        function_pointer:
            Pointer to the function to be called.
        delay:
            Delay in seconds
    """
    pyglet.clock.schedule_once(function_pointer, delay)
