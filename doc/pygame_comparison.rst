.. _pygame-comparison:

Pygame Comparison
=================

The Python Arcade Library has the same target audience as the well-known
Pygame library. So how do they differ?

.. list-table:: Library Information
   :widths: 33 33 33
   :header-rows: 1

   * - Feature
     - Arcade
     - Pygame
   * - Website
     - https://arcade.academy
     - https://www.pygame.org
   * - API Docs
     - `API Docs <https://arcade.academy/quick_index.html>`_
     - `API Docs <https://www.pygame.org/docs/>`_
   * - Examples code
     - `Example code <https://arcade.academy/examples/index.html>`_
     - N/A
   * - License
     - `MIT License`_
     - LGPL_
   * - Back-end graphics engine
     - OpenGL 3.3+ and `Pyglet <http://pyglet.org/>`_
     - `SDL 2 <https://www.libsdl.org/>`_
   * - Back-end audio engine
     - ffmpeg via Pyglet_
     - `SDL 2 <https://www.libsdl.org/>`_
   * - Example Projects
     - :ref:`sample_games`
     - `Games Made With Pygame <https://www.pygame.org/tags/all>`_

.. list-table:: Feature Comparison
   :widths: 33 33 33
   :header-rows: 1

   * - Feature
     - Arcade
     - Pygame
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
   * - Tiled Map Support
     - `Yes <examples/platform_tutorial/step_09.html>`_
     - No
   * - Physics engines
     - `Simple <examples/platform_tutorial/step_04.html>`_,
       `platformer <examples/platform_tutorial/step_05.html>`_, and
       `PyMunk <tutorials/pymunk_platformer/index.html>`_
     - None
   * - Event Management
     - Pyglet-based
     - No (or add `Pygame Zero <https://pygame-zero.readthedocs.io/en/stable/>`_)
   * - View Support
     - `Yes <tutorials/views/index.html>`_
     - No
   * - Light Support
     - `Yes <tutorials/lights/index.html>`_
     - No
   * - GUI Support
     - `Yes <tutorials/user_interface/index.html>`_
     - No (or add `pygame-gui <https://pygame-gui.readthedocs.io/en/latest/>`_)
   * - GPU Shader Support
     - `Yes <tutorials/gpu_particle_burst/index.html>`_
     - No
   * - Built-in Resources
     - `Yes <resources.html>`_
     - No

.. list-table:: Performance Comparison [#f6]_
   :widths: 33 33 33
   :header-rows: 1

   * - Feature
     - Arcade
     - Pygame
   * - Draw 50,000 sprites
     - 0.004 seconds `Source <https://github.com/pythonarcade/performance_tests/blob/master/src/arcade_tests/draw_stationary_sprites.py>`_
     - 0.425 seconds `Source <https://github.com/pythonarcade/performance_tests/blob/master/src/pygame_1_9_tests/draw_stationary_sprites.py>`_
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
.. [#f6] Performance tests done on an Intel Core i7-9700F with GeForce GTX 980 Ti. Souce code for tests available at
         https://github.com/pythonarcade/performance_tests and more detailed results at
         https://craven-performance-testing.s3-us-west-2.amazonaws.com/index.html
.. [#f3] Polygon hit box, rotation allowed
.. [#f4] Rectangular hit box, no rotation allowed

.. _MIT License: https://github.com/pythonarcade/arcade/blob/development/license.rst
.. _LGPL: https://github.com/pygame/pygame/blob/main/docs/LGPL.txt
.. _type hinting: https://docs.python.org/3/library/typing.html
.. _moiré pattern: http://stackoverflow.com/questions/10148479/artifacts-when-drawing-primitives-with-pygame
.. _2.0: https://github.com/pygame/pygame/releases/tag/2.0.0
