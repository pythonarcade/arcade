.. _performance:

Performance
===========

.. image:: ../images/flame-arrow.svg
    :width: 20%
    :class: right-image

This page covers the most common slowdowns in games:

#. :ref:`Collision detection <collision_detection_performance>`
#. :ref:`Drawing <drawing_performance>`
#. :ref:`Loading-related issues <loading_performance>`


.. _collision_detection_performance:

Collision Detection Performance
-------------------------------

.. image:: ../images/collision.svg
    :width: 30%
    :class: right-image

Why are collisions slow?
^^^^^^^^^^^^^^^^^^^^^^^^

Imagine you have 50,000 :py:class:`~arcade.Sprite` instances:

* One is the player
* The other 49,999 are the ground

The Simplest Solutions are Slow
"""""""""""""""""""""""""""""""

The simplest approach is a for loop over every wall. Even if the hitboxes
of both the player and the ground :py:class:`Sprite` objects are squares,
it will still be a lot of work.

Game developers often use **Big O** notation to describe:
* the worst-case execution speed of code
* how quickly it grows with the size of the input.

In this case, it grows linearly with the number of walls. Therefore, it's
called "Order N" or "O(N)" and Pronounced "Oh-En".

Adding more moving elements means the number of collision checks will grow
very quickly. How do we stop a game from dropping below 60 FPS?

The Faster Alternatives
^^^^^^^^^^^^^^^^^^^^^^^
Arcade supports two solutions out the box. Both are described below:

#. The built-in :ref:`collision_detection_performance_hashing`
#. The :ref:`Pymunk physics engine integrations <collision_detection_performance_pymunk>`

Which should I use?
"""""""""""""""""""

