
.. _platformer_part_four:

Step 4 - Add User Control
-------------------------

Now we need to be able to get the user to move around.

First, at the top of the program add a constant that controls how many pixels
per update our character travels:

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_user_control.py
    :caption: 04_user_control.py - Player Move Speed Constant
    :lines: 15-16

Next, at the end of our ``setup`` method, we need to create a physics engine that will
move our player and keep her from running through walls. The ``PhysicsEngineSimple``
class takes two parameters: The moving
sprite, and a list of sprites the moving sprite can't move through.

For more information about the physics engine we are using in this tutorial,
see :py:class:`arcade.PhysicsEngineSimple`.

.. note::

    It is possible to have multiple physics engines, one per moving sprite. These
    are very simple, but easy physics engines. See
    :ref:`pymunk_platformer_tutorial` for a more advanced physics engine.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_user_control.py
    :caption: 04_user_control.py - Create Physics Engine
    :lines: 73-76

Each sprite has ``center_x`` and ``center_y`` attributes. Changing these will
change the location of the sprite. (There are also attributes for top, bottom,
left, right, and angle that will move the sprite.)

Each sprite has ``change_x`` and ``change_y`` variables. These can be used to
hold the velocity that the sprite is moving with. We will adjust these
based on what key the user hits. If the user hits the right arrow key
we want a positive value for ``change_x``. If the value is 5, it will move
5 pixels per frame.

In this case, when the user presses a key we'll change the sprites change x and y.
The physics engine will look at that, and move the player unless she'll hit a wall.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_user_control.py
    :caption: 04_user_control.py - Handle key-down
    :linenos:
    :pyobject: MyGame.on_key_press

On releasing the key, we'll put our speed back to zero.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_user_control.py
    :caption: 04_user_control.py - Handle key-up
    :linenos:
    :pyobject: MyGame.on_key_release

.. note::

    This method of tracking the speed to the key the player presses is simple, but
    isn't perfect. If the player hits both left and right keys at the same time,
    then lets off the left one, we expect the player to move right. This method won't
    support that. If you want a slightly more complex method that does, see
    :ref:`sprite_move_keyboard_better`.

Our ``on_update`` method is called about 60 times per second. We'll ask the physics
engine to move our player based on her ``change_x`` and ``change_y``.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_user_control.py
    :caption: 04_user_control.py - Update the sprites
    :linenos:
    :pyobject: MyGame.on_update

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_user_control.py
    :caption: 04_user_control.py - User Control
    :linenos:
    :emphasize-lines: 15-16, 35-36, 73-76, 87-115
