
.. _platformer_part_eight:

Step 8 - Display The Score
--------------------------

Now that we can collect coins and get points, we need a way to display the score on the screen.

This process is a little bit more complex than just drawing some text at an X and Y location.
For properly drawing text, or any GUI elements, we need to use a separate camera than the one
we use to draw the rest of our scene.

This is because we are scrolling around the main game camera, but we want our GUI elements to
stay still. Using a second camera lets us do this.

As an example, if we were not to use a second camera, and instead draw on the same camera as
our scene. We would need to offset the position that we draw our text at by position of the
camera. This might be easier if you're only displaying one thing, but if you have a lot of GUI
elements this could get out of hand.

First start by creating the new GUI camera and the score variables in the ``__init__`` function.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/08_score.py
    :caption: Display The Score - The init method
    :lines: 44-48

Then we can initialize them in the ``setup`` function. We reset the score to 0 here because this
function is intended to fully reset the game back to it's starting state.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/08_score.py
    :caption: Display The Score - The setup method
    :lines: 62-66

Then in our ``on_draw`` function we can first draw our scene like normal, and then switch to the
GUI camera, and then finally draw our text.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/08_score.py
    :caption: Display The Score - The on_draw method
    :lines: 110-133
    :emphasize-lines: 13-24
  
Lastly in the ``on_update`` function we just need to update the score when a player collects a coin:

.. literalinclude:: ../../../arcade/examples/platform_tutorial/08_score.py
    :caption: Display The Score - The on_update method
    :lines: 179-186
    :emphasize-lines: 7-8

.. note::

    You might also want to add:

    * A count of how many coins are left to be collected.
    * Number of lives left.
    * A timer: :ref:`timer`
    * This example shows how to add an FPS timer: :ref:`stress_test_draw_moving`

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/08_score.py
    :caption: Display The Score
    :linenos:
    :emphasize-lines: 44-48, 62-66, 122-133, 186
