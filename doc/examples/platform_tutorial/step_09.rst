
.. _platformer_part_nine:

Step 9 - Multiple Levels and Other Layers
-----------------------------------------

Here's an expanded example:

* This adds foreground, background, and "Don't Touch" layers.

  * The background tiles appear behind the player
  * The foreground appears in front of the player
  * The Don't Touch layer will reset the player to the start (228-237)

* The player resets to the start if they fall off the map (217-226)
* If the player gets to the right side of the map, the program attempts to load another layer

  * Add ``level`` attribute (69-70)
  * Updated ``setup`` to load a file based on the level (76-144, specifically lines 77 and 115)
  * Added end-of-map check(245-256)

.. literalinclude:: ../../../arcade/examples/platform_tutorial/09_endgame.py
    :caption: More Advanced Example
    :linenos:
    :emphasize-lines: 69-70, 77, 114-115, 248-259

.. note::

    What else might you want to do?

    * :ref:`sprite_enemies_in_platformer`
    * :ref:`sprite_face_left_or_right`
    * Bullets (or something you can shoot)

      * :ref:`sprite_bullets`
      * :ref:`sprite_bullets_aimed`
      * :ref:`sprite_bullets_enemy_aims`

    * Add :ref:`sprite_explosion_bitmapped`
    * Add :ref:`sprite_move_animation`
