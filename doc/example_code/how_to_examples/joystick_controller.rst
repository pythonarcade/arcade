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
The joystick values can be obtained by using :code:`self.joystick.x` and :code:`self.joystick.y`. This can be used to update the current positon of an object.
def update(self, delta_time):

.. code-block:: python

    # Update the position according to the game controller
    if self.joystick:
        print(self.joystick.x, self.joystick.y)

        self.object.change_x = self.joystick.x
        self.object.change_y = -self.joystick.y

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
A centered joystick might have a value not at 0, but at 0.0001 or some small number. This will make for a small “drift” on a person’s character. We often counteract this by having a “dead zone” where if the number is below a certain value, we just assume it is zero to eliminate the drift.

How we take care of the dead zone:

After 

.. code-block:: console

    import arcade

add the following line:

.. code-block:: console

    DEAD_ZONE = 0.02


and adding the following code to the :code:`update`:

.. code-block:: python

    def update(self, delta_time):

            # Update the position according to the game controller
            if self.joystick:

                # Set a "dead zone" to prevent drive from a centered joystick
                if abs(self.joystick.x) < DEAD_ZONE:
                    self.object.change_x = 0
                else:
                    self.object.change_x = self.joystick.x * MOVEMENT_SPEED

                # Set a "dead zone" to prevent drive from a centered joystick
                if abs(self.joystick.y) < DEAD_ZONE:
                    self.object.change_y = 0
                else:
                    self.object.change_y = -self.joystick.y * MOVEMENT_SPEED

How-To Example Code
===================
