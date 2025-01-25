.. _platformer_part_nine:

Step 9 - Adding Sound
---------------------

Our game has a lot of graphics so far, but doesn't have any sound yet. Let's change that!
In this chapter we will add a sound when the player collects the coins, as well as when they jump.

Loading and playing sounds in Arcade is very easy. We will only need two functions for this:

* :func:`arcade.load_sound`
* :func:`arcade.play_sound`

In our ``__init__`` function, we will add these two lines to load our coin collection and jump sounds.

.. code-block::

    self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
    self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

.. note::

    Why are we not adding empty variables to ``__init__`` and initializing them in ``setup`` like
    our other objects?

    This is because sounds are a static asset within our game. If we reset the game, the sounds don't
    change, so it's not worth re-loading them.

Now we can play these sounds by simple adding the ``play_sound`` function wherever we want them to occur.
Let's add one alongside our removal of coins in the ``on_update`` function.

.. code-block::

    # Within on_update
    for coin in coin_hit_list:
        coin.remove_from_sprite_lists()
        arcade.play_sound(self.collect_coin_sound)

This will play a sound whenever we collect a coin. We can add a jump sound by adding this to our ``UP`` block
for jumping in the ``on_key_press`` function:

.. code-block::

    # Within on_key_press
    if key == arcade.key.UP or key == arcade.key.W:
        if self.physics_engine.can_jump():
            self.player_sprite.change_y = PLAYER_JUMP_SPEED
            arcade.play_sound(self.jump_sound)

Now we will also have a sound whenever we jump.

Documentation for :class:`arcade.Sound`

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/09_sound.py
    :caption: Load the Map
    :linenos:
    :emphasize-lines: 56-58, 146, 160

Run This Chapter
~~~~~~~~~~~~~~~~

.. code-block::

  python -m arcade.examples.platform_tutorial.09_sound
