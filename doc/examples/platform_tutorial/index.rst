Build Your Own 2D Platformer Game
=================================

*To be presented at the `2019 PyCon`_ in Cleveland, Ohio.*

In this tutorial, use Python and the Arcade library to create your own 2D platformer.
Learn to work with Sprites and the `Tiled Map Editor`_ to create your own games.
Add coins, ramps, moving platforms, enemies, and more.

.. _Tiled Map Editor: https://www.mapeditor.org/
.. _Pycon 2019: https://us.pycon.org/2019/about/

Audience
--------

1) Who is this tutorial for:

* People learning to program and wanting something fun (video games) to create.
* People interested in teaching programming
* People wanting to use Python to create simple games
* Hobbyist programmers who just want to write something fun

2) Students should have enough Python for basic use of:

* Conditionals (if statements)
* Loops (for/while loops)
* Functions
* Classes
* Being able to iterate through lists

Part One - Create a Platformer
------------------------------

Introduction to the Arcade library - 15 minutes

45 minutes - Self-paced tutorial with different steps that cover how to:

Installation
~~~~~~~~~~~~

* Make sure you are using Python 3.6 or greater.
* Install Arcade with ``pip install arcade`` on Windows
  or ``pip3 install arcade`` on Mac/Linux. Or install via a venv.
* Download bundle with images and sounds from `kenney.nl`_

.. _kenney.nl: https://kenney.nl/

Open a Window
~~~~~~~~~~~~~

To begin with, let's open up a blank window.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/01_open_window.py
    :caption: Open a Window
    :linenos:

Add Sprites To Game
~~~~~~~~~~~~~~~~~~~

Sprites are objects that we can interact with on the screen. They are managed with the
``Sprite`` class.

Sprites are stored in a ``SpriteList``. The ``SpriteList`` class has a lot of OpenGL code
behind it, allowing it to quickly draw all the sprites in a batch.

In this version, we show three ways to add sprites. Manually create an individual sprite,
create a lot of sprites in a loop, and via a list of coordinates. (Eventually, we'll show
how to use a map editor.)

.. literalinclude:: ../../../arcade/examples/platform_tutorial/02_draw_sprites.py
    :caption: Place Sprites
    :linenos:
    :emphasize-lines: 11-14, 27-34, 39-43, 45-76, 84-87

Add User Control
~~~~~~~~~~~~~~~~

This adds the ability to move the character around with the keyboard. It also
shows how to use a simplified physics engine to keep the player from moving
through walls.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_user_control.py
    :caption: Control User By Keyboard
    :linenos:
    :emphasize-lines: 16-17, 98-108, 110-120, 122-127

If you are interested in a somewhat better method of keyboard control, see
:ref:`sprite_move_keyboard_better`.

Add Gravity
~~~~~~~~~~~

If you are interested in a side view, rather than a top-down view, you
probably want to add in gravity.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_add_gravity.py
    :caption: Add Gravity
    :linenos:
    :emphasize-lines: 18-19, 87-89, 105-107, 116-119

Add Scrolling
~~~~~~~~~~~~~

Let's not be limited to one screen. Let's scroll around a larger world.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/05_scrolling.py
    :caption: Add Scrolling
    :linenos:
    :emphasize-lines: 21-26, 51-53, 144-184

Add Coins And Sound
~~~~~~~~~~~~~~~~~~~

A game needs some kind of goal. This adds coins to pick up and includes some sound.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/06_coins_and_sound.py
    :caption: Add Coins and Sound
    :linenos:
    :emphasize-lines: 55-57, 71, 99-104, 128, 149-159

Display The Score
~~~~~~~~~~~~~~~~~

Add in a score you your game.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/07_score.py
    :caption: Display The Score
    :linenos:
    :emphasize-lines: 55-56, 71-72, 128-131, 170-171

Explore On Your Own
~~~~~~~~~~~~~~~~~~~

* Practice creating your own layout with different tiles.
* Add background images. See :ref:`sprite_collect_coins_background`
* Add moving platforms. See :ref:`sprite_moving_platforms`
* Add ramps. See :ref:`sprite_ramps`
* Change the character image based on the direction she is facing.
  See :ref:`sprite_face_left_or_right`
* Add instruction and game over screens. See :ref:`instruction_and_game_over_screens`

Part Two - Use a Map Editor
---------------------------

Download and install the `Tiled Map Editor`_. Think about donating, as it is
a wonderful project.

Open a new file:

.. image:: new_file.png

Save it as ``map.tmx``.

Rename the layer "Platforms":

.. image:: platforms.png

Create a new tileset:

.. image:: new_tileset.png

.. image:: new_tileset_02.png

Once you create a new tile, adding tiles to the tileset isn't obvious. Click
the wrench:

.. image:: new_tileset_03.png

Then click the 'plus' and add in your tiles

.. image:: new_tileset_04.png

.. literalinclude:: ../../../arcade/examples/platform_tutorial/08_load_map.py
    :caption: Load a .tmx file from Tiled Map Editor
    :linenos:
    :emphasize-lines: 87-115


* Edit the collision / hitbox of a tile
* Add a sudden death layer (like lava)
* Add enemies

Explore On Your Own
~~~~~~~~~~~~~~~~~~~

* Multiple levels
* Insta-death layer
* Make ramps

Part Three - Spruce It Up
-------------------------


15 minutes - Talk about additional items that could be added to the game

45 minutes - Self paced section where students can:

* Continue their prior work or
* Add explosions
* Add animations
* Add bullets (or something you can shoot)
* Add multiple levels

