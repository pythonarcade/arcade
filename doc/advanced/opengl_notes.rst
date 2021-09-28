
OpenGL Notes
============

Arcade is using OpenGL for the underlying rendering. OpenGL
functionality is given to use through pyglet when a window
is crated. The underlying representation of this is an
OpenGL context. Arcade's representation of this context
is the :py:attr:`arcade.Window.ctx`. This is an
:py:class:`~arcade.ArcadeContext`.

Working with OpenGL do add some challenges we need to be aware of.

Initialization
--------------

Certain operations can't be done before a window is created.
In Arcade we do deferred initialization in many of our types
to make this as painless as possible for the user.
:py:class:`~arcade.SpriteList` can for example be built before window creation
and will be initialized internally in the first draw call.

:py:class:`~arcade.TextureAtlas` on the other hand cannot
be crated before the window is created, but :py:class:`~arcade.Texture`
can freely be loaded at any time since these only manage
pixel data with Pillow and calculate hit box data on the cpu.

Threads
-------

OpenGL is not thread safe meaning doing actions from
anything but the main thread is not possible. You
can still use threads with arcade, but they cannot
interact with anything that affects OpenGL objects.
This will throw an error immediately.

Another problem with threads is that the garbage
collector might decide to run in a non-main thread
for various reasons. A way to combat this is to change
the garbage collection mode for OpenGL resources

.. code:: python

    # Enable "context_gc" mode (default is "auto") during
    # window creation
    Window(gc_mode="context_gc")

    # From now on you need to manually call ctx.gc()
    # for OpenGL resources to be deleted. This can be
    # done very frame if needed or in shorter intervals
    window.ctx.gc()

Note that if vsync is enabled all threads will stall
when all rendering is done and OpenGL is waiting for
the next vertical blank. The only way to combat this
is to disable vsync or use subprocesses.
