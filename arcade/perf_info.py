"""
Utility functions to keep performance information
"""
import collections
from typing import Dict

import pyglet
import time

# Evil globals
_timings: Dict = {}
_pyglets_dispatch_event = None
_frame_times: collections.deque = collections.deque()
_max_history: int = 100


def _dispatch_event(self, *args):
    """
    Dispatch event function that will be monkey-patched over Pyglet's dispatch event function.
    """
    # Name of the dispatched event, like 'on_draw'
    name = args[0]

    # Start the clock, and keep the time if this is on_draw for FPS calcs.
    start_time = time.perf_counter()
    if name == 'on_draw':
        _frame_times.append(start_time)

    # Call Pyglet's dispatch event function
    _pyglets_dispatch_event(self, *args)

    # Stop the clock
    end_time = time.perf_counter()
    processing_time = end_time - start_time

    # Get the historical list of timings, or create one if we don't have it.
    if name in _timings:
        data = _timings[name]
    else:
        data = collections.deque()
        _timings[name] = data

    # Add out time to the list
    data.append(processing_time)

    # Past out history limit? Pop off the first one on the list
    if len(data) > _max_history:
        data.popleft()


def print_timings():
    """
    This prints to stdout a table of the most recent dispatched events and
    their average time.

    The table looks something like:

    .. code-block:: text

        Event          Count Average Time
        -------------- ----- ------------
        update            60       0.0553
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


def clear_timings():
    """
    Clear the dispatch event timing table created after :func:`arcade.enable_timings` is called.
    """
    global _timings
    _timings = {}


def get_timings() -> Dict:
    """
    Get a table with the dispatch event timings.
    """
    return _timings


def enable_timings(max_history: int = 100):
    """
    Enable the saving of performance information.
    """
    global _pyglets_dispatch_event, _max_history

    if _pyglets_dispatch_event is not None:
        raise ValueError("Timings already enabled.")

    _pyglets_dispatch_event = pyglet.window.BaseWindow.dispatch_event
    pyglet.window.BaseWindow.dispatch_event = _dispatch_event
    _max_history = max_history


def disable_timings():
    """
    Turn off the collection of timing information started by :func:`arcade.enable_timings`.
    """
    global _pyglets_dispatch_event

    if _pyglets_dispatch_event is None:
        raise ValueError("Timings are not enabled.")

    # Restore the original pyglet dispatch event function
    pyglet.window.BaseWindow.dispatch_event = _dispatch_event
    _pyglets_dispatch_event = None

    clear_timings()


def get_fps(frame_count: int = 60) -> float:
    """
    Get the current FPS.
    :func:`arcade.enable_timings` must be called before getting the FPS.

    :param int frame_count: How many frames to look at to get FPS. So 30, would give you
                            average FPS over the last 30 frames.
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


def timings_enabled():
    """
    Return true if timings are enabled, false otherwise. See :func:`arcade.enable_timings`.
    """
    return _pyglets_dispatch_event is not None
