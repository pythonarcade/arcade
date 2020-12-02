.. _platformer_tutorial:

Simple Platformer
=================

.. image:: intro_screen.png
    :width: 70%

Use Python and the Arcade_ library to create a 2D platformer game.
Learn to work with Sprites and the `Tiled Map Editor`_ to create your own games.
Add coins, ramps, moving platforms, enemies, and more.

.. _Tiled Map Editor: https://www.mapeditor.org/
.. _Arcade: http://arcade.academy

The tutorial is divided into these parts:

* :ref:`platformer_part_one`
* :ref:`platformer_part_two`
* :ref:`platformer_part_three`
* :ref:`platformer_part_four`
* :ref:`platformer_part_five`
* :ref:`platformer_part_six`
* :ref:`platformer_part_seven`
* :ref:`platformer_part_eight`
* :ref:`platformer_part_nine`
* :ref:`platformer_part_ten`
* :ref:`platformer_part_eleven`


.. _platformer_part_one:

Step 1 - Install and Open a Window
----------------------------------

Our first step is to make sure everything is installed, and that we can at least
get a window open.

Installation
~~~~~~~~~~~~
* Make sure Python is installed. `Download Python here <https://www.python.org/downloads/>`_
  if you don't already have it.
* `Download this bundle with code, images, and sounds <../../_static/platform_tutorial.zip>`_.
  (Images are from `kenney.nl`_.)
  Your file structure should look like:

.. image:: file_structure.png
    :scale: 75%

* Make sure the `Arcade library <https://pypi.org/project/arcade/>`_ is installed.

  * Install Arcade with ``pip install arcade`` on Windows
    or ``pip3 install arcade`` on Mac/Linux. Or install by using a venv.
  * Here are the longer, official :ref:`installation-instructions`.

I highly recommend using the free community edition of PyCharm as an editor.
If you do, see :ref:`install-pycharm`.

.. _kenney.nl: https://kenney.nl/


Open a Window
~~~~~~~~~~~~~

The example below opens up a blank window. Set up a project and get the code
below working. (It is also in the zip file as
``01_open_window.py``.)

.. note::

  This is a fixed-size window. It is possible to have  a
  :ref:`resizable_window` or a :ref:`full_screen_example`, but there are more
  interesting things we can do first. Therefore we'll stick with a fixed-size
  window for this tutorial.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/01_open_window.py
    :caption: 01_open_window.py - Open a Window
    :linenos:

Once you get the code working, figure out how to:

* Change the screen size
* Change the title
* Change the background color

  * See the documentation for :ref:`color`
  * See the documentation for :ref:`csscolor`

* Look through the documentation for the
  `Window <../../arcade.html#arcade.Window>`_ class to get an idea of everything
  it can do.

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

.. _platformer_part_three:

Step 3 - Add User Control
-------------------------

Now we need to be able to get the user to move around.

First, at the top of the program add a constant that controls how many pixels
per update our character travels:

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_user_control.py
    :caption: 03_user_control.py - Player Move Speed Constant
    :lines: 16-17

Next, at the end of our ``setup`` method, we are need to create a physics engine that will
move our player and keep her from running through walls. The ``PhysicsEngineSimple``
class takes two parameters: The moving
sprite, and a list of sprites the moving sprite can't move through.

For more information about the physics engine we are using here, see
`PhysicsEngineSimple class <../../arcade.html#arcade.PhysicsEngineSimple>`_

.. note::

    It is possible to have multiple physics engines, one per moving sprite. These
    are very simple, but easy physics engines. See
    :ref:`pymunk_platformer_tutorial` for a more advanced physics engine.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_user_control.py
    :caption: 03_user_control.py - Create Physics Engine
    :lines: 16-17

Each sprite has ``center_x`` and ``center_y`` attributes. Changing these will
change the location of the sprite. (There are also attributes for top, bottom,
left, right, and angle that will move the sprite.)

Each sprite has ``change_x`` and ``change_y`` variables. These can be used to
hold the velocity that the sprite is moving with. We will adjust these
based on what key the user hits. If the user hits the right arrow key
we want a positive value for ``change_x``. If the value is 5, it will move
5 pixels per frame.

In this case, when the user presses a key we'll change the sprites change x and y.
The physics engine will look at that, and move the player unless she'll hit a wall.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_user_control.py
    :caption: 03_user_control.py - Handle key-down
    :linenos:
    :pyobject: MyGame.on_key_press

On releasing the key, we'll put our speed back to zero.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_user_control.py
    :caption: 03_user_control.py - Handle key-up
    :linenos:
    :pyobject: MyGame.on_key_release

.. note::

    This method of tracking the speed to the key the player presses is simple, but
    isn't perfect. If the player hits both left and right keys at the same time,
    then lets off the left one, we expect the player to move right. This method won't
    support that. If you want a slightly more complex method that does, see
    :ref:`sprite_move_keyboard_better`.