.. list-table::
   :header-rows: 1

   * - Approach
     - Best when
     - Example code

   * - Default settings
     - N < 100 sprites (especially if most move)
     - :ref:`sprite_follow_simple`

   * - Spatial hashing
     - N > 100 mostly non-moving sprites [#]_
     - :ref:`line_of_sight`

   * - :py:class:`~arcade.pymunk_physics_engine.PymunkPhysicsEngine`
     - You need forces, torque, joints, or springs
     - :ref:`example-code-pymunk`

.. [#]
   Arcade's non-PyMunk physics both engines assume it will be enabled
   for any :py:class:`~arcade.sprite_list.SpriteList` provided via their
   ``walls`` argument.

.. _collision_detection_performance_hashing:

Spatial Hashing
^^^^^^^^^^^^^^^

**Spatial hashing** is meant for collision checking sprites
against a :py:class:`~arcade.sprite_list.SpriteList` of
**non-moving** sprites:

* checking collisions against hashed sprites becomes much faster
* moving or resizing any sprite in the hash becomes much slower

It divides the game world into grid squares of regular size. Then, it
uses a **hash map** (:py:class:`dict`) of grid square coordinates to lists
of :py:class:`~arcade.Sprite` objects in each square.

How does this help us? We may need as few as zero hitbox checks to collide
a given sprite against a :py:class:`~arcade.sprite_list.SpriteList`. Yes,
**zero**:

.. image:: images/spatial_hash_grid_mockup.png
   :alt: A blue bird is alone in its own grid square.

#. The sand-colored ground consists of sprites in a
   :py:class:`~arcade.sprite_list.SpriteList` with spatial hashing enabled
#. The bright green lines show the grid square boundaries
#. The moving sprites are the blue bird and the red angry faces

The exact number of checks per moving sprite depends on the following:

* the grid size chosen (controlled by the ``spatial_hash_cell_size`` argument)
* how many :py:class:`~arcade.Sprite` objects are in any given square
* the size of each :py:class:`~arcade.Sprite` passed

Since the bird is small enough to be alone in a grid square, it
will perform zero hitbox checks against terrain while flying. This
will also be true for any projectiles or other flying objects in the
air above the terrain.

What about the red angry-faces on the ground? They still perform fewer
hitbox checks against terrain than if spatial hashing was not enabled.


.. _collision_detection_performance_spatial_hashing_doc:

Enabling Spatial Hashing
""""""""""""""""""""""""

The best way to enable spatial hashing on a
:py:class:`~arcade.sprite_list.SpriteList` is before anything else,
especially before gameplay.

The simplest way is passing ``use_spatial_hash=True`` when creating
and storing the list inside a :py:class:`~arcade.Window` or
:py:class:`~arcade.view.View`:

.. code-block:: python

   # Inside a Window or View, and often inside a setup() method
   self.spritelist_with_hashing = arcade.SpriteList(use_spatial_hash=True)


Spatial Hashing and Tiled Maps
""""""""""""""""""""""""""""""
There is also a way to enable spatial hashing when loading Tiled maps. For
each layer you'd like to load with spatial hashing, set a ``"use_spatial_hashing"``
key in its layer options to ``True``:

.. code-block:: python

   layer_options = {
        "ground": {
            "use_spatial_hash": True
        },
        "non_moving_platforms": {
            "use_spatial_hash": True
        }
   }

For a runnable example of this, please see :ref:`camera_platform`. Additional
examples are linked below in :ref:`collision_performance_spatial_hashing_examples`.

The Catch
"""""""""
Spatial hashing doubles the cost of moving or resizing sprites.

However, this doesn't mean we can't *ever* move or resize a sprite!
Instead, it means we have to be careful about when and how much we
do so. This is because moving and resizing now consists of:

#. Remove it from the internal list of every grid square it is currently in
#. Add it again by re-computing its new location

If we only move a few sprites in the list now and then, it can work out.
When in doubt, test it and see if it works for your specific use case.

.. _collision_performance_spatial_hashing_examples:

Further Example Code
""""""""""""""""""""

For detailed step-by-step tutorial steps on using spatial hashing,
please see:

* :ref:`platformer_part_three`
* :ref:`platformer_part_twelve`

For detailed API notes, please see:

* :py:class:`arcade.SpriteList`
* :py:meth:`arcade.SpriteList.enable_spatial_hashing`
* :py:class:`arcade.sprite_list.spatial_hash.SpatialHash`
* :py:class:`arcade.physics_engines.PhysicsEngineSimple`
* :py:class:`arcade.physics_engines.PhysicsEnginePlatformer`


Spatial Hashing Implementation Details
""""""""""""""""""""""""""""""""""""""

.. note:: Many readers can skip this section.

The hash map is a Python :py:class:`dict` mapping :py:class:`tuple`
coordinate pairs to :py:class:`list` instances.

"Hashing" works like this for any given sprite:

#. Divide the X and Y of its lower left by the grid square size
#. Divide the X and Y of its upper right by the grid square size
#. Every grid square between these is considered touched

Adding a sprite hashes its hitbox as above. Colliding with sprites already
added involves hashing, then performing a detailed collision check against
every sprite in every touched tile.

.. _collision_detection_performance_pymunk:

Pymunk Physics Engine
^^^^^^^^^^^^^^^^^^^^^
Arcade provides a helper wrappers around `Pymunk`_, a binding for
the professional-grade `Chipmunk2D`_ engine.

It offers many features beyond anything Arcade's other built-in physics
options currently offer. This professional-grade power comes with complexity
and speed many users may want find worthwhile.

None of Arcade's other engines support torque, multiple forces, joints, or springs.
If you find yourself needing these or the speed only binary-backed acceleration can
offer, this may be the right choice.

To get started, please see the following:

* The :ref:`example-code-pymunk` Example
* Arcade's :ref:`pymunk_platformer_tutorial` tutorial
* :py:class:`arcade.pymunk_physics_engine.PymunkPhysicsEngine`
* The :py:mod:`pymunk` documentation

Compute Shader
^^^^^^^^^^^^^^

Currently on the drawing board, is the use of a **compute shader** on your graphics card
to detect collisions. This has the speed advantages of spatial hashing, without the speed
penalty.

.. _drawing_performance:

Drawing Performance
-------------------

To draw at 60 frames per second or better, there are rules you need to follow.

The most important is simple. You should draw items the same way you would bake
muffins: in batches. If you ignore this, you will have poor drawing performance.

The rest of this section will cover how to avoid that.

Drawing Shapes
^^^^^^^^^^^^^^

The :py:mod:`arcade.draw` module is slow despite being convenient.

This is because it does not perform batched drawing. Instead of sending batches
of shapes to draw, it sends them individually.

You have three options for drawing shapes more efficiently:

#. Use Arcade's non-modifiable shapes with :class:`arcade.shape_list.ShapeElementList`
#. Use pyglet's updatable :py:mod:`pyglet.shapes` module
#. Write your own advanced shaders

For more information, please see:

* :ref:`shape_list_demo`

Sprite drawing performance
--------------------------

Arcade's :class:`arcade.SpriteList` is the only way to draw a :py:class:`~arcade.Sprite`.

This is because all drawing with a graphics card is batched drawing.
The :py:class:`~arcade.SpriteList` handles batching for you. As a result,
you can draw thousands of moving sprites with any extra effort on your
part.

An Option for Advanced Users
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Advanced users may want to try pyglet's :py:class:`pyglet.sprite.Sprite`.

Instead of Arcade's :py:class:`~arcade.SpriteList`, pyglet sprites use a
mix of the following classes:

* :py:class:`pyglet.graphics.Batch`
* :py:class:`pyglet.graphics.Group`

Both pyglet's sprites, groups, and batches are much closer to OpenGL's
low-level components and will require investing time to learn their features.
They also lack many of the features you may be used to in Arcade.


Text drawing performance
------------------------

The slowest thing aside from disk access is :meth:`arcade.draw_text`.

To improve performance:

#. Use :py:class:`arcade.Text` instead
#. (Optional) Pass a pyglet :py:class:`~pyglet.graphics.Batch` object at creation

See the following to learn more:

* :ref:`drawing_text_objects`
* :ref:`drawing_text_objects_batch`


.. _loading_performance:

Loading Performance
-------------------

Disk access is one of the slowest things a computer can do.

Your goal for minimizing performance is to reduce the amount of data you
read and write during gameplay to a minimum. Fortunately, this is fairly
easy. It comes down to one thing above all else.

Preload everything you can before gameplay.

Loading Screens and Rooms
^^^^^^^^^^^^^^^^^^^^^^^^^

You may be familiar with loading screens.

Other approaches include:

* In-game loading "rooms" with minimal performance impact
* Multi-threading to load data on background threads [#]_

Both allow background loading of data before gameplay. You can use these for
loading audio, textures, and other data before the player enters the game.

However, there are a few exceptions. These are described below, especially
with streaming audio.

.. [#]
   This can be dangerous for loading graphics and sprite data due to
   since OpenGL only allows one thread to touch the OpenGL context.


.. _loading_performance_sound:

Sound Performance in Depth
--------------------------

This page covers static and streaming sounds in depth.

If you are not familiar, you may want to read :ref:`sound-loading-modes`
before proceeding.

.. _sound-loading-modes-static:

Static Sounds are for Speed
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Static sounds can help your game run smoothly by preloading
data before gameplay.

If music is a central part of your gameplay or application, then in some
cases you may want to use this approach for loading music. However, you
should be careful about it.

Each decompressed minute of CD-quality audio uses slightly over 10 MB
of RAM. This adds up quickly. Loading entire albums into memory without
clearing them can slow down or freeze a computer, especially if you
fill RAM completely.

For music and long background audio, you should strongly consider
:ref:`streaming <sound-loading-modes-streaming>` from compressed files
instead.

When to Use Static Sounds
"""""""""""""""""""""""""

If an audio file meets one or more of the following conditions, you may
want to load it as static audio:

* You need to start playback quickly in response to gameplay.
* Two or more "copies" of the sound can be playing at the same time.
* You will unpredictably skip to different times in the file.
* You will unpredictably restart playback.
* You need to automatically loop playback.
* The file is a short clip.

.. _sound-loading-modes-streaming:

Streaming Saves Memory
^^^^^^^^^^^^^^^^^^^^^^

Streaming audio from compressed files is similar to streaming video online.

Both save memory by:

#. Transmitting a compressed version over a constrained connection
#. Only decompressing part of a file in memory at a time

As with online video, this works on even the weakest recent hardware
if:

* You only stream one media source at a time.
* You don't need to loop or jump around in the audio.

Since compressed formats like MP3 are much smaller than their
decompressed forms, the cost of reading them piece by piece into
RAM can be an acceptable tradeoff which saves memory. Once in RAM,
many formats are quick to decompress and worth the RAM savings.

When to Stream
""""""""""""""
In general, avoid streaming things other than music and ambiance.

In addition to disabling features like looping and multiple playbacks,
they can  also introduce other complications. For example, you may face
issues with synchronization and interruptions. These may worsen as the
quantity and quality of the audio tracks involved increases.

If you're unsure, avoid streaming unless you can say yes to all of the
following:

#. The :py:class:`~arcade.sound.Sound` will have at most one playback at a time.

#. The file is long enough to make it worth it.

#. Seeking (skipping to different parts) will be infrequent.

   * Ideally, you will never seek or restart playback suddenly.
   * If you do seek, the jumps will ideally be close enough to
     land in the same or next chunk.

See the following to learn more:

* :ref:`sound-intermediate-playback-change-aspects-ongoing`
* The :py:class:`pyglet.media.StreamingSource` class used to implement
  streaming


.. _sound-loading-modes-streaming-freezes:

Streaming Can Cause Freezes
"""""""""""""""""""""""""""
Failing to meet the requirements above can cause buffering issues.

Good compression on files can help, but it can't fully overcome it. Each
skip outside the currently loaded data requires reading and decompressing
a replacement.

In the worst-case scenario, frequent skipping will mean constantly
buffering instead of playing. Although video streaming sites can
downgrade quality, your game will be at risk of stuttering or freezing.

The best way to handle this is to only use streaming when necessary.





