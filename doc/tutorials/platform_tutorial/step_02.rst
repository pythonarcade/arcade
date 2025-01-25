.. _platformer_part_two:

Step 2 - Textures and Sprites
-----------------------------

Our next step in this tutorial is to draw something on the Screen. In order to
do that we need to cover two topics, Textures and Sprites.

At the end of this chapter, we'll have something that looks like this. It's largely the
same as last chapter, but now we are drawing a character onto the screen:

.. image:: images/title_02.png
    :width: 70%

Textures
~~~~~~~~

Textures are largely just an object to contain image data. Whenever you load an image
file in Arcade, for example a ``.png`` or ``.jpeg`` file. It becomes a Texture.

To do this, internally Arcade uses Pyglet to load the image data, and the texture is
responsible for keeping track of this image data.

We can create a texture with a simple command, this can be done inside of our ``__init__``
function. Go ahead and create a texture that we will use to draw a player.

.. code-block::

    self.player_texture = arcade.load_texture(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png")

.. note::

    You might be wondering where this image file is coming from? And what is ``:resources:`` about?

    The ``:resources:`` section of the string above is what Arcade calls a resource handle.
    You can register your own resource handles to different asset directories. For example you
    might want to have a ``:characters:`` and a ``:objects:`` handle.

    However, you don't have to use a resource handle here, anywhere that you can load files in Arcade will
    accept resource handles, or just strings to filepaths, or ``Path`` objects from ``pathlib``

    Arcade includes the ``:resources:`` handle with a bunch of built-in assets from `kenney <https://kenney.nl>`_.

    For more information checkout :ref:`resources`

Sprites
~~~~~~~

If Textures are an instance of a particular image, then :class:`arcade.Sprite` is an instance of that image
on the screen. Say we have a ground or wall texture. We only have one instance of the texture, but we can create 
multiple instances of Sprite, because we want to have many walls. These will use the same texture, but draw it
in different positions, or even with different scaling, rotation, or colors/post-processing effects.

Creating a Sprite is simple, we can make one for our player in our ``__init__`` function, and then set it's position.

.. code-block::

    self.player_sprite = arcade.Sprite(self.player_texture)
    self.player_sprite.center_x = 64
    self.player_sprite.center_y = 128

.. note::

    You can also skip ``arcade.load_texture`` from the previous step and pass the image file to ``arcade.Sprite`` in place of the Texture object. 
    A Texture will automatically be created for you. However, it may desirable in larger projects to manage your textures directly.

Now we can draw the sprite by adding this to our ``on_draw`` function:

.. code-block::

    arcade.draw_sprite(self.player_sprite)

We're now drawing a Sprite to the screen! In the next chapter, we will introduce techniques to draw many(even hundreds of thousands) sprites at once.

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/02_draw_sprites.py
    :caption: 02_draw_sprites - Draw and Position Sprites
    :linenos:
    :emphasize-lines: 24-30, 44-45

Running this code should result in a character being drawn on the screen, like in
the image at the start of the chapter.

* Documentation for the :class:`arcade.Texture` class
* Documentation for the :class:`arcade.Sprite` class

.. note::

    Once you have the code up and working, try adjusting the code for the following:

    * Adjust the code and try putting the sprite in new positions(Try setting the positions using other attributes of Sprite)
    * Use different images for the texture (see :ref:`resources` for the built-in images, or try using your own images.)
    * Practice placing more sprites in different ways(like placing many with a loop)

Run This Chapter
~~~~~~~~~~~~~~~~

.. code-block::

  python -m arcade.examples.platform_tutorial.02_draw_sprites
