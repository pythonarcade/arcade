.. _pg_spritelists:

Drawing with SpriteLists
========================

.. _pg_spritelists_why:

Why SpriteLists?
----------------

Your Game Will Be Faster
^^^^^^^^^^^^^^^^^^^^^^^^

Graphics hardware is designed to draw objects in groups called batches.
:py:class:`~arcade.SpriteList` automatically translates your
:py:class:`~arcade.Sprite` instances into optimized batches.

Trying to force Sprites to draw one at a time will make your game
run much slower.

.. tip:: Don't use :py:class:`~arcade.Sprite`'s :py:meth:`~arcade.Sprite.draw` method!

         This method uses a batch size of 1 for each sprite. It's meant
         for debugging rather than drawing. Use
         :py:meth:`arcade.SpriteList for drawing instead!


Development Will Be Faster
^^^^^^^^^^^^^^^^^^^^^^^^^^

SpriteLists increase your efficiency as a developer:

* Sprites outside the current viewport are automatically skipped when drawing
* Thousands of sprites can be drawn at once with reasonable performance
* Built-in methods for common tasks such as collision detection & drawing hitboxes


.. _pg_spritelists_drawing_sprites:

Creating & Drawing Sprites with SpriteLists
-------------------------------------------

There are 4 steps to drawing sprites using a :py:class:`~arcade.SpriteList`:

 1. Create the SpriteList
 2. Create & configure your :py:class:`~arcade.Sprite` instance(s)
 3. Add your sprite(s) to your SpriteList
 4. Call :py:meth:`~arcade.SpriteList.draw` on your SpriteList inside an
    :py:meth:`~arcade.Window.on_draw` method

Here's a minimal example:

.. code:: python

    import arcade


    class WhiteSpriteCircleExample(arcade.Window):

        def __init__(self):
            super().__init__(800, 600, "White SpriteCircle Example")
            self.sprites = None
            self.setup()

        def setup(self):
            # 1. Create the SpriteList
            self.sprites = arcade.SpriteList()

            # 2. Create & configure your Sprite instance
            self.circle = arcade.SpriteCircle(30, arcade.color.WHITE)  # 30 pixel radius circle
            self.circle.position = self.width // 2, self.height // 2  # Put it in the middle

            # 3. Add your sprite to your SpriteList
            self.sprites.append(self.circle)

        def on_draw(self):
            # 4. Call draw() on the SpriteList inside an on_draw() method
            self.sprites.draw()


    game = WhiteSpriteCircleExample()
    game.run()

Using Images with Sprites
^^^^^^^^^^^^^^^^^^^^^^^^^

Beginners should see the following to learn more, such as
how to load images into sprites:

* :ref:`Arcade's Sprite examples <sprites>`
* :ref:`Arcade's Simple Platformer Tutorial <platformer_tutorial>`

Viewports
^^^^^^^^^

Intermediate users can move past the limitations of
:py:class:`arcade.Window` with the following classes:

* :py:class:`arcade.Camera` (:ref:`examples <examples_cameras>`)
* :py:class:`arcade.View` (:ref:`examples <view_examples>`)
* :py:class:`arcade.Section` (:ref:`examples <section_examples>`)


.. _pg_spritelists_spatial_hashing:

Spatial Hashing & Collisions
----------------------------

Spatial hashing is a way of speeding up collision detection.
In practical terms, it's a tradeoff:

 * Collision checks become much faster
 * Adding & moving sprites becomes much slower
 * Changing sprite hitboxes becomes much slower
   to the list

.. note:: In technical terms, spatial hashing makes collision checks
          ``O(1)`` at the price of making hit box changes to the
          :py:class:`~arcade.SpriteList` ``O(N)``.

This means you should only consider spatial hashing for
:py:class:`~arcade.SpriteList` instances whose contents do not change
frequently during gameplay.

The best case is holding a game map's indestructible and unmoving
walls. However, you may also find spatial hashing useful in less strict
cases. When in doubt, experiment and profile your code to be sure!
Profiling & performance tuning are a separate topic, but Arcade's built-in
:ref:`performance graphs <performance_statistics_example>` may help you
get started.

Advanced users may want to subclass :py:class:`~arcade.SpriteList` and/or
:py:class:`~arcade.SpatialHash` to customize behavior, such as sharing a
single :py:class:`~arcade.SpatialHash` object between multiple SpriteLists.

For more information on spatial hashing, see the following resources:

* `The gamedev.net article which inspired Arcade's implementation <https://www.gamedev.net/articles/programming/general-and-gameplay-programming/spatial-hashing-r2697/>`_
* `An interactive example from Red Blob Games <https://www.redblobgames.com/x/1730-spatial-hash/>`_
* `A chapter from Game Programming Patterns <http://gameprogrammingpatterns.com/spatial-partition.html>`_

.. _pg_spritelists_advanced:

Advanced SpriteList Features
----------------------------
Beginners should skip the following sections. They can present the
following issues:

* They require prior knowledge of programming for full effectiveness
* Some contain techniques which can slow or even crash your game if
  misused


.. _pg_spritelists_draw_order_and_sorting:

Advanced: Draw Order & Sorting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In some cases, you can combine two features of SpriteList:
* :py:class:`~arcade.SpriteList` has a :py:meth:`~arcade.SpriteList.sort`
  method.
