.. _pygame-comparison:

Pygame Comparison
=================

The Python Arcade Library has the same target audience as the well-known
Pygame library. So how do they differ?

.. list-table:: Feature Comparison
   :widths: 33 33 33
   :header-rows: 1

   * - Feature
     - Arcade
     - PyGame
   * - Website
     - https://arcade.academy/
     - https://www.pygame.org/
   * - API Docs
     - `API Docs <https://arcade.academy/quick_index.html>`_
     - `API Docs <https://www.pygame.org/docs/>`_
   * - Official examples
     - `Example code <https://arcade.academy/examples/index.html>`_
     - N/A
   * - License
     - `MIT License`_
     - LGPL_
   * - Back-end graphics engine
     - OpenGL 3.3+ and Pyglet
     - `SDL 2 <https://www.libsdl.org/>`_
   * - Back-end audio engine
     - ffmpeg
     - `SDL 2 <https://www.libsdl.org/>`_
   * - Tiled Map Support
     - Yes
     - No
   * - Drawing primitives support rotation
     - Yes
     - No [#f1]_
   * - Sprites support rotation
     - Yes
     - No [#f1]_
   * - Sprites support scaling
     - Yes
     - No [#f1]_
   * - Sprite image caching
     - Yes
     - No [#f2]_
   * - Transparency support
     - Yes
     - Must specify transparent pixel
   * - Android support
     - No
     - Yes
   * - Raspberry Pi support
     - No
     - Yes
   * - Batch drawing
     - Via GPU
     - No [#f5]_
   * - Default Hitbox
     - .. image:: images/hitbox_simple.png
          :width: 30%
     - .. image:: images/hitbox_none.png
          :width: 50%
   * - Physics engines
     - Simple, platformer, and PyMunk
     - None
   * - Draw 50,000 sprites
     - 0.004 seconds
     - 0.425 seconds
   * - Move 5,000 sprites
     - 0.011 seconds
     - 0.003 seconds
   * - Collision detection 50,000 sprites
     - | 0.044 seconds no spatial hashing [#f3]_
       | 0.005 seconds with spatial hashing
     - 0.004 seconds [#f4]_

.. [#f1] To support rotation and/or scaling, PyGame programs must write the image to a surface, transform the surface,
         then create a sprite out of the surface. This takes a lot of CPU. Arcade off-loads all these operations to the
         graphics card.
.. [#f2] When creating a sprite from an image, PyGame will load the image from the disk every time. The user must
         cache the image with their own code for better performance. Arcade does this automatically.
.. [#f5] A programmer can achieve a similar result by drawing to a surface, then drawing drawing the surface to the screen.
.. [#f3] Polygon hit box, rotation allowed
.. [#f4] Rectangular hit box, no rotation allowed

.. _MIT License: https://github.com/pythonarcade/arcade/blob/development/license.rst
.. _LGPL: https://github.com/pygame/pygame/blob/main/docs/LGPL.txt
.. _type hinting: https://docs.python.org/3/library/typing.html
.. _moiré pattern: http://stackoverflow.com/questions/10148479/artifacts-when-drawing-primitives-with-pygame
.. _2.0: https://github.com/pygame/pygame/releases/tag/2.0.0
