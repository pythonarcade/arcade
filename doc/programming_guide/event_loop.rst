Event Loop
==========

Introduction
------------

Python Arcade provides a simple three event loop to build off.

:py:func:`on_draw`
    is provided to render to the window. After the ``on_draw`` event the
    window will present itself to the screen.  By default this attempts
    to occur every 1/60 seconds or rouch 16.7 milliseconds. This can be
    changed when initialising your :py:class:`arcade.Window` with the
    ``draw_rate`` argument. Setting the draw rate to a value above a
    screens refresh rate can cause tearing unless the ``vsync`` argument
    is set to true.

**TODO**: add note about camera state resetting once that's in

All three methods are exposed to be overridden in :py:class:`arcade.Window`
and :py:class:`arcade.View`. You may also register your own handlers
to these events using :py:func:`arcade.Window.push_handlers`, but this i

Time
====