* By default, SpriteLists draw starting from their lowest index.

Consider Better Ways to Control Draw Order
""""""""""""""""""""""""""""""""""""""""""

Instead of sorting many sprites every frame, consider the following
alternatives:

* Use multiple SpriteLists or :py:class:`arcade.Scene` to
  achieve layering
* Use Sprite's :py:attr:`~arcade.BasicSprite.depth` attribute
  to control drawing
* Use :ref:`shaders <tutorials_shaders>` to modify draw order
* Chunk your game world into SpriteLists for smaller regions, and
  only sort when something moves inside them moves or changes

These are almost always a better choice for a polished game than
sorting all or most of your sprites every frame.

Sorting SpriteLists
"""""""""""""""""""

In most cases, you should use the techniques listed above to control
sprite draw order. However, general sorting can still be useful when
you care more about development speed than performance.

Like Python's built-in :py:meth:`list.sort`, you can pass a
`callable object <https://docs.python.org/3/library/functions.html#callable>`_
via the key argument to specify how to sort, along with an optional ``reverse``
keyword to reverse the direction of sorting.

Here's an example of how you could use sorting to quickly create an
inefficient prototype:

.. code:: python

    import arcade
    import random


    # warning: the bottom property is extra slow compared to other attributes
    def bottom_edge_as_sort_key(sprite):
        return sprite.bottom


    class InefficientTopDownGame(arcade.Window):
        """
        Uses sorting to allow the player to move in front & behind shrubs

        For non-prototyping purposes, other approaches will be better.
        """

        def __init__(self, num_shrubs=50):
            super().__init__(800, 600, "Inefficient Top-Down Game")

            self.background_color = arcade.color.SAND
            self.shrubs = arcade.SpriteList()
            self.drawable = arcade.SpriteList()

            # Randomly place pale green shrubs around the screen
            for i in range(num_shrubs):
                shrub = arcade.SpriteSolidColor(20, 40, color=arcade.color.BUD_GREEN)
                shrub.position = random.randrange(self.width), random.randrange(self.height)
                self.shrubs.append(shrub)
                self.drawable.append(shrub)

            self.player = arcade.SpriteSolidColor(16, 30, color=arcade.color.RED)
            self.drawable.append(self.player)

        def on_mouse_motion(self, x, y, dx, dy):
            # Update the player position
            self.player.position = x, y
            # Sort the sprites so the highest on the screen draw first
            self.drawable.sort(key=bottom_edge_as_sort_key, reverse=True)

        def on_draw(self):
            self.clear()
            self.drawable.draw()


    game = InefficientTopDownGame()
    game.run()


.. _pg_spritelist_texture_atlases:

Advanced: Custom Texture Atlases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A :py:class:`~arcade.TextureAtlas` represents :py:class:`~arcade.Texture`
data packed side-by-side in video memory. As textures are added, the atlas
grows to fit them all into the same stretch of VRAM.

By default, each :py:class:`~arcade.SpriteList` uses the same default
atlas. Use the ``atlas`` keyword argument to specify
a custom atlas for the :py:class:`~arcade.SpriteList`.

This is especially useful to prevent problems when using large or oddly
shaped textures.

Please see the following for more information:

* :ref:`Arcade's dedicated Texture Atlas article in the Programming Guide <pg_textureatlas_custom_atlas>`
* The API documentation for :py:class:`arcade.TextureAtlas`


.. _pg_spritelist_lazy_spritelists:

Advanced: Lazy SpriteLists
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can delay creating the OpenGL resources for a
:py:class:`~arcade.SpriteList` by passing ``lazy=True`` on creation:

.. code:: python

    sprite_list = SpriteList(lazy=True)

The SpriteList won't create the OpenGL resources until forced to
by one of the following:

 1. The first :py:meth:`~arcade.SpriteList.draw` call on the SpriteList
 2. Its :py:meth:`~arcade.SpriteList.initialize` method is called

This behavior is most useful in the following cases:

.. list-table::
    :header-rows: 1

    * - Case
      - Primary Purpose

    * - Multi-threaded SpriteList creation
      - Faster loading & world generation times

    * - Creating SpriteLists before a Window
      - CPU-only `unit tests <https://docs.python.org/3/library/unittest.html>`_ which
        never draw



Multi-threaded Loading
""""""""""""""""""""""

To increase loading speed & reduce stutters during gameplay, you can
use multiple threads to handle tasks such as pre-generating maps or
pre-loading assets from disk into RAM.

.. warning:: Only the main thread is allowed to access OpenGL!

             Attempting to access OpenGL from non-main threads will
             raise an OpenGL Error!

To safely implement multi-threaded loading, you will want to use the
following general approach before allowing gameplay to begin:

1. Pass ``lazy=True`` when creating :py:class:`~arcade.SpriteList`
   instances in your loader threads
2. Inside the main thread, call :py:meth:`~arcade.SpriteList.initialize`
   once each SpriteList is ready to allocate corresponding GPU resources

Please see the following for additional information:

* :ref:`Arcade's OpenGL notes <open_gl_notes>` for arcade-specific threading considerations
* `Python's general documentation on threading <https://docs.python.org/3/library/threading.html>`_
