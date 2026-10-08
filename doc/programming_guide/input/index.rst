.. _pg_input:

Input Handling
==============

Arcade has a number of different options for handling input, but they fall into two main categories:

:ref:`The Simple Way <pg_simple_input>`: This is what you will generally see used in most of Arcade's example code. This way
of working is mostly directly talking with the underlying windowing library, and can work fine for keyboard/mouse
but starts to require a lot of manual work when you want more complex systems, especially when making extensive use
of controllers or mixing different types of input devices(like supporting both keyboard/mouse and controllers).

:ref:`The Advanced Way <pg_advanced_input>`: This is where the advanced input system comes in. The advanced input system provides a very rigidly defined but much more
capable interface for handling input. This system allows defining custom actions, which can be linked to multiple different
input sources(for example a keypress or a button on a controller can trigger the same action). It also supports things like
joystick input from controllers, has utilities for switching between input devices, and more. While this system is more
capable, it has more boilerplate to get started with, and is less flexible than the simple one if you want to build your own
system for input on top of something.


.. toctree::
   :maxdepth: 1

   simple_input
   advanced_input