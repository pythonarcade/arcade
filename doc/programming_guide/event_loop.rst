Event Loop
==========

Introduction
------------

Python Arcade provides a simple three event loop to build off.

:py:func:`on_draw`
    is provided to render to the window. After the ``on_draw`` event, the window
    will draw to the screen. By default, this attempts to occur every 1/60 seconds
    or around 16.7 milliseconds. It can be changed when initialising your
    :py:class:`arcade.Window` with the ``draw_rate`` argument. Setting the draw rate
    to a value above a screen's refresh rate can cause tearing unless you set the
    ``vsync `` argument to true. We recommend keeping your ``draw_rate``around the
    screen's refresh rate.

:py:func:`on_update`
    is provided to update state which needs to happen at a roughly regular interval.
    The update event is not strictly paired to the draw event, but they share the same
    thread. This can cause a bottle-neck if one is significantly slower than the other.
    The event also provides a ``delta_time`` argument which is the time elapsed since the
    last ``on_update`` event. You can change the rate at which ``on_update`` is called with
    the ``update_rate`` argument when initialising your :py:class:`arcade.Window`.

:py:func:`on_fixed_update`
    is provided to update state which must happen with an exactly regular interval.
    Because Arcade can't ensure the event is actually fired regularly it stores how
    much time has passed since the last update, and once enough time has passed it
    releases an ``on_fixed_update`` call. The fixed update always provides the same
    ``delta_time`` argument. You can change the rate at which ``on__fixed_update`` is 
    called with the ``update_rate`` argument when initialising your :py:class:`arcade.Window`.

**TODO**: add note about camera state resetting once that's in

All three methods are exposed to be overridden in :py:class:`arcade.Window`
and :py:class:`arcade.View`. You may also register your own handlers
to these events using :py:func:`arcade.Window.push_handlers`, but this is
not recommended for beginners. 

Time
----