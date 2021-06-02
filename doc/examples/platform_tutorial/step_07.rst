
.. _platformer_part_seven:

Step 7 - Add Coins And Sound
----------------------------

.. image:: listing_07.png
    :width: 70%

The code below adds coins that we can collect. It also adds a sound to be played
when the user hits a coin, or presses the jump button.

We check to see if the user hits a coin by the ``arcade.check_for_collision_with_list``
function. Just pass the player sprite, along with a ``SpriteList`` that holds
the coins. In this example, we retrieve that ``SpriteList`` from our scene.
The function returns a list of coins in contact with the player sprite.
If no coins are in contact, the list is empty.

The method ``Sprite.remove_from_sprite_lists`` will remove that sprite from all
lists, and effectively the game.

Notice that any transparent "white-space" around the image counts as the hitbox.
You can trim the space in a graphics editor, or in the second section,
we'll show you how to specify the hitbox.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/07_coins_and_sound.py
    :caption: Add Coins and Sound
    :linenos:
    :emphasize-lines: 52-54, 95-100, 122, 142-152

.. note::

    Spend time placing the coins where you would like them.
    If you have extra time, try adding more than just coins. Also add gems or keys
    from the graphics provided.

    You could also subclass the coin sprite and add an attribute for a score
    value. Then you could have coins worth one point, and gems worth 5, 10, and
    15 points.

Source Code
~~~~~~~~~~~

* :ref:`07_coins_and_sound`
* :ref:`07_coins_and_sound_diff`
