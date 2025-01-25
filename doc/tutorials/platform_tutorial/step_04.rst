
.. _platformer_part_four:

Step 4 - Add User Control
-------------------------

Now we've got a character and a world for them to exist in, but what fun is a game if
you can't control the character and move around? In this Chapter we'll explore adding
keyboard input in Arcade.

First, at the top of our program, we'll want to add a new constant that controls how 
many pixels per update our character travels:

.. code-block::
    
    PLAYER_MOVEMENT_SPEED = 5

In order to handle the keyboard input, we need to add to add two new functions to our
Window class, ``on_key_press`` and ``on_key_release``. These functions will automatically
be called by Arcade whenever a key on the keyboard is pressed or released. Inside these
functions, based on the key that was pressed or released, we will move our character.

.. code-block::

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called whenever a key is released."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

In these boxes, we are modifying the ``change_x`` and ``change_y`` attributes on our
player Sprite. Changing these values will not actually perform the move on the Sprite.
In order to apply this change, we need to create a physics engine with our Sprite,
and update the physics engine every frame. The physics engine will then be responsible
for actually moving the sprite.

The reason we give the physics engine this responsibility instead of doing it ourselves,
is so that we can let the physics engine do collision detections, and allow/disallow a
movement based on the result. In later chapters, we'll use more advanced physics engines
which can do things like allow jumping with gravity, or climbing on ladders for example.

.. note::

    This method of tracking the speed to the key the player presses is simple, but
    isn't perfect. If the player hits both left and right keys at the same time,
    then lets off the left one, we expect the player to move right. This method won't
    support that. If you want a slightly more complex method that does, see
    :ref:`sprite_move_keyboard_better`.

Let's create a simple physics engine in our ``__init__`` function. We will do this by passing
it our player sprite, and the SpriteList containing our walls.

.. code-block::

    self.physics_engine = arcade.PhysicsEngineSimple(
        self.player_sprite, self.wall_list
    )

Now we have a physics engine, but we still need to update it every frame. In order to do this
we will add a new function to our Window class, called ``on_update``. This function is similar to
``on_draw``, it will be called by Arcade at a default of 60 times per second. It will also give
us a ``delta_time`` parameter that tells the amount of time between the last call and the current one.
This value will be used in some calculations in future chapters. Within this function, we will update
our physics engine. Which will process collision detections and move our player based on it's ``change_x``
and ``change_y`` values.

.. code-block::

    def on_update(self, delta_time):
        """Movement and Game Logic"""

        self.physics_engine.update()

At this point you should be able to run the game, and move the character around with the keyboard.
If the physics engine is working properly, the character should not be able to move through the ground
or the boxes.

For more information about the physics engine we are using in this tutorial,
see :py:class:`arcade.PhysicsEngineSimple`.

.. note::

    It is possible to have multiple physics engines, one per moving sprite. These
    are very simple, but easy physics engines. See
    :ref:`pymunk_platformer_tutorial` for a more advanced physics engine.

.. note::

    If you want to see how the collisions are checked, try using the ``draw_hit_boxes()`` function
    on the player and wall SpriteLists inside the ``on_draw`` function. This will show you what the
    hitboxes that the physics engine uses look like. 

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_user_control.py
    :caption: 04_user_control.py - User Control
    :linenos:
    :emphasize-lines: 13-17, 53, 65, 93-121

Run This Chapter
~~~~~~~~~~~~~~~~

.. code-block::

  python -m arcade.examples.platform_tutorial.04_user_control
