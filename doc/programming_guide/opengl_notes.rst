.. _open_gl_notes:

OpenGL
======

Arcade is using OpenGL for the underlying rendering. OpenGL
functionality is given to use through pyglet when a window
is crated. The underlying representation of this is an
OpenGL context. Arcade's representation of this context
is the :py:attr:`arcade.Window.ctx`. This is an
:py:class:`~arcade.ArcadeContext`.

Working with OpenGL adds some challenges we need to be aware of.

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

Garbage Collection & Threads
----------------------------

OpenGL is not thread safe meaning doing actions from
anything but the main thread is not possible. You
can still use threads with arcade, but they cannot
interact with anything that affects OpenGL objects.
This will throw an error immediately.

When threads are used in a project or underlying libraries
there is always the risk that Python's garbage collector
will run outside the main thread. This is just how Python's
garbage collector works.

For this reason, Arcade's default garbage collection mode
requires actively releasing OpenGL objects. We are doing
this for you in the :py:meth:`arcade.Window.flip` method that is
automatically called every frame.

This garbage collection mode is called ``context_gc``
since dead OpenGL objects are collected in the context
and only released when ``ctx.gc()`` is called.

Garbage collection modes can be configured during
window creation or changed runtime in the context.

.. code:: python

    # auto mode works like python's garbage collection (but more risky)
    window = Window(gc_mode="auto")

    # This context mode is implied by default
    window = Window(gc_mode="context_gc")
    # From now on you need to manually call window.ctx.gc()
    # for OpenGL resources to be deleted. This can be
    # done very frame if needed or in shorter intervals
    num_released = window.ctx.gc()
    print("Resources released:", num_released)

    # Change gc mode runtime
    window.gc_mode = "auto"
    window.gc_mode = "context_gc"

If you for some reason need garbage collection to run more
often than once per frame it can safely be called as many
times as you want from the main thread.

In the vast majority of cases this is nothing you need to
be worried about. The current default exists to make your
life as easy as possible.

Threads & vsync
---------------

Note that if vsync is enabled all threads will stall
when all rendering is done and OpenGL is waiting for
the next vertical blank. The only way to combat this
is to disable vsync or use sub-processes.

SpriteList & Threads
--------------------

SpriteLists can be created in threads if they are
created with the ``lazy=True`` parameters.
This ensures OpenGL resources are not created until the
first ``draw()`` call or ``initialize()`` is called.

.. _prog-guide-gl-buffer-protocol-typing:

Writing Raw Bytes to GL Buffers & Textures
-----------------------------------------------------------

Many of arcade's OpenGL classes support creation from or writing to
any object that supports the
`buffer protocol <https://docs.python.org/3/c-api/buffer.html>`_.
The classes most useful to end users are:

* :py:meth:`arcade.gl.Buffer <arcade.gl.Buffer.write>`
* :py:meth:`arcade.gl.Texture <arcade.gl.Texture.write>`

This functionality can be used for displaying the results of
calculations such as:

* Scientific visualizations displaying data from numpy arrays
* Simple console emulators drawing their internal screen buffer

There should be no typing issues when using Python's built-in buffer
protocol objects as arguments to the ``write`` method of arcade's GL
objects. We list these built-in types in the
``arcade.arcade_types.BufferProtocol``
`Union <https://docs.python.org/3/library/typing.html#typing.Union>`_
type.

For objects from third-party libraries, your type checker may warn you
about type mismatches. This is because Python will not support general
annotations for buffer protocol objects until
`version 3.12 at the earliest <https://peps.python.org/pep-0688/>`_.

In the meantime, there are workarounds for users who want to write to
arcade's GL objects from third-party buffer protocol objects:

* use the `typing.cast <https://docs.python.org/3/library/typing.html#typing.cast>`_
  method to convert the object's type for the linter
* use ``# type: ignore`` to silence the warnings
