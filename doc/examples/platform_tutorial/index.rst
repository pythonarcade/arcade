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
* Make sure Python and the Arcade library are installed
* Download bundle with images from kenney.nl

Open a Window
~~~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/01_open_window.py
    :caption: Open a Window
    :linenos:

Add Sprites To Game
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/02_draw_sprites.py
    :caption: Place Sprites
    :linenos:
    :emphasize-lines: 11-14, 27-34, 39-43, 45-76, 84-87

Add User Control
~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_user_control.py
    :caption: Control User By Keyboard
    :linenos:
    :emphasize-lines: 16-17, 98-108, 110-120, 122-127

Add Gravity
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/04_add_gravity.py
    :caption: Add Gravity
    :linenos:
    :emphasize-lines: 18-19, 87-89, 105-107, 116-119

Add Scrolling
~~~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/05_scrolling.py
    :caption: Add Scrolling
    :linenos:
    :emphasize-lines: 21-26, 51-53, 144-184


* Add coins layer for the player to pick up
* Fast-paced users may also experiment with sound, background images, moving platforms, and ramps.

Part Two - Use a Map Editor
---------------------------

15 minutes - Talk about using a map editor. Demo and point out the important parts.

45 minutes - Self-paced tutorial with the following steps:

* Install the Tiled map editor
* Used the tiled map editor to create a map
* Create a layer with coins to pick up
* Edit the collision / hitbox of a tile
* Add a sudden death layer (like lava)
* Add enemies

Part Three - Spruce It Up
-------------------------


15 minutes - Talk about additional items that could be added to the game

45 minutes - Self paced section where students can:

* Continue their prior work or
* Add explosions
* Add animations
* Add bullets (or something you can shoot)
* Add multiple levels

