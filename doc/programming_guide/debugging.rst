.. _debugging:

Debugging
=========

Every game has bugs. This page covers the basic techniques for finding them,
from quick ``print`` statements to full debuggers, and how to check that your
setup is working before you ask for help.

.. contents::
    :local:
    :depth: 1


Print debugging
---------------

The quickest way to see what your code is doing is to print values to the
console. F-strings make this easy. Adding ``=`` after a name prints both the
name and the value:

.. code-block:: python

    def on_key_press(self, key, modifiers):
        print(f"{key=}, {modifiers=}")

Be careful when printing inside :meth:`~arcade.Window.on_update` or
:meth:`~arcade.Window.on_draw`. They run many times every second, so printing
there floods the console. Either print from event handlers, or only print every
so often:

.. code-block:: python

    def on_update(self, delta_time):
        self.frame_count += 1
        if self.frame_count % 60 == 0:
            print(f"{self.player_sprite.center_x=}")

Print debugging is simple and works everywhere. However, it only shows you what
you thought to print. For anything harder, use a debugger.


Use a debugger
--------------

A debugger is a tool that can pause your program while it is running. While it
is paused you can:

* see the values of all variables
* step through your code one line at a time
* run small pieces of code to test ideas

Most editors have a debugger built in:

* `Debugging Python in Visual Studio Code <https://code.visualstudio.com/docs/python/debugging>`_
* `Debugging in PyCharm <https://www.jetbrains.com/help/pycharm/debugging-your-first-python-application.html>`_

If you are working in a terminal, Python has a command line debugger. Put a
call to the built-in :py:func:`breakpoint` function where you want the program
to pause. See the `pdb documentation <https://docs.python.org/3/library/pdb.html>`_
for the commands it understands.

A few tips for debugging games:

* A breakpoint in :meth:`~arcade.Window.on_update` or
  :meth:`~arcade.Window.on_draw` is hit every frame. Put breakpoints in event
  handlers such as ``on_key_press`` instead, or use a conditional breakpoint
  that only triggers when something looks wrong.
* The game stops while it is paused. When you continue, the next
  ``delta_time`` can be very large because it includes the time you spent
  paused. That can make things like movement jump.


See what the game is doing
--------------------------

Some problems are easier to see than to print. Arcade has a few tools for that.

Hit boxes
^^^^^^^^^

If collisions don't behave the way you expect, draw the hit boxes. Both
:meth:`arcade.Sprite.draw_hit_box` and :meth:`arcade.SpriteList.draw_hit_boxes`
are meant for debugging:

.. code-block:: python

    def on_draw(self):
        self.clear()
        self.wall_list.draw()
        self.player_list.draw()

        # Slow. Only use these while debugging.
        self.wall_list.draw_hit_boxes(color=arcade.color.RED)
        self.player_list.draw_hit_boxes(color=arcade.color.RED)

Frame rate and timings
^^^^^^^^^^^^^^^^^^^^^^

If the game feels slow, measure before you change anything. Call
:func:`arcade.enable_timings` once at the start of your program. Then you can use
:func:`arcade.get_fps`, :func:`arcade.print_timings` and :class:`arcade.PerfGraph`
to see how long things take. See :ref:`performance_statistics_example` for a
complete example, and :ref:`performance` for common causes of slowdowns.


Check your setup
----------------

Some "bugs" are really problems with the environment, such as an old version of
Arcade or two different versions of a library installed at once. To see what you
are running, use::

    python -m arcade info

This prints the Arcade version along with your graphics device, Python version,
operating system and the pyglet and Pillow versions.

Arcade requires a specific version of pyglet. If you install another version
over it, you may see errors that are hard to explain. To get a clean start,
create a new virtual environment and install Arcade again.


Asking for help
---------------

If you are stuck, you can ask on the `Arcade Discord <https://discord.gg/ZjGDqMp>`_
or `open an issue on GitHub <https://github.com/pythonarcade/arcade/issues>`_.
You are more likely to get a quick answer if you include:

* the output of ``python -m arcade info``
* the full error message (the "traceback"), copied as text rather than a screenshot
* the smallest program that still shows the problem
