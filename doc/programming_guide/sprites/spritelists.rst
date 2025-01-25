.. _pg_spritelists:

Drawing with Sprites and SpriteLists
------------------------------------

What's a Sprite?
^^^^^^^^^^^^^^^^

Each sprite describes where a game object is & how to draw it. This includes:

* Where it is in the world
* Where to find the image data
* How big the image should be

The rest of this page will explain using the ``SpriteList`` class to draw
sprites to the screen.


.. _pg_spritelists_why:

Why SpriteLists?
^^^^^^^^^^^^^^^^

.. _pg_spritelists_why_hardware:

They're How Hardware Works
""""""""""""""""""""""""""

Graphics hardware is designed to draw groups of objects at the same time.
These groups are called **batches**.

Each :py:class:`~arcade.SpriteList`
automatically translates every :py:class:`~arcade.Sprite` in it
into an optimized batch. It doesn't matter if a batch has one or hundreds of
sprites: it still takes the same amount of time to draw!

This means that using fewer batches helps your game run faster, and that you
should avoid trying to draw sprites one at a time.


.. _pg_spritelists_why_faster_dev:

They Help Develop Games Faster
""""""""""""""""""""""""""""""

Sprite lists do more than just draw. They also have built-in features which save
you time & effort, including:

* Automatically skipping off-screen sprites
* Collision detection
* Debug drawing for hit boxes


.. _pg_spritelists_minimal_sprite_drawing:

Using Sprites and SpriteLists
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's get to the example code.

There are 3 steps to drawing sprites with a sprite list:

1. Create a :py:class:`~arcade.SpriteList`
2. Create & append your :py:class:`~arcade.Sprite` instance(s) to the list
3. Call :py:meth:`~arcade.SpriteList.draw` on your SpriteList inside an
   :py:meth:`~arcade.Window.on_draw` method

Here's a minimal example:

.. literalinclude:: ../../../arcade/examples/sprite_minimal.py
    :caption: sprite_minimal.py
    :linenos:


Using Images with Sprites
^^^^^^^^^^^^^^^^^^^^^^^^^

Beginners should see the following to learn more, such as how to load images
into sprites:

* :ref:`Arcade's Sprite examples <sprite_examples>`
* :ref:`Arcade's Simple Platformer Tutorial <platformer_tutorial>`
* The :py:class:`~arcade.Sprite` API documentation


Viewports, Cameras, and Screens
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Intermediate users can move past the limitations of :py:class:`arcade.Window`
with the following classes:

* :py:class:`arcade.Camera2D` (:ref:`examples <camera_examples>`) to control which part of game space is drawn
* :py:class:`arcade.View` (:ref:`examples <view_examples>`) for start, end, and menu screens
