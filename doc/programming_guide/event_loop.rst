Event Loop
==========

Introduction
------------

Python Arcade provides a simple three event loop to build off. All three methods are exposed to be overridden in :py:class:`arcade.Window`
and :py:class:`arcade.View`. You may also register your own handlers
to these events using :py:func:`arcade.Window.push_handlers`, but this is
not recommended for beginners.

:py:func:`on_draw`
^^^^^^^^^^^^^^^^^^
is provided to render to the window. After the ``on_draw`` event, the window
will draw to the screen. By default, this attempts to occur every 1/60 seconds
or once every 16.7 milliseconds. It can be changed when initializing your
:py:class:`arcade.Window` with the ``draw_rate`` argument. Setting the draw rate
to a value above a screen's refresh rate can cause tearing unless you set the
``vsync`` argument to true. We recommend keeping your ``draw_rate`` around the
screen's refresh rate. After every draw event camera state will be reset. 
This means that non-default cameras must be reused on every draw event.

:py:func:`on_update`
^^^^^^^^^^^^^^^^^^^^
is provided to update state which needs to happen at a roughly regular interval.
The update event is not strictly paired to the draw event, but they share the same
thread. This can cause a bottle-neck if one is significantly slower than the other.
The event also provides a ``delta_time`` argument which is the time elapsed since the
last ``on_update`` event. You can change the rate at which ``on_update`` is called with
the ``update_rate`` argument when initialising your :py:class:`arcade.Window`.

:py:func:`on_fixed_update`
^^^^^^^^^^^^^^^^^^^^^^^^^^
is provided to update state which must happen with an exactly regular interval.
Because Arcade can't ensure the event is actually fired regularly it stores how
much time has passed since the last update, and once enough time has passed it
releases an ``on_fixed_update`` call. The fixed update always provides the same
``delta_time`` argument. You can change the rate at which ``on__fixed_update`` is 
called with the ``fixed_rate`` argument when initialising your :py:class:`arcade.Window`.

Time
----
While pyglet does provide a clock for scheduling events it is closely tied
to the window's own events. For simple time keeping arcade provides global
clock objects. Both clocks can be imported from ``arcade.clock`` as 
``GLOBAL_CLOCK`` and ``GLOBAL_FIXED_CLOCK``

:py:class:`arcade.Clock`
^^^^^^^^^^^^^^^^^^^^^^^^
The base arcade clock tracks the elapsed time in seconds, the total number
of clock ticks, and the amount of time that elapsed since the last tick.
The currently active window automatically ticks the ``GLOBAL_CLOCK`` every ``on_update``.
This means there is no reason to manually tick it. If you need more
clocks, possibly ticking at a different rate, an :py:class:`arcade.Clock`
can be created on the fly.

:py:class:`arcade.FixedClock`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The fixed clock tracks the same values as the normal clock, but has two special features.
Firstly it inforces that the ``delta_time`` passed into its ``tick`` method is always the same.
This is because advanced physics engines require consistent time. Secondly the fixed clock
requires a sibling regular clock. It uses this clock to track how offset from the true time it is.
Like the regular clock you may make a new :py:class:`arcade.FixedClock` at any time,
but ensure they have a sibling.

Up Coming
^^^^^^^^^
In future versions of arcade there will be a :py:class:`arcade.SubClock`. The sub clock will
provide many useful features currently missing from regular and fixed clocks. Sub clocks are 
ticked by their parent clock. This means you won't need to manually tick clocks created at runtime.
Sub clocks will also allow for time manipulation by changing how fast they see time flow. This
allows you to easily create slow-down effects without any advanced maths or changing the number of 
updates per frame. To gain access to a draft :py:class:`arcade.SubClock` you can find it in
``arcade.future.sub_clock``. This version of the sub clock is not final. If you find any bugs do
not hesitate to raise an issue on the github.

More on Fixed update
--------------------
the ``on_fixed_update`` event can be an extremelly powerful tool, but it has many complications
that should be accounted for. If used imporperly the event can grind a game to a halt.

Death Spiral
^^^^^^^^^^^^
A fixed update represnts a very specific amount of time. If all of the computations take
longer than the fixed update represents than the ammount of time accumulated between update
events will grow. If this happens for multiple frames the game will begin to spiral. The 
first few frames of the spiral will lead to one update cycle requiring two fixed update
calls. This will increase the extra time accumulated until three fixed updates must occur at once.
This will continue to happen until either: the fixed updates start taking less time, or the game 
crashes.

There are a few solutions to this issue. The simplist method, which works best when there may be spikes in
computation time that quickly settle, is to clamp the max number of fixed updates that can occur in a single
frame. In arcade this is done by setting the ``fixed_frame_cap`` argument when initialising your
:py:class:`arcade.Window`. The second method is to slow-down time temporarily. By changing the
``_tick_speed`` of arcade's ``GLOBAL_CLOCK`` is is possible to slow down the accumulation of time.
For example setting ``GLOBAL_CLOCK._tick_speed = 0.5`` would allow the fixed update twice as many frames
to calculate for.

Update Interpolation
^^^^^^^^^^^^^^^^^^^^
Because fixed updates work on the accumulation of time this may not sync with the perfectly with 
the ``on_draw`` or ``on_update`` events. In extreme cases this can cause a visible stuttering to
objects moved within ``on_fixed_update``. This is where the ``accumulated`` and ``fraction`` properties
on ``GLOBAL_FIXED_CLOCK`` come into play. By storing the last frame's position information it is possible
to use ``fraction`` to interpolate towards the next calculated positions. For a visual representation of 
this effect look at the ``arcade.examples.fixed_update_interpolation``. Paired with slowing down time when
computations get expensive allows for a much smoother game experience at the cost of code complexity.

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