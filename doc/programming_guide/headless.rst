
.. _headless:

Headless Arcade
===============

For some applications, it may be that we want to run Arcade, but not open
up a window. We might want to draw to a buffer and save an image to be
used in a server or data science visualization. In remote cloud operations,
we might not even have a monitor for the computer. Running Arcade this way
is called headless mode.

Arcade can render in `headless mode <https://en.wikipedia.org/wiki/Headless_software>`_
on Linux servers with
`EGL <https://en.wikipedia.org/wiki/EGL_(API)>`_ installed.
This should work both in a desktop environment and on servers and even
in virtual machines. Both software and hardware rendering should
be acceptable depending on your use case.

We are leveraging the headless mode in pyglet. If you are seeking knowledge
about the inner workings of headless, that's the right place to look.

Enabling headless mode
----------------------

Headless mode needs to be configured **before** Arcade is imported.
This can be done in the following ways:

.. code:: py

    # Before Arcade is imported
    import os
    os.environ["ARCADE_HEADLESS"] = "True"

    # The above is a shortcut for
    import pyglet
    pyglet.options.headless = True

This of course also means you can configure headless externally.

.. code:: bash

    $ export ARCADE_HEADLESS=True

To quickly check the enviroment such as renderer and versions::

    $ python -m arcade

    Arcade 2.6.12
    -------------
    vendor: AMD
    renderer: AMD Radeon(TM) Vega 11 Graphics (RAVEN, DRM 3.41.0, 5.13.0-37-generic, LLVM 12.0.0)
    version: (4, 6)
    python: 3.9.9 (main, Dec 20 2021, 08:19:16) 
    [GCC 9.3.0]
    platform: linux

How is this affecting my code?
------------------------------

In headless mode we don't have any window events or inputs events.
This means events like ``on_key_press`` and ``on_mouse_motion``
will never be called. A project not created for a headless setting
will need some tweaking.

In headless mode the arcade :py:class:`~arcade.Window` will extend
pyglet's headless window instead. We've added a property
:py:attr:`arcade.Window.headless` (bool) that can be used to separate
headless logic.

Note that the window itself still has a framebuffer you can render
to and read pixels from. The size of this framebuffer is the size
you specify when creating the window. More framebuffers can be
created through the :py:class:`~arcade.ArcadeContext` if needed.

.. Warning::

    If you are creating and destroying a lot of Arcade objects
    you might want to look into :py:attr:`arcade.gl.Context.gc_mode`.
    In Arcade we normally do garbage collection of OpenGL objects
    once per frame by calling :py:meth:`~arcade.gl.Context.gc`.

Examples
--------

There are two recommended approaches: :ref:`simple_headless_approach`
and :ref:`extend_arcade_window_headless`.

.. _simple_headless_approach:

Simple headless mode
~~~~~~~~~~~~~~~~~~~~

For simpler applications we don't need to subclass the window. 

.. code:: py

    # Configure headless before importing arcade
    import os
    os.environ["ARCADE_HEADLESS"] = "true"
    import arcade

    # Create a 100 x 100 headless window
    window = arcade.open_window(100, 100)

    # Draw a quick rectangle
    arcade.draw_rectangle_filled(50, 50, 50, 50, color=arcade.color.AMAZON)

    # Dump the framebuffer to a png
    image = arcade.get_image(0, 0, *window.get_size())
    image.save(f"framebuffer.png")

You are free to :py:meth:`~arcade.Window.clear` the window and render
new contents at any time.

.. _extend_arcade_window_headless:

Headless mode while extending the Arcade Window
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For Arcade users extending the window, this method makes more sense.
The :py:meth:`~arcade.run` method supports headless
mode and will emulate Pyglet's event loop by calling
``on_update``, ``on_draw`` and ``flip()`` (swap buffers)
in a loop until you close the window.

.. code:: py

    import os
    os.environ["ARCADE_HEADLESS"] = "true"
    import arcade

    class App(arcade.Window):

        def __init__(self):
            super().__init__(200, 200)
            self.frame = 0
            self.sprite = arcade.Sprite(
                ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
                center_x=self.width / 2,
                center_y=self.height / 2,
            )

        def on_draw(self):
            self.clear()
            arcade.draw_sprite(self.sprite)

            # Dump the window framebuffer to disk
            image = arcade.get_image(0, 0, *self.get_size())
            image.save("framebuffer.png")

        def on_update(self, delta_time: float):
            # Close the window on the second frame
            if self.frame == 2:
                self.close()

            self.frame += 1

    App().run()

You can also split your code into :py:class:`arcade.View` classes
if needed. Doing it this way might make it simpler to work
with headless and non-headless mode during development. You just
need to programmatically close the window and switch views.
We can easily separate logic with the :py:attr:`arcade.Window.headless`
flag. When calling ``run()`` we also garbage collect OpenGL
resources every frame.

Advanced
--------

The lower level rendering API is of course still available
through :py:attr:`arcade.Window.ctx`. It exposes methods
to create framebuffers, textures, shaders (including compute shaders)
and other higher level wrappers over OpenGL types.

When working in a multi-gpu environment you can also select
a specific device id. This is 0 by default and must be set
before the window is created. These device ids usually refers
to a physical device (graphics card) or a virtual card/device.

.. code:: py

    # Default setting
    pyglet.options.headless_device = 0

    # Use the second gpu/device
    pyglet.options.headless_device = 1

Issues?
-------

If you run into issues or have questions please
create an issue on github or join our discord server.
