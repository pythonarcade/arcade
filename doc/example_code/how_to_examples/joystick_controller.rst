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

.. code-block:: python

    def update(self, delta_time):
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

==============================

How the (-1.0 to 1.0) range works
=================
This is the direction or intensity of joystick movement on a game.  

The joystick movements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. image:: joystickController.png
    :width: 400px
    :align: center
    :alt: Screenshot of controller movements

Values (-1 to 1)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table:: joystick controller
   :widths: 25 25 50
   :header-rows: 1
   
   * - Left & Right
     - Centered
     - Down & Up
   * -   (-1, 1)
     -    0
     -   (-1, 1)

     


   
