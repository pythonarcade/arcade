

.. _platformer_part_five:

Step 5 - Add Gravity
--------------------

The previous example is great for top-down games, but what if it is a side view with
jumping like our platformer? We need to add gravity. First, let's define a 
constant to represent the acceleration for gravity, and one for a jump speed.

.. code-block::

    GRAVITY = 1
    PLAYER_JUMP_SPEED = 20

Now, let's change the Physics Engine we created in the ``__init__`` function to a 
:class:`arcade.PhysicsEnginePlatformer` instead of a :class:`arcade.PhysicsEngineSimple`.
This new physics engine will handle jumping and gravity for us, and will do even more
in later chapters.

.. code-block::
    
    self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.player_sprite, walls=self.wall_list, gravity_constant=GRAVITY
    )

This is very similar to how we created the original simple physics engine, with two exceptions.
The first being that we have sent it our gravity constant. The second being that we have explicitly
sent our wall SpriteList to the ``walls`` parameter. This is a very important step. The platformer
physics engine has two parameters for collidable objects, one named ``platforms`` and one named ``walls``.

The difference is that objects sent to ``platforms`` are intended to be moved. They are moved in the same 
way the player is, by modifying their ``change_x`` and ``change_y`` values. Objects sent to the
``walls`` parameter will not be moved. The reason this is so important is that non-moving walls have much
faster performance than movable platforms.

Adding static sprites via the ``platforms`` parameter is roughly an O(n) operation, meaning performance will
linearly get worse as you add more sprites. If you add your static sprites via the ``walls`` parameter, then
it is nearly O(1) and there is essentially no difference between for example 100 and 50,000 non-moving sprites.

Lastly we will give our player the ability to jump. Modify the ``on_key_press`` and ``on_key_release`` functions.
We'll remove the up/down statements we had before, and make ``UP`` jump when pressed.

.. code-block::

    if key == arcade.key.UP or key == arcade.key.W:
        if self.physics_engine.can_jump():
            self.player_sprite.change_y = PLAYER_JUMP_SPEED

The ``can_jump()`` check from our physics engine will make it so that we can only jump if we are touching the
ground. You can remove this function to allow jumping in mid-air for some interesting results. Think about how
you might implement a double-jump system using this.

.. note::

    You can change how the user jumps by changing the gravity and jump constants.
    Lower values for both will make for a more "floaty" character. Higher values make
    for a faster-paced game. 

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/05_add_gravity.py
    :caption: 05_add_gravity.py - Add Gravity
    :linenos:
    :emphasize-lines: 18-19, 72-81, 105-123

Run This Chapter
~~~~~~~~~~~~~~~~

.. code-block::

  python -m arcade.examples.platform_tutorial.05_add_gravity
