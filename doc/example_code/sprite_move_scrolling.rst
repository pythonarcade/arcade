.. _sprite_move_scrolling:

Move with a Scrolling Screen - Centered
=======================================

Using a :class:`arcade.Camera2D`, a program can easily scroll around a larger
"world" while only showing part of it on the screen.

If you are displaying a GUI or some other items that should NOT scroll, you'll
need two cameras. One that shows the unscrolled GUI, and one that shows the scrolled
sprites.

See also :ref:`sprite_move_scrolling_box`.

.. image:: images/sprite_move_scrolling.png
    :width: 600px
    :align: center
    :alt: Screen shot of using a scrolling window

.. literalinclude:: ../../arcade/examples/sprite_move_scrolling.py
    :caption: sprite_move_scrolling.py
    :linenos:
    :emphasize-lines: 55-58, 100-101, 107-108, 161-162, 164-176, 178-184
