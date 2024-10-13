Event Loop
==========

Introduction
------------

Python Arcade provides three simple methods to integrate with the event loop.
All three methods are exposed to be overridden in :py:class:`arcade.Window`
and :py:class:`arcade.View`. For advanced use cases it is possible to add own
handler via :py:func:`arcade.Window.push_handlers`.

:py:func:`on_draw`
^^^^^^^^^^^^^^^^^^
provides a hook to render to the window. After the ``on_draw`` event, the window
will draw to the screen. By default, this attempts to occur every 1/60 seconds
or once every 16.7 milliseconds. It can be changed when initializing your
:py:class:`arcade.Window` with the ``draw_rate`` argument. Setting the draw rate
to a value above a screen's refresh rate can cause tearing unless you set the
``vsync`` argument to true. We recommend keeping your ``draw_rate`` around the
screen's refresh rate. After every draw event camera state will be reset. 
This means that non-default cameras must be reused on every draw event.

:py:func:`on_update`
^^^^^^^^^^^^^^^^^^^^
provides a hook to update state which needs to happen at a roughly regular interval.
The update event is not strictly paired to the draw event, but they share the same
thread. This can cause a bottle-neck if one is significantly slower than the other.
The event also provides a ``delta_time`` argument which is the time elapsed since the
last ``on_update`` event. You can change the rate at which ``on_update`` is called with
the ``update_rate`` argument when initialising your :py:class:`arcade.Window`.

:py:func:`on_fixed_update`
^^^^^^^^^^^^^^^^^^^^^^^^^^
provides a hook to update state which must happen with an exactly regular interval.
Because Arcade can't ensure the event is actually fired regularly it stores how
much time has passed since the last update, and once enough time has passed it
releases an ``on_fixed_update`` call. The fixed update always provides the same
``delta_time`` argument. You can change the rate at which ``on__fixed_update`` is 
called with the ``fixed_rate`` argument when initialising your :py:class:`arcade.Window`.

Time
----
While the underlying library, pyglet, provide a clock for scheduling events it is closely tied
to the window's own events. For simple time keeping Arcade provides global
clock objects. Both clocks can be imported from ``arcade.clock`` as 
``GLOBAL_CLOCK`` and ``GLOBAL_FIXED_CLOCK``

:py:class:`arcade.Clock`
^^^^^^^^^^^^^^^^^^^^^^^^
The base Arcade clock tracks the elapsed time in seconds, the total number
of clock ticks, and the amount of time that elapsed since the last tick.
The currently active window automatically ticks the ``GLOBAL_CLOCK`` every ``on_update``.
This means there is no reason to manually tick it. If you need more
clocks, possibly ticking at a different rate, an :py:class:`arcade.Clock`
can be created on the fly.

:py:class:`arcade.FixedClock`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The fixed clock tracks the same values as the normal clock, but has two special features.
Firstly it enforces that the ``delta_time`` passed into its ``tick`` method is always the same.
This is because advanced physics engines require consistent time. Secondly the fixed clock
requires a sibling regular clock. It uses this clock to track how offset from the true time it is.
Like the regular clock you may make a new :py:class:`arcade.FixedClock` at any time,
but ensure they have a sibling.

Up Coming
^^^^^^^^^
In future version of arcade :py:class:`Clock` will be updated to allow for sub clocks. 
Sub clocks will be ticked by their parent clock rather than be manually updated. Sub clocks
will make it easier to control the flow of time for specific groups of objects. Such as only
slowing enemies or excluding UI elements. To gain access to a draft :py:class:`arcade.Clock`
you can find it in ``arcade.future.sub_clock``. This version of the sub clock is not final.
If you find any bugs do not hesitate to raise an issue on the github.

More on Fixed update
--------------------
The ``on_fixed_update`` event can be an extremely powerful tool, but it has many complications
that should be taken into account. If used imporperly the event can grind a game to a halt.

Death Spiral
^^^^^^^^^^^^
A fixed update represents a very specific amount of time. If all of the computations take
longer than the fixed update represents than the ammount of time accumulated between update
events will grow. If this happens for multiple frames the game will begin to spiral. The 
first few frames of the spiral will lead to one update cycle requiring two fixed update
calls. This will increase the extra time accumulated until three fixed updates must occur at once.
This will continue to happen until either: the fixed updates start taking less time, or the game 
crashes.

There are a few solutions to this issue. The simplist method, which works best when there may be spikes in
computation time that quickly settle, is to clamp the max number of fixed updates that can occur in a single
frame. In Arcade this is done by setting the ``fixed_frame_cap`` argument when initialising your
:py:class:`arcade.Window`. The second method is to slow-down time temporarily. By changing the
``_tick_speed`` of Arcade's ``GLOBAL_CLOCK`` is is possible to slow down the accumulation of time.
For example setting ``GLOBAL_CLOCK._tick_speed = 0.5`` would allow the fixed update twice as many frames
to calculate for.

Update Interpolation
^^^^^^^^^^^^^^^^^^^^
Because fixed updates work on the accumulation of time this may not sync with 
the ``on_draw`` or ``on_update`` events. In extreme cases this can cause a visible stuttering to
objects moved within ``on_fixed_update``. To prevent this, ``GLOBAL_FIXED_CLOCK`` provides
the ``accumulated`` and ``fraction``properties. By storing the last frame's position information it is possible
to use ``fraction`` to interpolate towards the next calculated positions. For a visual representation of 
this effect look at ``arcade.examples.fixed_update_interpolation``.

Vertical Synchronization
------------------------

What is vertical sync?
^^^^^^^^^^^^^^^^^^^^^^

Vertical synchronization (vsync) is a window option in which the
video card is prevented from doing anything visible to the display
memory until after the monitor finishes its current refresh cycle.

To enable vsync in Arcade::

    # On window creation
    arcade.Window(800, 600, "Window Title", vsync=True)

    # While the application is running
    window.set_vsync(True)

This have advantages and disadvantages depending on the situation.

Most windows are what we call "double buffered". This means
the window actually has two surfaces. A visible surface and a 
hidden surface. All drawing commands will end up in the
hidden surface. When we're done drawing our frame the hidden
and visible surfaces swap places and the new frame is revealed
to the user.

If this "dance" of swapping surfaces is not timed correctly 
with your monitor you might experience small hiccups in movement
or `screen tearing <https://en.wikipedia.org/wiki/Screen_tearing>`_.

Vertical sync disabled as a default
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Arcade window is by default created with vertical sync
disabled. This is a much safer default for
a number of reasons.

* In some environments vertical sync is capped to 30 fps.
  This can make the game run at half the speed if ``delta_time``
  is not accounted for. We don't expect beginners take
  ``delta_time`` into consideration in their projects.
* If threads are used all threads will stall while the
  application is waiting for vertical sync

We cannot guarantee that vertical sync is disabled if
this is enforced on driver level. The vast amount of
driver defaults lets the application control this.