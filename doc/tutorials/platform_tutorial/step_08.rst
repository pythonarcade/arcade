.. _platformer_part_eight:

Step 8 - Collecting Coins
-------------------------

Now that we can fully move around our game, we need to give the player an objective. A classic
goal in video games is collecting coins, so let's go ahead and add that.

In this chapter you will learn how to check for collisions with our player, and find out exactly
what they collided with and do something with it. For now we will just remove the coin from the
screen when they collect it, but in later chapters we will give the character a score, and add to
it when they collect a coin. We will also start playing sounds later.

First off we will create a new SpriteList to hold our coins. Exactly like our other spritelist for
walls, go ahead and add a variable to the ``__init__`` function to store it, and then initialize it
inside the ``setup`` function. We will want to turn on spatial hashing for this list for now. If you
decided to have moving coins, you would want to turn that off.

.. code-block::

    # Inside __init__
    self.coin_list = None

    # Inside setup
    self.coin_list = arcade.SpriteList(use_spatial_hash=True)

See if you can experiment with a way to add the coins to the SpriteList using what we've already learned.
The built-in resource for them is ``:resources:images/items/coinGold.png``. HINT: You'll want to scale these
just like we did with our boxes and ground. If you get stuck, you can check the full source code below to
see how we've placed them following the same pattern we used for the ground.

Once you have placed the coins and added them to the ``coin_list``, don't forget to add them to ``on_draw``.

.. code-block::

    self.coin_list.draw()

Now that we're drawing our coins to the screen, how do we make them interact with the player? When the player
hits one, we want to remove it from the screen. To do this we will use :func:`arcade.check_for_collision_with_list` function.
This function takes a single Sprite, in this instance our player, and a SpriteList, for us, the coins. It will return
a list containing all of the Sprites from the given SpriteList that the Sprite collided with.

We can iterate over that list with a for loop to do something with each sprite that had a collision. This means
we can detect the user hitting multiple coins at once if we had them placed close together.

In order to do this, and remove the coin sprites when the player hits them, we will add this to the ``on_update`` function.

.. code-block::

    coin_hit_list = arcade.check_for_collision_with_list(
        self.player_sprite, self.coin_list
    )

    for coin in coin_hit_list:
        coin.remove_from_sprite_lists()

We use this :func:`arcade.BasicSprite.remove_from_sprite_lists` function in order to ensure our Sprite is completely
removed from all SpriteLists it was a part of. 

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/08_coins.py
    :caption: Collecting Coins
    :linenos:
    :emphasize-lines: 15, 50-51, 68, 90-95, 125, 133-141

Run This Chapter
~~~~~~~~~~~~~~~~

.. code-block::

  python -m arcade.examples.platform_tutorial.08_coins
