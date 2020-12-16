

.. _platformer_part_two:

Step 2 - Add Sprites
--------------------

Our next step is to add some sprites_, which are graphics we can see and interact
with on the screen.

.. _sprites: https://en.wikipedia.org/wiki/Sprite_(computer_graphics)

.. image:: listing_02.png
    :width: 70%

Setup vs. Init
~~~~~~~~~~~~~~

In the next code example, ``02_draw_sprites``,
we'll have both an ``__init__`` method and a
``setup``.

The ``__init__`` creates the variables. The variables are set to values such as
0 or ``None``. The ``setup`` actually creates the object instances, such as
graphical sprites.

I often get the very reasonable question, "Why have two methods? Why not just
put everything into ``__init__``? Seems like we are doing twice the work."
Here's why.
With a ``setup`` method split out, later on we can easily add
"restart/play again" functionality to the game.
A simple call to ``setup`` will reset everything.
Later, we can expand our game with different levels, and have functions such as
``setup_level_1`` and ``setup_level_2``.

Sprite Lists
~~~~~~~~~~~~

Sprites are managed in lists. The ``SpriteList`` class optimizes drawing, movement,
and collision detection.

We are using three logical groups in our game. A ``player_list`` for the player.
A ``wall_list`` for walls we can't move through. And finally a
``coin_list`` for coins we can pick up.

.. code-block::

    self.player_list = arcade.SpriteList()
    self.wall_list = arcade.SpriteList(use_spatial_hash=True)
    self.coin_list = arcade.SpriteList(use_spatial_hash=True)

Sprite lists have an option to use something called "spatial hashing." Spatial
hashing speeds the time it takes to find collisions, but increases the time it
takes to move a sprite. Since I don't expect most of my walls or coins to move,
I'll turn on spatial hashing for these lists. My player moves around a lot,
so I'll leave it off for her.


Add Sprites to the Game
~~~~~~~~~~~~~~~~~~~~~~~

To create sprites we'll use the ``arcade.Sprite`` class.
We can create an instance of the sprite class with code like this:

.. code-block::

    self.player_sprite = arcade.Sprite("images/player_1/player_stand.png", CHARACTER_SCALING)

The first parameter is a string or path to the image you want it to load.
An optional second parameter will scale the sprite up or down.
If the second parameter (in this case a constant ``CHARACTER_SCALING``) is set to
0.5, and the the sprite is 128x128, then both width and height will be scaled
down 50% for a 64x64 sprite.

.. sidebar:: Built-in Resources

    The arcade library has a few built-in :ref:`resources` so we can run
    examples without downloading images. If you see code samples where sprites
    are loaded beginning with "resources", that's what's being referenced.

Next, we need to tell *where* the sprite goes. You can use the attributes
``center_x`` and ``center_y`` to position the sprite. You can also use ``top``,
``bottom``, ``left``, and ``right`` to get or set the sprites location by an
edge instead of the center. You can also use ``position`` attribute to set both the
x and y at the same time.

.. code-block::

    self.player_sprite.center_x = 64
    self.player_sprite.center_y = 120

Finally, all instances of the ``Sprite`` class need to go in a ``SpriteList``
class.

.. code-block::

    self.player_list.append(self.player_sprite)

We manage groups of sprites by the list that they are in.
In the example below there's a ``wall_list`` that will hold everything that the
player character can't walk through, and
a ``coin_list`` for sprites we can pick up to get points. There's also a ``player_list``
which holds only the player.

* Documentation for the `Sprite class <../../arcade.html#arcade.Sprite>`_
* Documentation for the `SpriteList class <../../arcade.html#arcade.SpriteList>`_

Notice that the code creates ``Sprites`` three ways:

* Creating a ``Sprite`` class, positioning it, adding it to the list
* Create a series of sprites in a loop
* Create a series of sprites using coordinates

.. literalinclude:: ../../../arcade/examples/platform_tutorial/02_draw_sprites.py
    :caption: 02_draw_sprites - Draw and Position Sprites
    :linenos:
    :emphasize-lines: 11-14, 27-34, 38-70, 78-81

.. note::

    Once the code example is up and working:

    * Adjust the code and try putting sprites in new positions.
    * Use different images for sprites (see the images folder).
    * Practice placing individually, via a loop, and by coordinates in a list.
