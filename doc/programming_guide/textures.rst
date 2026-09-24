
Textures
========

Introduction
------------

The :py:class:`arcade.Texture` type is how Arcade normally interacts with
images either loaded from disk or created manually. This is basically a
wrapper for PIL/Pillow images including detection for hit box data
using pymunk depending on the selected hit box algorithm. These texture objects are responsible for providing raw RGBA pixel
data to OpenGL and hit box geometry used when rendering sprites.

There is another texture type in Arcade in the lower level
OpenGL API: :py:class:`arcade.gl.Texture2D`. This represents an
actual OpenGL texture and should only be used when dealing
with the low level rendering API.

Textures can be created/loaded before or after the window is created
because they don't interact with OpenGL directly.

Texture Layers
--------------

Textures in Arcade interact with several layers of the rendering system:

* **Arcade (Python / RAM)**  
  The :py:class:`arcade.Texture` object stores image data and metadata
  in system memory, including raw pixel data and hit box information.

* **pyglet**  
  Arcade relies on pyglet to manage the window and communicate with the
  graphics system.

* **OpenGL / GPU**  
  When rendering occurs, the texture data is uploaded to the GPU so it
  can be used efficiently when drawing sprites.

Texture Uniqueness
------------------

Each texture in Arcade has a ``name`` (sometimes referred to as a hash)
that uniquely identifies it in the texture cache. This value is used as
the cache key when textures are loaded or created.

A *unique* name means that no two textures should share the same
identifier. If multiple textures use the same name, the cache may return
the wrong texture instance. This can lead to incorrect sprite rendering
or invalid hit box data.

When textures are loaded from files using functions such as
:py:func:`arcade.load_texture`, Arcade automatically generates a unique
name based on several pieces of information, including:

* The absolute path to the image file
* The selected image region or size
* Flipping options (horizontal, vertical, or diagonal)
* Other transformation parameters

Using the absolute file path ensures that textures loaded from
different relative paths still resolve to the same cached texture.

Flipping options also affect the generated name. For example,
loading a texture with ``flipped_vertically=True`` produces a different
texture instance because the underlying pixel data changes. This is
important because hit box detection relies on the transformed pixel
data.

For implementation details, see the texture loading logic in
``arcade/cache/texture.py``.

Texture Cache
-------------

Each :py:class:`arcade.Texture` has a ``name`` attribute that uniquely
identifies it. Arcade uses this attribute in the
:py:class:`arcade.cache.TextureCache` to speed up texture loading.

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

Arcade stores texture instances in the default texture cache
(:py:class:`arcade.cache.TextureCache`). To clear all cached textures,
use the :py:meth:`arcade.cache.TextureCache.flush` method:

.. code:: python

    arcade.texture.default_texture_cache.flush()

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
