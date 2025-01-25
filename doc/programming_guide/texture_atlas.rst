
.. _pg_textureatlas:

Texture Atlas
=============

.. _pg_textureatlas_intro:

Introduction
------------

:py:class:`arcade.DefaultTextureAtlas` is where your textures eventually end up
when they are used in a sprite. This is where the image data is moved
to graphics memory (OpenGL) and is one of the reasons we can
batch draw hundreds of thousands of sprites extremely fast.

A texture atlas is basically a large texture containing multiple textures
and we keep track of where these textures are located. Arcade's
texture atlas reside in graphics memory and is dynamic meaning
textures can be added and removed on the fly.

Arcade's texture atlas also automatically resizes when needed all the way
up to the maximum texture size your hardware supports. This requires
a complete rebuild of the atlas, something we do on the gpu itself
to minimize the impact of this operations. For average hardware 
it's something you won't notice runtime.

It's also important to note that texture atlases can only be created
after the window has been created. Textures and sprites can be
created before the window because they don't interact with OpenGL
directly. This part is usually the most time consuming while
atlases are very fast to create and build.

Size Restriction
----------------

Currently we use a very simple row based allocation algorithm
to make room for new textures over time. This means that very
tall textures can end up taking a lot of vertical space.

The maximum size of the atlas is usually 16384 x 16384 if we
are targeting average hardware.

Resize
-------

Atlases will resize automatically when full. It will also
try to pack the textures better by sorting them by their
height.

Default Texture Atlas
---------------------

Most users will not be aware that Arcade is using a texture
atlas under the hood. More advanced users can take advantage
of these if they run into limitations.

Arcade has a global default texture atlas stored in ``window.ctx.default_atlas``.
This is an instance of :py:class:`arcade.ArcadeContext` where the low
level rendering API is accessed (OpenGL).

.. _pg_textureatlas_custom_atlas:

Custom Atlas
------------

Instead of relying on the global texture atlas we can also create our own.
Sprite lists take an ``atlas`` argument for supplying your own texture atlas instance.
This atlas can also be shared between several sprite lists if needed.

.. code:: python

    # Create an empty 256 x 256 texture atlas
    my_atlas = DefaultTextureAtlas((256, 256))
    spritelist = SpriteList(atlas=my_atlas)

When new textures are detected (sprite is added to list) the texture is
added to the atlas.

We can also pre-add textures into an atlas before the game starts to
avoid potential minor stalls. This is usually not a problem, but when
adding a large amount of them it can be noticeable.

.. code:: python

    # List of arcade.Texture instances
    list_of_textures = ...

    # Create an atlas with a specific size and initial textures
    atlas = DefaultTextureAtlas((256, 256), textures=list_of_textures)

    # We can also pre-add textures at any time using:
    # (can also be done with the default texture atlas)
    atlas.add(texture)

Border
------

Atlases has a ``border`` property that is ``1`` by default. This is important
to avoid "texture bleeding" between borders of the textures in the atlas.
This is a very common issues in games using the gpu based graphics and is
even a problem with using ``NEAREST`` interpolation when sprites are rotating.

Keep the default value of this property unless you know exactly what you are doing.

Updating Texture
----------------

In some instances it can be useful to update a texture. We would normally
do this by modifying the Pillow texture in the :py:class:`arcade.Texture`
instance. However, this doesn't update the texture in the atlas itself.
We can manually update it:

.. code:: python

    # Change the internal image in a texture
    texture.image  # <- Modify or crate a new image with the same size

    # Write the new image data to the atlas
    atlas.update_texture_image(texture)

This updates the already allocated region and the image needs to be exactly
the same size. This should be used sparingly or at least not a per frame
operation. If can be fast as a per-frame operation, but you'll need to
profile that. Animated sprites are much better option, but of course
requires pre-determined texture frames.

Removing Texture
----------------

If you have stale textures they can be removed from the atlas using::

    atlas.remove(texture)

This will make the region free for new textures the next time the
atlas rebuilds. You can also call :py:meth:`arcade.DefaultTextureAtlas.rebuild`
directly if you are removing a large quantity of textures, but generally
it's enough to let this happen automatically when needed.

Rendering Into Atlas
---------------------

A much faster way to update a texture in the atlas is rendering directly
into it. This can for example be used to make a minimap for your game
or in any case you need the sprite texture to be really dynamic
(not decided by pre-made texture frames). It can be used in many creative ways.

.. code:: python

    # --- Initialization ---
    # Create an empty texture so we can allocate some space in the atlas
    texture = arcade.Texture.create_empty("render_area_1", size=(256, 256))

    # Assign the texture to a sprite
    sprite = arcade.Sprite(center_x=200, center_y=300, texture=texture)

    # Create the spritelist and add the sprite
    spritelist = arcade.SpriteList()
    # Adding the sprite will also add the texture to the atlas
    spritelist.append(sprite)

    # -- Rendering ---
    # Let's render something into our texture directly.
    # All operations will only affect the allocated portion of the atlas for texture.
    # We are given a framebuffer instance representing this area
    with spritelist.atlas.render_into(texture) as framebuffer:
        # Clear the allocated region in the atlas (if you need it)
        framebuffer.clear()
        # From here on we can draw using any Arcade draw functionality
        arcade.draw_rectangle_filled(128, 128, 160, 160, arcade.color.WHITE, rotation)

    # Draw the spritelist and see your animating sprite texture
    spritelist.draw()

Doing the rendering part above every frame (and incrementing ``rotation`` by delta time)
will give you a sprite with a rotating rectangle a a texture. Again, you can draw anything
into this texture area. Spritelists, shapes and whatnot.

We can also specify what should be projected into this texture area in the atlas.
By default the projection will be ``(0, width, 0, height)``, but this is not always
what you want (were ``width`` and ``height`` are the region/texture size)

.. code:: python

    # Assuming your window is 800 x 600 we could draw the entire game into this atlas region
    projection = 0, 800, 0, 600
    with spritelist.atlas.render_into(texture, projection=projection) as framebuffer:
        framebuffer.clear()
        # Draw your game here

    # Draw sprite with a texture containing your entire game here

Scrolling can also be applied to projection just like cameras.

.. code:: python

    # Scroll projection (or even zoom)
    projection = 0 + scroll_x, 800 + scroll_x, 0 + scroll_y, 600 + scroll_y

Rendering into an atlas is superior (at least 100 times faster) to updating texture data using Pillow,
but that doesn't mean it's free. We can possibly get away with 50-100 of these per
frame, but this is something you will have to profile.

Debugging
---------

When working with atlases it can be useful to see the contents.
We provide two methods for this.

:py:meth:`arcade.DefaultTextureAtlas.show` will display the atlas using Pillow::

    atlas.show()

:py:meth:`arcade.DefaultTextureAtlas.save` will save the atlas contents to a png file::

    atlas.write("path/to/atlas.png")

Both of these methods will "download" the atlas texture from graphics memory
for you to inspect the raw data.
