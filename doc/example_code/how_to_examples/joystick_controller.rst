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

Controllers have a strictly defined set of inputs. These inputs called buttons and are the following:

+---------------+-------------------------------------------------------+
| Button/Action | Notes                                                 |
+===============+=======================================================+
| A             | The “south” face button                               |
+---------------+-------------------------------------------------------+
| B             | The “east” face button                                |
+---------------+-------------------------------------------------------+
| X             | The “west” face button                                |
+---------------+-------------------------------------------------------+
| Y             | The “north” face button                               |
+---------------+-------------------------------------------------------+
| LeftShoulder  |                                                       |
+---------------+-------------------------------------------------------+
| RightShoulder |                                                       |
+---------------+-------------------------------------------------------+
| Start         | Called “options” on some controllers                  |
+---------------+-------------------------------------------------------+
| Back          | Called “select” or “share” on some controllers        |
+---------------+-------------------------------------------------------+
| Guide         | Usually in the center, with a company logo            |
+---------------+-------------------------------------------------------+
| LeftStick     | Pressing in on the left analog stick                  |
+---------------+-------------------------------------------------------+
| RightStick    | Pressing in on the right analog stick                 |
+---------------+-------------------------------------------------------+
| DPLeft        |                                                       |
+---------------+-------------------------------------------------------+
| DPRight       |                                                       |
+---------------+-------------------------------------------------------+
| DPUp          |                                                       |
+---------------+-------------------------------------------------------+
| DPDown        |                                                       |
+---------------+-------------------------------------------------------+

An event is dispatched when any of the values of the controllers are changed. These events can be handle like this:
.. code-block:: python

      @controller.event
      def on_button_press(controller, button_name):
          if button_name == 'a':
              # start firing
          elif button_name == 'b':
              # do something else
              
      @controller.event
      def on_button_release(controller, button_name):
          if button_name == 'a':
              # stop firing
          elif button_name == 'b':
              # do something else

How to use hat
==============================
Add the following code to the end of :code:`update`:
in this example, the :code:`on_stick_motion`
.. code-block:: python

    def on_stick_motion(self, controller, stick_name, x, y):
        """ Handle hat events """
        print(f"Movement on stick {stick_name}: ({x}, {y})")
Define an event handler function to 
==============================
How to use ranged triggers (like for acceleration)
=================================================================

Different types of controllers
==============================
Joystick hats are the directional pads on game controller. It allows you to move in eight directions (up, down, left, right and the diagonals).


==============================

The (-1.0 to 1.0) values on Controller
================= 
* The values will be between -1 and +1, with 0 being a centered joystick.
* The x-axis numbers will be negative if the stick goes left, positive for right.
* The y-axis numbers will be opposite of what you might expect. Negative for up, positive for down.

.. list-table:: joystick controller
   :widths: 25 25 50
   :header-rows: 1
   
   * - Left & Right
     - Centered
     - Up & Down
   * -   (-1, 1)
     -    0
     -   (-1, 1)


The joystick movements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. image:: joystickController.png
    :width: 400px
    :align: center
    :alt: Screenshot of controller movements

     
Deadzone
========
A centered joystick might have a value not at 0, but at 0.0001 or some small number. This will make for a small “drift” on a person’s character. We often counteract this by having a “dead zone” where if the number is below a certain value, we just assume it is zero to eliminate the drift.

How we take care of the dead zone:

After 

.. code-block:: console
      import arcade

add the following line at the top of the code to define a constant :code:`DEAD_ZONE` :

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


   
