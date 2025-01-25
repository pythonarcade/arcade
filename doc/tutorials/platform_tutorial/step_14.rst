.. _platformer_part_fourteen:

Step 14 - Multiple Levels
-------------------------

Now we will make it so that our game has multiple levels. For now we will just have two levels,
but this technique can be easily expanded to include more.

To start off, create two new variables in the ``__init__`` function to represent the position that marks
the end of the map, and what level we should be loading.

.. code-block::

    # Where is the right edge of the map?
    self.end_of_map = 0

    # Level number to load
    self.level = 1

Next in the ``setup`` function we will change the map loading call to use an f-string to load a map file
depending on the level variable we created.

.. code-block::

    # Load our TileMap
    self.tile_map = arcade.load_tilemap(f":resources:tiled_maps/map2_level_{self.level}.json", scaling=TILE_SCALING, layer_options=layer_options)

Again in the setup function, we will calculate where the edge of the currently loaded map is, in pixels. To do this
we get the width of the map, which is represented in number of tiles, and multiply it by the tile width. We also need to consider
the scaling of the tiles, because we are measuring this in pixels.

.. code-block::

    # Calculate the right edge of the map in pixels
    self.end_of_map = (self.tile_map.width * self.tile_map.tile_width) * self.tile_map.scaling

Now in the ``on_update`` function, we will add a block to check the player position against the end of the map value.
We will do this right before the ``center_camera_to_player`` function call at the end. This will increment our current level,
and leverage the ``setup`` function in order to re-load the game with the new level.

.. code-block::

    # Check if the player got to the end of the level
    if self.player_sprite.center_x >= self.end_of_map:
        # Advance to the next level
        self.level += 1

        # Reload game with new level
        self.setup()

If you run the game at this point, you will be able to reach the end of the first level and have the next level load and play through it.
We have two problems at this point, did you notice them? The first problem is that the player's score resets in between levels, maybe you
want this to happen in your game, but we will fix it here so that when switching levels we don't reset the score.

To do this, first add a new variable to the ``__init__`` function which will serve as a trigger to know if the score should be reset or not.
We want to be able to reset it when the player loses, so this trigger will help us only reset the score when we want to.

.. code-block::

    # Should we reset the score?
    self.reset_score = True

Now in the ``setup`` function we can replace the score reset with this block of code. We change the ``reset_score`` variable back to True
after resetting the score, because the default in our game should be to reset it, and we only turn off the reset when we want it off.

.. code-block::

    # Reset the score if we should
    if self.reset_score:
        self.score = 0
    self.reset_score = True

Finally, in the section of ``on_update`` that we advance the level, we can add this line to turn off the score reset

.. code-block::

    # Turn off score reset when advancing level
    self.reset_score = False

Now the player's score will persist between levels, but we still have one more problem. If you reach the end of the second level, the game crashes!
This is because we only actually have two levels available, but we are still trying to advance the level to 3 when we hit the end of level 2.

There's a few ways this can be handled, one way is to simply make more levels. Eventually you have to have a final level though, so this probably isn't
the best solution. As an exercise, see if you can find a way to gracefully handle the final level. You could display an end screen, or restart the game
from the beginning, or anything you want.

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/14_multiple_levels.py
    :caption: Moving the enemies
    :linenos:
    :emphasize-lines: 57-64, 79-80, 116-119, 173-182