Our ``on_update`` method is called about 60 times per second. We'll ask the physics
engine to move our player based on her ``change_x`` and ``change_y``.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_user_control.py
    :caption: 03_user_control.py - Update the sprites
    :linenos:
    :pyobject: MyGame.on_update

* :ref:`03_user_control`
* :ref:`03_user_control_diff`

.. _platformer_part_four:

Step 4 - Add Gravity
--------------------

The example above works great for top-down, but what if it is a side view with
jumping? We need to add gravity. First, let's define a constant to represent the
acceleration for gravity, and one for a jump speed.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_add_gravity.py
    :caption: 04_add_gravity.py - Add Gravity
    :lines: 18-19

At the end of the ``setup`` method, change the physics engine to
``PhysicsEnginePlatformer`` and include gravity as a parameter.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_add_gravity.py
    :caption: 04_add_gravity.py - Add Gravity
    :lines: 80-83

Then, modify the key down and key up event handlers. We'll remove the up/down
statements we had before, and make 'UP' jump when pressed.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_add_gravity.py
    :caption: 04_add_gravity.py - Add Gravity
    :lines: 96-113
    :linenos:
    :emphasize-lines: 4-6

.. note::

    You can change how the user jumps by changing the gravity and jump constants.
    Lower values for both will make for a more "floaty" character. Higher values make
    for a faster-paced game.

* :ref:`04_add_gravity`
* :ref:`04_add_gravity_diff`

.. _platformer_part_five:

Step 5 - Add Scrolling
----------------------

We can have our window be a small viewport into a much larger world by adding
scrolling.

The viewport margins control how close you can get to the edge of the screen
before the camera starts scrolling.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/05_scrolling.py
    :caption: Add Scrolling
    :linenos:
    :emphasize-lines: 21-26, 51-53, 137-177

.. note::

    Work at changing the viewport margins to something that you like.

.. _platformer_part_six:

Step 6 - Add Coins And Sound
----------------------------

.. image:: listing_06.png
    :width: 70%

The code below adds coins that we can collect. It also adds a sound to be played
when the user hits a coin, or presses the jump button.

We check to see if the user hits a coin by the ``arcade.check_for_collision_with_list``
function. Just pass the player sprite, along with a ``SpriteList`` that holds
the coins. The function returns a list of coins in contact with the player sprite.
If no coins are in contact, the list is empty.

The method ``Sprite.remove_from_sprite_lists`` will remove that sprite from all
lists, and effectively the game.

Notice that any transparent "white-space" around the image counts as the hitbox.
You can trim the space in a graphics editor, or in the second section,
we'll show you how to specify the hitbox.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/06_coins_and_sound.py
    :caption: Add Coins and Sound
    :linenos:
    :emphasize-lines: 55-57, 71, 100-105, 120, 129, 149-158

.. note::

    Spend time placing the coins where you would like them.
    If you have extra time, try adding more than just coins. Also add gems or keys
    from the graphics provided.

    You could also subclass the coin sprite and add an attribute for a score
    value. Then you could have coins worth one point, and gems worth 5, 10, and
    15 points.

.. _platformer_part_seven:

Step 7 - Display The Score
--------------------------

Now that we can collect coins and get points,
we need a way to display the score on the screen.

This is a bit more complex
than just drawing the score at the same x, y location every time because
we have to "scroll" the score right with the player if we have a scrolling
screen. To do this, we just add in the ``view_bottom`` and ``view_left`` coordinates.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/07_score.py
    :caption: Display The Score
    :linenos:
    :emphasize-lines: 55-56, 71-72, 129-132, 170-171

.. note::

    You might also want to add:

    * A count of how many coins are left to be collected.
    * Number of lives left.
    * A timer: :ref:`timer`
    * This example shows how to add an FPS timer: :ref:`stress_test_draw_moving`

Explore On Your Own
~~~~~~~~~~~~~~~~~~~

* Practice creating your own layout with different tiles.
* Add background images. See :ref:`sprite_collect_coins_background`
* Add moving platforms. See :ref:`sprite_moving_platforms`
* Change the character image based on the direction she is facing.
  See :ref:`sprite_face_left_or_right`
* Add instruction and game over screens.

.. _platformer_part_eight:

Step 8 - Use a Map Editor
-------------------------

.. image:: use_tileset.png
    :width: 70%

Create a Map File
~~~~~~~~~~~~~~~~~

For this part, we'll restart with a new program. Instead of placing our tiles
by code, we'll use a map editor.

Download and install the `Tiled Map Editor`_. (Think about donating, as it is
a wonderful project.)

Open a new file with options similar to these:

* Orthogonal - This is a normal square-grid layout. It is the only version that
  Arcade supports very well at this time.
* Tile layer format - This selects how the data is stored inside the file. Any option works, but Base64
  zlib compressed is the smallest.
* Tile render order - Any of these should work. It simply specifies what order the tiles are
  added. Right-down has tiles added left->right and top->down.
