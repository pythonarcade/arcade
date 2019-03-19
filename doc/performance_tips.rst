Performance
===========

Drawing Sprites
---------------

Drawing the sprites in a single SpriteList class is a very fast operation. You can
put almost as many sprites into a SpriteList as you want (I've had over 400,000)
and still keep 60 fps.

Pygame takes longer to draw sprites, but it still can handle thousands of them
before you notics a slowdown.

.. image:: images/chart_stress_test_draw_moving_draw_comparison.svg

Moving Sprites
--------------

The faster drawing speed comes at a cost.
It takes longer to move sprites in Arcade than Pygame.

Arcade not only stores the sprite location in the Python object, it also
stores the sprite location in a numpy data array managed by the SpriteList. This
numpy array gets passed to the graphics card. Changing a numpy value in the
array is much slower than changing a native Python value.

Hopefully we will soon find a way to improve this issue in Arcade.

.. image:: images/chart_stress_test_draw_moving_process_comparison.svg

Collision Detection
-------------------

Pygame has fast collision detection as the rects are managed in C, and
that part of Pygame compiles natively to the computer.
The trade-off for not being pure Python is very fast collision detection,
even if it is an O(n) operation.

Arcade is much slower, unless the SpriteList was created with
``use_spatial_hash=True`` as a parameter.
Spatial hashing allows us to group the sprites so that we only check sprites that
are nearby. For sprites that are spread out (like a map) we can do detection
closer to O(1).
Unfortunately, it take longer to move a sprite in a SpriteList because the hash
maps have to be updated.

.. image:: images/chart_stress_test_collision_comparison.svg

