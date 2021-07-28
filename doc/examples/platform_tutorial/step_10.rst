
.. _platformer_part_ten:

Step 10 - Multiple Levels and Other Layers
------------------------------------------

Here's an expanded example:

* This adds foreground, background, and "Don't Touch" layers.

  * The background tiles appear behind the player
  * The foreground appears in front of the player
  * The Don't Touch layer will reset the player to the start (218-231)

* The player resets to the start if they fall off the map (207-216)
* If the player gets to the right side of the map, the program attempts to load another layer

  * Add ``level`` attribute (73-74)
  * Updated ``setup`` to load a file based on the level (81-101, specifically lines 81 and 85)
  * Added end-of-map check(233-244)

.. literalinclude:: ../../../arcade/examples/platform_tutorial/10_multiple_levels.py
    :caption: More Advanced Example
    :linenos:
    :emphasize-lines: 73-74, 81, 84-85, 233-244

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

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/10_multiple_levels.py
    :caption: Multiple Levels
    :linenos:

..
    * :ref:`10_multiple_levels`
    * :ref:`10_multiple_levels_diff`