* Map size - You can change this later, but this is your total grid size.
* Tile size - the size, in pixels, of your tiles. Your tiles all need to be the same size.
  Also, rendering works better if the tile size is a power of 2, such as
  16, 32, 64, 128, and 256.

.. image:: new_file.png
   :scale: 80%

Save it as ``map.tmx``.

Rename the layer "Platforms". We'll use layer names to load our data later. Eventually
you might have layers for:

* Platforms that you run into (or you can think of them as walls)
* Coins or objects to pick up
* Background objects that you don't interact with, but appear behind the player
* Foreground objects that you don't interact with, but appear in front of the player
* Insta-death blocks (like lava)
* Ladders

.. Note::

    Once you get multiple layers it is VERY easy to add items to the wrong
    layer.

.. image:: platforms.png
   :scale: 80%

Create a Tileset
~~~~~~~~~~~~~~~~

Before we can add anything to the layer we need to create a set of tiles.
This isn't as obvious or intuitive as it should be. To create a new tileset
click "New Tileset" in the window on the lower right:

.. image:: new_tileset.png
   :scale: 80%

Right now, Arcade only supports a "collection of images" for a tileset.
I find it convenient to embed the tileset in the map.

.. image:: new_tileset_02.png
   :scale: 80%

Once you create a new tile, the button to add tiles to the tileset is
hard to find. Click the wrench:

.. image:: new_tileset_03.png
   :scale: 80%

Then click the 'plus' and add in your tiles

.. image:: new_tileset_04.png
   :scale: 80%

Draw a Level
~~~~~~~~~~~~

At this point you should be able to "paint" a level. At the very least, put
in a floor and then see if you can get this program working. (Don't put
in a lot of time designing a level until you are sure you can get it to
load.)

The program below assumes there are layers created by the tiled
map editor for for "Platforms" and "Coins".

Test the Level
~~~~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/08_load_map.py
    :caption: Load a .tmx file from Tiled Map Editor
    :linenos:
    :emphasize-lines: 88-117

.. note::

    You can set the **background color** of the map by selecting "Map...Map Properties".
    Then click on the three dots to pull up a color picker.

    You can edit the **hitbox** of a tile to make ramps
    or platforms that only cover a portion of the rectangle in the grid.

    To edit the hitbox, use the polygon tool (only) and draw a polygon around
    the item. You can hold down "CTRL" when positioning a point to get the exact
    corner of an item.

    .. image:: collision_editor.png
       :scale: 20%

.. _platformer_part_nine:

Step 9 - Multiple Levels and Other Layers
-----------------------------------------

Here's an expanded example:

* This adds foreground, background, and "Don't Touch" layers.

  * The background tiles appear behind the player
  * The foreground appears in front of the player
  * The Don't Touch layer will reset the player to the start (228-237)

* The player resets to the start if they fall off the map (217-226)
* If the player gets to the right side of the map, the program attempts to load another layer

  * Add ``level`` attribute (69-70)
  * Updated ``setup`` to load a file based on the level (76-144, specifically lines 77 and 115)
  * Added end-of-map check(245-256)

.. literalinclude:: ../../../arcade/examples/platform_tutorial/09_endgame.py
    :caption: More Advanced Example
    :linenos:
    :emphasize-lines: 69-70, 77, 114-115, 248-259

.. note::

    What else might you want to do?

    * :ref:`sprite_enemies_in_platformer`
    * :ref:`sprite_face_left_or_right`
    * Bullets (or something you can shoot)

      * :ref:`sprite_bullets`
      * :ref:`sprite_bullets_aimed`
      * :ref:`sprite_bullets_enemy_aims`

    * Add :ref:`sprite_explosion_bitmapped`
    * Add :ref:`sprite_move_animation`

.. _platformer_part_ten:

Step 10 - Add Ladders, Properties, and a Moving Platform
--------------------------------------------------------

.. image:: 10_ladders_and_more.png
   :scale: 40%

This example shows using:

* Ladders
* Properties to define point value of coins and flags
* Properties and an object layer to define a moving platform.

To create a moving platform using TMX editor, there are a few steps:

1. Define an **object layer** instead of a tile layer.
2. Select **Insert Tile**
3. Select the tile you wish to insert.
4. Place the tile.
5. Add custom properties. You can add:

  * ``change_x``
  * ``change_y``
  * ``boundary_bottom``
  * ``boundary_top``
  * ``boundary_left``
  * ``boundary_right``

.. image:: moving_platform_setup.png

.. literalinclude:: ../../../arcade/examples/platform_tutorial/10_ladders_and_more.py
    :caption: Ladders, Animated Tiles, and Moving Platforms
    :linenos:

.. _platformer_part_eleven:

Step 11 - Add Character Animations, and Better Keyboard Control
---------------------------------------------------------------

Add character animations!

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/TZtXhqDOLy0" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

.. literalinclude:: ../../../arcade/examples/platform_tutorial/11_animate_character.py
    :caption: Animate Characters
    :linenos:
