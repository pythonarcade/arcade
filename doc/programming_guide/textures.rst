
Textures
========

Introduction
------------

The :py:class:`arcade.Texture` type is how Arcade normally interacts with
images either loaded from disk or created manually. This is basically a
wrapper for PIL/Pillow images including detection for hit box data
using pymunk depending on the selected hit box algorithm. These texture
objects are in other words responsible to provide raw RGBA pixel
data to OpenGL and hit box geometry to the sprite engine.

There is another texture type in Arcade in the lower level
OpenGL API: :py:class:`arcade.gl.Texture2D`. This represents an
actual OpenGL texture and should only be used when dealing
with the low level rendering API.

Textures can be created/loaded before or after the window is created
because they don't interact with OpenGL directly.

Texture Uniqueness
------------------

When a texture is created a ``hash/name`` is required. This should be a unique
string. If two more more textures have the same name we will run into
trouble. When loading textures the absolute path to the file is used
as part of the name including vertical/horizontal/diagonal, size and
other parameter for a truly unique name.

When loading texture through Arcade the name of the texture will be
the absolute path to the image and various parameters such as size,
flipping, xy position etc.

Also remember that the texture class do hit box detection with pymunk
by looking at the raw pixel data. This means for example a texture with
different flipping will be loaded multiple times (or fetched from cache)
because we rely in the transformed pixel data to get the hit box.

Texture Cache
-------------

Arcade is caching texture instances based on the ``name/hash`` attribute
to significantly speed up loading times.

.. code:: python

    # The texture will only be loaded during the first sprite creation
    tex_name = "path/to/sprite.png"
    sprite_1 = arcade.Sprite(tex_name)
    sprite_2 = arcade.Sprite(tex_name)
    sprite_3 = arcade.Sprite(tex_name)
    # Will be loaded and cached because we need fresh pixel data for hit box detection
    sprite_4 = arcade.Sprite(tex_name, flipped_vertically=True)
    # Fetched from cache
    sprite_5 = arcade.Sprite(tex_name, flipped_vertically=True)

The above also applies when using :py:func:`arcade.load_texture` or other
texture loading functions.

Arcade's default texture cache can be cleared using ``arcade.texture.default_texture_cache.flush()``

Custom Textures
---------------

We can manually create textures by creating PIL/Pillow images. How this is done
is entirely up to you. Using the drawing functionality of Pillow or simply
providing raw pixel data from another library/source into a Pillow image.
A random example is getting raw pixel data from matplotlib.

.. code:: python

    # Create a image from raw pixel data from some source
    image = PIL.Image.frombuffer(raw_data)

    # NOTE: Also make sure you use a sane hit_box_algorithm
    texture = arcade.Texture("unique_name", image, hit_box_algorithm=...)

Again, how you create the image is up to you. There are many possibilities
with Pillow.
