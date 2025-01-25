.. _platformer_part_six:

Step 6 - Resetting
------------------

You might have noticed that throughout this tutorial, there has been a ``setup`` function
in our Window class. So far, we haven't used this function at all, so what is it for?

Let's imagine that we want a way to "reset" our game to it's initial state. This could be
because the player lost, and we want to restart the game, or perhaps we just want to give the
player the option to restart.

With our current architecture of creating everything in our ``__init__`` function, we would have to
duplicate all of that logic in another function in order to make that happen, or completely re-create
our Window, which will be an unpleasent experience for a player.

In this chapter, we will do a small amount of re-organizing our existing code to make use of this
setup function in a way that allows to simply call the ``setup`` function whenever we want our game
to return to it's original state.

First off, we will change our ``__init__`` function to look like below. We are setting values
to something like ``None``, 0, or similar. The purpose of this step is to ensure that the attributes
are created on the class. In Python, we cannot add new attributes to a class outside of the ``__init__`` function.

.. code-block::

    def __init__(self):

        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.player_texture = None
        self.player_sprite = None
        self.player_list = None

        self.wall_list = None

Next we will move the actual creation of these objects into our setup function. This looks almost identical
to our original ``__init__`` function. Try and move these sections of code on your own, if you get stuck you can
see the ``setup`` function in the full source code listing below.

The last thing we need to do is create a way to reset the game. For now we'll add a simple key press to do it.
Add the following in your ``on_key_press`` function to reset the game when the Escape key is pressed.

.. code-block::

    if key == arcade.key.ESCAPE:
        self.setup()

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/06_reset.py
    :caption: Resetting
    :linenos:
    :emphasize-lines: 33, 36, 39, 47, 49-93, 114-115

Run This Chapter
~~~~~~~~~~~~~~~~

.. code-block::

  python -m arcade.examples.platform_tutorial.06_reset
