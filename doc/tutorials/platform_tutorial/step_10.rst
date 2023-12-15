
.. _platformer_part_ten:

Step 10 - Adding a Score
------------------------

Our game is starting to take shape, but we still need to give the player a reward for their hard work
collecting coins. To do this we will add a score which will be increased everytime they collect a coin,
and display that on the screen.

In this chapter we will cover using :class:`arcade.Text` objects, as well as a technique for using two cameras
to draw objects in "screen space" and objects in "world space".

.. note::

    What is screen space and world space? Think about other games you may have played, and let's compare it to
    our game. A player moves around in the world, and we scroll a camera around based on that position. This is
    an example of "world space" coordinates. They can expand beyond our window and need to be positioned within
    the window accordingly. 

    An example of "screen space" coordinates is our score indicator. We will draw this on our screen, but we don't
    want it to move around the screen when the camera scrolls around. To achieve this we will use two different cameras,
    and move the world space camera, but not move the screen space camera.

    In our code, we will call this screen space camera, ``gui_camera``

Let's go ahead and add a variable for our new camera and initialize it in ``setup``. We will also add a variable for
our score. This will just be an integer initially set to 0. We will set this in both ``__init__`` and ``setup``.

.. code-block::

    # Within __init__
    self.gui_camera = None
    self.score = 0

    # Within setup
    self.gui_camera = arcade.SimpleCamera(viewport=(0, 0, width, height))
    self.score = 0

Now we can go into our ``on_update`` function, and when the player collects a coin, we can increment our score variable.
For now we will give the player 75 points for collecting a coin. You can change this, or as an exercise try adding different
types of coins with different point values. In later chapters we'll explore dynamically providing point values for coins from
a map editor.

.. code-block::

    # Within on_update
    for coin in coin_hit_list:
        coin.remove_from_sprite_lists()
        arcade.play_sound(self.collect_coin_sound)
        self.score += 75

Now that we're incrementing our score, how do we draw it onto the screen? Well we will be using our GUI camera, but so far we haven't
talked about drawing Text in Arcade. There are a couple of ways we can do this in Arcade, the first way is using the
:func:`arcade.draw_text` function. This is a simple function that you can put directly in ``on_draw`` to draw a string of text.

This function however, is not very performant, and there is a better way. We will instead use :class:`arcade.Text` objects. These have many
advantages, like not needing to re-calculate the text everytime it's drawn, and also can be batch drawn much like how we do with Sprite and SpriteList.
We will explore batch drawing Text later.

For now, let's create an :class:`arcade.Text` object to hold our score text. First create the empty variable in ``__init__`` and initialize in ``setup``.

.. code-block::

    # Within __init__
    self.score_text = None

    # Within setup
    self.score_text = arcade.Text(f"Score: {self.score}", start_x = 0, start_y = 5)

The first parameter we send to ``arcade.Text`` is a String containing the text we want to draw. In our example we provide an f-string which
adds our value from ``self.score`` into the text. The other parameters are defining the bottom left point that our text will be drawn at.

I've set it to draw in the bottom left of our screen here. You can try moving it around.

Now we need to add this to our ``on_draw`` function in order to get it to display on the screen.

.. code-block::

    # Within on_draw
    self.gui_camera.use()
    self.score_text.draw()

This will now draw our text in the bottom left of the screen. However, we stil have one problem left, we're not updating the text when our user
gets a new score. In order to do this we will go back to our ``on_update`` function, where we incremented the score when the user collects a coin,
and add one more line to it:

.. code-block::

    for coin in coin_hit_list:
        coin.remove_from_sprite_lists()
        arcade.play_sound(self.collect_coin_sound)
        self.score += 75
        self.score_text.text = f"Score: {self.score}"

In this new line we're udpating the actual text of our Text object to contain the new score value.

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/10_score.py
    :caption: Multiple Levels
    :linenos:
    :emphasize-lines: 56-63, 124-131, 149-153, 171-172

Run This Chapter
~~~~~~~~~~~~~~~~

.. code-block::

  python -m arcade.examples.platform_tutorial.10_score
