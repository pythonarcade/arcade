"""
Utility functions to keep performance information
"""

import time
from collections import deque

import pyglet

# Evil globals
_timings: dict[str, deque[float]] = {}
_pyglets_dispatch_event = None
_frame_times: deque = deque()
_max_history: int = 100

__all__ = [
    "print_timings",
    "clear_timings",
    "get_timings",
    "enable_timings",
    "disable_timings",
    "get_fps",
    "timings_enabled",
]


def _dispatch_event(self, *args) -> None:
    """
    This function will be monkey-patched over Pyglet's dispatch event function.
    """
    # Name of the dispatched event, like 'on_draw'
    name = args[0]

    # Start the clock, and keep the time if this is on_draw for FPS calcs.
    start_time = time.perf_counter()
    if name == "on_draw":
        _frame_times.append(start_time)

    # Call Pyglet's dispatch event function
    if _pyglets_dispatch_event is not None:
        _pyglets_dispatch_event(self, *args)

    # Stop the clock
    end_time = time.perf_counter()
    processing_time = end_time - start_time

    # Get the historical list of timings, or create one if we don't have it.
    if name in _timings:
        data = _timings[name]
    else:
        data = deque()
        _timings[name] = data

    # Add out time to the list
    data.append(processing_time)

    # Past out history limit? Pop off the first one on the list
    if len(data) > _max_history:
        data.popleft()


def print_timings() -> None:
    """
    Print event handler statistics to stdout as a table.

    Performance tracking must be enabled with
    :func:`arcade.enable_timings` before calling this function.

    See :ref:`performance_statistics_example` for an example of how to
    use function.

    The statistics consist of:

    * how many times each registered event was called
    * the average time for handling each type of event in seconds

    The table looks something like:

    .. code-block:: text

        Event          Count Average Time
        -------------- ----- ------------
        on_update         60       0.0000
        on_mouse_enter     1       0.0000
        on_mouse_motion   39       0.0000
        on_expose          1       0.0000
        on_draw           60       0.0020
    """
    global _timings
    print()
    print("Event          Count Average Time")
    print("-------------- ----- ------------")
    for index in _timings:
        data = _timings[index]

        call_count = len(data)
        average_time = sum(data) / len(data)
        print(f"{index:15}{call_count:5}  {average_time:11.4f}")


def clear_timings() -> None:
    """
    Reset the count & average time for each event type to zero.

    Performance tracking must be enabled with
    :func:`arcade.enable_timings` before calling this function.

    See :ref:`performance_statistics_example` for an example of how to
    use function.
    """
    global _timings
    _timings = {}


def get_timings() -> dict[str, deque[float]]:
    """
    Get a dict of the current dispatch event timings.

    Performance tracking must be enabled with
    :func:`arcade.enable_timings` before calling this function.

    :return: A dict of event timing data, consisting of counts and
             average handler duration.
    """
    return _timings


def enable_timings(max_history: int = 100) -> None:
    """
    Enable recording of performance information.

    This function must be called before using any other performance
    features, except for :func:`arcade.timings_enabled`, which can
    be called at any time.

    See :ref:`performance_statistics_example` for an example of how to
    use function.

    Args:
        max_history:
            How many frames to keep performance info for.
    """
    global _pyglets_dispatch_event, _max_history

    if pyglet.window.BaseWindow.dispatch_event == _dispatch_event:
        raise ValueError("Timings already enabled.")

    # Save the original pyglet dispatch event function
    _pyglets_dispatch_event = pyglet.window.BaseWindow.dispatch_event

    # Override the pyglet dispatch event function
    pyglet.window.BaseWindow.dispatch_event = _dispatch_event  # type: ignore
    _max_history = max_history


def disable_timings() -> None:
    """
    Disable collection of timing information.

    Performance tracking must be enabled with
    :func:`arcade.enable_timings` before calling this function.
    """
    if pyglet.window.BaseWindow.dispatch_event != _dispatch_event:
        raise ValueError("Timings are not enabled.")

    # Restore the original pyglet dispatch event function
    pyglet.window.BaseWindow.dispatch_event = _pyglets_dispatch_event  # type: ignore

    clear_timings()


def get_fps(frame_count: int = 60) -> float:
    """
    Get the FPS over the last ``frame_count`` frames.

    Performance tracking must be enabled with
    :func:`arcade.enable_timings` before calling this function.

    To get the FPS over the last 30 frames, you would pass 30 instead
    of the default 60.

    See :ref:`performance_statistics_example` for an example of how to
    use function.

    Args:
        frame_count: How many frames to calculate the FPS over.
    """
    cur_time = time.perf_counter()
    if len(_frame_times) == 0:
        return 0
    if len(_frame_times) < frame_count:
        frame_count = len(_frame_times)

    start_time = _frame_times[-frame_count]
    total_time = cur_time - start_time
    fps = frame_count / total_time
    return fps


def timings_enabled() -> bool:
    """
    Return true if timings are enabled, false otherwise.

    This function can be used at any time to check if timings are
    enabled. See :func:`arcade.enable_timings` for more information.

    :return: Whether timings are currently enabled.
    """
    return pyglet.window.BaseWindow.dispatch_event == _dispatch_event
