.. _text_guide:

Drawing Text
============

Arcade has four ways to draw text:

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Way
     - Best for
     - Cost
   * - :py:func:`arcade.draw_text`
     - Quick prototypes, and a few lines
     - Slowest per line drawn
   * - :py:class:`arcade.Text`
     - Most games: scores, menus, labels
     - Fast to draw, slow to create or change
   * - :py:class:`arcade.TextPool`
     - Many lines that change, without managing ``Text`` objects
     - Like ``Text``
   * - :py:func:`arcade.create_text_sprite`
     - Text that moves, rotates, or scales like a sprite
     - Slow to create, very fast to draw

All of them use the same arguments for the font, size, color and layout.

.. note::

   Text is drawn with the current camera, just like sprites. If you
   scroll the game world with a :py:class:`~arcade.Camera2D`, use a second
   camera for text that should stay in place, such as a score. See
   :ref:`sprite_move_scrolling`.

The numbers on this page were measured on one desktop computer.
Your numbers will differ, but the comparisons between them should hold.

draw_text
---------

:py:func:`arcade.draw_text` draws text in one call, which is handy while
you're getting something working:

.. code-block:: python

    def on_draw(self):
        self.clear()
        arcade.draw_text("Hello, World!", 100, 300, arcade.color.WHITE, 24)

Laying out text is slow, so ``draw_text`` keeps the text it laid out and
reuses it when you draw the same text again. Even so, each call has
overhead, and text that changes every frame, such as a timer, has to be
laid out again every frame. Drawing many lines with ``draw_text`` gets
slow quickly. For anything more than a few lines, use
:py:class:`arcade.Text`. ``draw_text`` reminds you of this with a
:py:class:`~arcade.exceptions.PerformanceWarning`.

Text objects
------------

An :py:class:`arcade.Text` object lays out its text once, when it's
created, and then draws it as often as you like. Create it once, for
example in ``__init__`` or a ``setup`` method, and draw it in ``on_draw``:

.. code-block:: python

    class MyGame(arcade.Window):
        def __init__(self):
            super().__init__()
            self.score = 0
            self.score_text = arcade.Text("Score: 0", 10, 10, arcade.color.WHITE, 16)

        def on_update(self, delta_time):
            self.score_text.text = f"Score: {self.score}"

        def on_draw(self):
            self.clear()
            self.score_text.draw()

What costs what:

* **Creating** a ``Text`` takes around half a millisecond. Don't create
  them every frame.
* **Drawing** one takes a few tens of microseconds.
* **Moving**, **recoloring**, **rotating**, or hiding it is almost free.
  Use :py:attr:`~arcade.Text.position` to change ``x`` and ``y`` together.
* **Changing the text**, font, size, bold, italic, width, or alignment
  lays the text out again, which takes about as long as drawing it
  several times. Setting a property to the value it already has costs nothing,
  so code like the example above only pays when the score changes.

To change several of these at once, use a ``with`` block. The text is
laid out once, at the end of the block, instead of once for each change:

.. code-block:: python

    with self.title:
        self.title.text = "Game Over"
        self.title.font_size = 48
        self.title.color = arcade.color.RED

See :ref:`drawing_text_objects` for an example.

Batches
~~~~~~~

Drawing many ``Text`` objects one at a time adds up. If you add them to a
pyglet :py:class:`~pyglet.graphics.Batch`, one call draws all of them:

.. code-block:: python

    import pyglet

    self.batch = pyglet.graphics.Batch()
    self.lines = [
        arcade.Text(f"Line {i}", 10, 20 * i, batch=self.batch)
        for i in range(20)
    ]

    def on_draw(self):
        self.clear()
        self.batch.draw()

In one measurement, drawing 20 ``Text`` objects one at a time took about
570 µs, and drawing them in one batch took about 30 µs.

You can still change texts in a batch. Set ``text.batch = None`` to take
one out. See :ref:`drawing_text_objects_batch` for an example.

TextPool
--------

If you'd rather write ``draw_text`` style code but want the speed of
``Text`` objects, use a :py:class:`arcade.TextPool`. You give each line
a name, and the pool keeps one ``Text`` object per name, updating it
only when something changes:

.. code-block:: python

    self.pool = arcade.TextPool()

    def on_draw(self):
        self.clear()
        self.pool.draw("score", f"Score: {self.score}", 10, 580, font_size=16)
        self.pool.draw("lives", f"Lives: {self.lives}", 10, 560, font_size=16)

Text sprites
------------

:py:func:`arcade.create_text_sprite` draws text into a texture once and
returns an :py:class:`arcade.Sprite` that shows it. Creating one takes a
few milliseconds, so it's for text that doesn't change, but after that it
draws as fast as any other sprite, and can be added to a
:py:class:`~arcade.SpriteList`, moved, rotated, and scaled:

.. code-block:: python

    self.sprites = arcade.SpriteList()
    label = arcade.create_text_sprite("Bonus!", color=arcade.color.YELLOW, font_size=20)
    label.position = 400, 300
    self.sprites.append(label)

