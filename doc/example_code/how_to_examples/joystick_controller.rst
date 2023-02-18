.. _example-code:

How to get connected controllers
===================
We can get a list of connected controllers by using :code:`arcade.get_joysticks()`.

.. code-block:: python

      joysticks = arcade.get_joysticks()
      if joysticks:
          self.joystick = joysticks[0]
          self.joystick.open()
      else:
          print("There are no joysticks.")
          self.joystick = None

Joystick Values
================
The hoystick values can be obtained by using :code:`self.joystick.x` and :code:`self.joystick.y`

How to use buttons
===================
How to use hatHow to use ranged triggers (like for acceleration)
=================================================================
Different types of controllers
==============================
How the (-1.0 to 1.0) range works
==================================
Deadzone
========
How-To Example Code
===================
