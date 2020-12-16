
.. _platformer_part_seven:

Step 7 - Display The Score
--------------------------

Now that we can collect coins and get points,
we need a way to display the score on the screen.

This is a bit more complex
than just drawing the score at the same x, y location every time because
we have to "scroll" the score right with the player if we have a scrolling
screen. To do this, we just add in the ``view_bottom`` and ``view_left`` coordinates.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/07_score.py
    :caption: Display The Score
    :linenos:
    :emphasize-lines: 55-56, 71-72, 129-132, 170-171

.. note::

    You might also want to add:

    * A count of how many coins are left to be collected.
    * Number of lives left.
    * A timer: :ref:`timer`
    * This example shows how to add an FPS timer: :ref:`stress_test_draw_moving`

Explore On Your Own
~~~~~~~~~~~~~~~~~~~

* Practice creating your own layout with different tiles.
* Add background images. See :ref:`sprite_collect_coins_background`
* Add moving platforms. See :ref:`sprite_moving_platforms`
* Change the character image based on the direction she is facing.
  See :ref:`sprite_face_left_or_right`
* Add instruction and game over screens.