To change the text, create a new sprite. Scaling a text sprite up makes
it blurry, so create it at the size it will be drawn.

Fonts
-----

``font_name`` can be:

* **The name of a font** installed on the computer, such as ``"arial"``.
* **A tuple or list of names.** The first one that's found is used,
  which helps when different computers have different fonts. The default
  is ``("Liberation Sans", "arial")``. Liberation Sans comes with Arcade,
  so text looks the same on every computer.
* **The path to a font file**, such as ``"fonts/MyFont.ttf"``, or a
  :ref:`resource handle <resource_handles>`, such as
  ``":resources:fonts/ttf/MyFont.ttf"``. The file is loaded the first
  time it's used.

If no font is found, the platform's default font is used instead, without
an error. If text shows up in the wrong font, check the name.

Fonts that come with your game
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use a font file by its name, load it first with
:py:func:`arcade.load_font`, and then use the font's name, not the
file name:

.. code-block:: python

    arcade.load_font("fonts/MyFont.ttf")
    text = arcade.Text("Hello", 10, 10, font_name="My Font")

The name is set inside the font file. Your operating system's font
viewer shows it, though some add the style, such as
``"Grand Hotel, Regular"`` for a font named ``"Grand Hotel"``. If you're
not sure of the name, use the file's path as ``font_name`` instead.

Many free fonts, such as most on `Google Fonts <https://fonts.google.com/>`_,
use the SIL Open Font License, which lets you ship them with your game.
Include the font's license file with it. For more about fonts, see pyglet's
:doc:`text guide <pyglet:programming_guide/text>`.

Fonts that come with Arcade
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Arcade includes the Kenney and Liberation fonts. The Liberation fonts
are loaded the first time you use one. Load the Kenney fonts before
using them:

.. code-block:: python

    arcade.resources.load_kenney_fonts()

    text = arcade.Text("Hello", 10, 10, font_name="Kenney Future")

The Kenney fonts are ``"Kenney Blocks"``, ``"Kenney Future"``,
``"Kenney Future Narrow"``, ``"Kenney High"``, ``"Kenney High Square"``,
``"Kenney Mini"``, ``"Kenney Mini Square"``, ``"Kenney Pixel"``,
``"Kenney Pixel Square"``, ``"Kenney Rocket"`` and
``"Kenney Rocket Square"``. The Liberation fonts are
``"Liberation Sans"``, ``"Liberation Serif"`` and ``"Liberation Mono"``,
which can stand in for Arial, Times New Roman and Courier New.

.. note::

   Windows treats ``"Kenney Future Narrow"`` as a narrower width of
   ``"Kenney Future"``, so it can't be found by its own name there. On
   Windows, use ``font_name="Kenney Future"`` with
   ``stretch="semicondensed"`` instead.

See :ref:`drawing_text` for an example with these fonts.

Style
-----

``bold``
    ``True`` or ``False``, or a font weight such as ``"thin"``,
    ``"light"``, ``"medium"``, ``"semibold"``, ``"extrabold"`` or
    ``"black"``. Not every font has every weight. If a font doesn't have
    the one you ask for, a nearby weight is used instead.

``italic``
    ``True`` or ``False``, or ``"oblique"``.

``color``
    Any Arcade color, such as ``arcade.color.WHITE`` or
    ``(255, 128, 0, 200)``. The alpha value makes the text partly
    transparent. For a gradient from the left edge of the text to the
    right, use a :py:class:`pyglet.text.LinearGradient`, which takes two
    RGBA colors:

    .. code-block:: python

        from pyglet.text import LinearGradient

        title = arcade.Text(
            "Arcade", 100, 300, font_size=48,
            color=LinearGradient((255, 0, 0, 255), (0, 0, 255, 255)),
        )

Layout
------

By default, ``x`` and ``y`` are the left end of the text's baseline, the
line most letters sit on. ``anchor_x`` (``"left"``, ``"center"``,
``"right"``) and ``anchor_y`` (``"baseline"``, ``"bottom"``,
``"center"``, ``"top"``) change which point of the text ``x`` and ``y``
refer to. For example, to center a title on the screen:

.. code-block:: python

    title = arcade.Text(
        "My Game", window.width / 2, window.height / 2, font_size=48,
        anchor_x="center", anchor_y="center",
    )

For text that wraps across several lines, set ``multiline=True`` and a
``width`` in pixels. ``align`` (``"left"``, ``"center"``, ``"right"``)
then aligns each line within that width.

To find out how big the text is, use
:py:attr:`~arcade.Text.content_width` and
:py:attr:`~arcade.Text.content_height`, or
:py:attr:`~arcade.Text.left`, :py:attr:`~arcade.Text.right`,
:py:attr:`~arcade.Text.top` and :py:attr:`~arcade.Text.bottom`.

For more options, see the :py:class:`arcade.Text` API documentation.
