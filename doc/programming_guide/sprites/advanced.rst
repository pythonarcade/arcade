.. _pg_spritelists_advanced:

Advanced SpriteList Techniques
------------------------------

This page provides overviews of advanced techniques. Runnable examples are
not guaranteed, as the reader is expected to be able to put the work into
implementing them.

Beginners should be careful of the following sections. Some of these techniques
can slow down or crash your game if misused.


.. _pg_spritelists_advanced_draw_order_and_sorting:

Draw Order & Sorting
^^^^^^^^^^^^^^^^^^^^

In some cases, you can combine two features of SpriteList:

* By default, SpriteLists draw starting from their lowest index.
* :py:class:`~arcade.SpriteList` has a :py:meth:`~arcade.SpriteList.sort`
  method nearly identical to :py:meth:`list.sort`.


First, Consider Alternatives
""""""""""""""""""""""""""""

Sorting in Python is a slow, CPU-bound function. Consider the following
techniques to eliminate or minimize this cost:

* Use multiple sprite lists or :py:class:`arcade.Scene` to
  achieve layering
* Chunk your game world into smaller regions with sprite lists
  for each, and only sort when something inside moves or changes
* Use the :py:attr:`Sprite.depth <arcade.BasicSprite.depth>` attribute
  with :ref:`shaders <tutorials_shaders>` to sort on the GPU

For a conceptual overview of chunks as used in a commercial 2D game, please
see the following:

* `Chunks in Factorio <https://wiki.factorio.com/Map_structure#Chunk>`_


Sorting SpriteLists
"""""""""""""""""""

Although the alternatives listed above are often better, sorting sprite lists to
control draw order can still be useful.

Like Python's built-in :py:meth:`list.sort`, you can pass a
`callable object <https://docs.python.org/3/library/functions.html#callable>`_
via the key argument to specify how to sort, along with an optional ``reverse``
keyword to reverse the direction of sorting.

Here's an example of how you could use sorting to quickly create an
inefficient prototype:

.. code:: python


    import random
    import arcade


    # Warning: the bottom property is extra slow compared to other attributes!
    def bottom_edge_as_sort_key(sprite):
        return sprite.bottom


    class InefficientTopDownGame(arcade.Window):
        """
        Uses sorting to allow the player to move in front of & behind shrubs

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


.. _pg_spritelist_advanced_texture_atlases:

Custom Texture Atlases
^^^^^^^^^^^^^^^^^^^^^^

A :py:class:`~arcade.DefaultTextureAtlas` represents :py:class:`~arcade.Texture`
data packed side-by-side in video memory. As textures are added, the atlas
grows to fit them all into the same portion of your GPU's memory.

By default, each :py:class:`~arcade.SpriteList` uses the same default
atlas. Use the ``atlas`` keyword argument to specify a custom atlas
for an instance.

This is especially useful to prevent problems when using large or oddly
shaped textures.

Please see the following for more information:

* :ref:`pg_textureatlas_custom_atlas`
* The :py:class:`~arcade.DefaultTextureAtlas` API documentation


.. _pg_spritelist_advanced_lazy_spritelists:

Lazy SpriteLists
^^^^^^^^^^^^^^^^

You can delay creating the OpenGL resources for a
:py:class:`~arcade.SpriteList` by passing ``lazy=True`` on creation:

.. code:: python

    sprite_list = SpriteList(lazy=True)

The SpriteList won't create the OpenGL resources until forced to
by one of the following:

1. The first :py:meth:`SpriteList.draw() <arcade.SpriteList.draw>` call on it
2. :py:meth:`SpriteList.initialize() <arcade.SpriteList.initialize>`
3. GPU-backed collisions, if enabled

This behavior is most useful in the following cases:

.. list-table::
    :header-rows: 1

    * - Case
      - Primary Purpose

    * - Creating SpriteLists before a Window
      - CPU-only `unit tests <https://docs.python.org/3/library/unittest.html>`_ which
        never draw

    * - Parallelized SpriteList creation
      - Faster loading & world generation via :py:mod:`threading`
        or :py:mod:`subprocess` & :py:mod:`pickle`


.. _pg_spritelist_advanced_parallel_loading:

Parallelized Loading
""""""""""""""""""""

To increase loading speed & reduce stutters during gameplay, you can
run pre-gameplay tasks in parallel, such as pre-generating maps
or pre-loading assets from disk into RAM.


.. warning:: Only the main thread is allowed to access OpenGL!

             Attempting to access OpenGL from non-main threads will
             raise an OpenGL Error!

To safely implement parallel loading, you will want to use the following
general approach before allowing gameplay to begin:

1. Pass ``lazy=True`` when creating :py:class:`~arcade.SpriteList` instances
   in your loading code as described above
2. Sync the SpriteList data back to the main thread or process once loading
   is finished
3. Inside the main thread, call
   :py:meth:`Spritelist.initialize() <arcade.SpriteList.initialize>` on each
   sprite list once it's ready to allocate GPU resources


Very advanced users can use :py:mod:`subprocess` to create SpriteLists
inside another process and the :py:mod:`pickle` module to help pass data
back to the main process.

Please see the following for additional information:

* :ref:`Arcade's OpenGL notes <open_gl_notes>` for Arcade-specific
  threading considerations
* Python's :py:mod:`threading` documentation
* Python's :py:mod:`subprocess` and :py:mod:`pickle` documentation
