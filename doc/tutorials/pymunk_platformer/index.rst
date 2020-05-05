.. _pymunk_platformer_tutorial:

Pymunk Platformer Tutorial
==========================

.. warning::

    This tutorial requires Arcade version 2.4, which is currently in Alpha.
    You'll need to specifically install it, as 2.3 will be default. The API
    for the Pymunk interface is still subject to change.

This tutorial covers how to write a platformer using Arcade and its Pymunk API.
This tutorial assumes the you are somewhat familiar with Python, Arcade, and
the `Tiled Map Editor`_.

.. _Tiled Map Editor: https://www.mapeditor.org/

* If you aren't familiar with programming in Python, check out https://learn.arcade.academy
* If you aren't familiar with the Arcade library, work through the :ref:`platformer_tutorial`.
* If you aren't familiar with the Tiled Map Editor, the :ref:`platformer_tutorial`
  also introduces how to create a map with the Tiled Map Editor.

Open a Window
-------------

To begin with, let's start with a program that will use Arcade to open a blank
window. It also has stubs for methods we'll fill in later. Try this code and make
sure you can run it. It should pop open a black window.

.. literalinclude:: pymunk_demo_platformer_01.py
    :caption: Starting Program
    :linenos:

Now let's set up the ``import`` statements, and define the constants we are going
to use. In this case, we've got sprite tiles that are 128x128 pixels. They are
scaled down to 50% of the width and 50% of the height (scale of 0.5). The screen
size is set to 25x15 grid.

To keep things simple, this example will not scroll the screen with the player.
See :ref:`platformer_tutorial` or :ref:`sprite_move_scrolling`.

When you run this program, the screen should be larger.

.. literalinclude:: pymunk_demo_platformer_02.py
    :caption: Adding some constance
    :linenos:
    :emphasize-lines: 4-27

Create Constants
----------------

Next, let's create instance variables we are going to use, and set a background
color that's green: ``arcade.color.AMAZON``

If you aren't familiar with type-casting on Python, you might not be familiar with
lines of code like this:

.. code-block:: python

    self.player_list: Optional[arcade.SpriteList] = None

This means the ``player_list`` attribute is going to be an instance of
``SpriteList`` or ``None``. If you don't want to mess with typing, then
this code also works just as well:

.. code-block::

    self.player_list = None

Running this program should show the same window, but with a green background.

.. literalinclude:: pymunk_demo_platformer_03.py
    :caption: Create instance variables
    :linenos:
    :emphasize-lines: 34-53

Load and Display Map
--------------------

To get started, create a map with the Tiled Map Editor. Place items that
you don't want to move, and to act as platforms in a layer named "Platforms".
Place items you want to push around in a layer called "Dynamic Items". Name the
file "pymunk_test_map.tmx" and place in the exact same directory as your code.

.. image:: tiled_map.png
    :width: 75%

Now, in the ``setup`` function, we are going add code to:

* Create instances of ``SpriteList`` for each group of sprites we are doing
  to work with.
* Create the player sprite.
* Read in the tiled map.
* Make sprites from the layers in the tiled map.

.. note::

    When making sprites from the tiled map layer, the name of the layer you
    load must match **exactly** with the layer created in the tiled map editor.
    It is case-sensitive.

There's no point in having sprites if we don't draw them, so in the ``on_draw``
method, let's draw out sprite lists.

With the additions in the program below, running your program should show the
tiled map you created:

.. image:: pymunk_demo_platformer_04.png
    :width: 75%

.. literalinclude:: pymunk_demo_platformer_04.py
    :caption: Creating and drawing our sprites
    :linenos:
    :emphasize-lines: 58-81, 95-101

Add Physics Engine
------------------

The next step is to add in the physics engine.

First, add some constants for our physics. Here we are setting:

* A constant for the force of gravity
* Values for "damping". A damping of 1.0 will cause an item to lose all it's
  velocity once a force no longer applies to it. A damping of 0.5 causes 50% of
  speed to be lost in 1 second. A value of 0 is free-fall.
* Values for friction. 0.0 is ice, 1.0 is like rubber.
* Mass. Item default to 1. We make the player 2, so she can push items around
  easier.
* Limits are the players horizontal and vertical speed. It is easier to play if
  the player is limited to a constant speed. And more realistic, because they
  aren't on wheels.

Second, in the ``setup`` method we create the physics engine and add the sprites.
The player, walls, and dynamic items all have different properties so they are
added individually.

Third, in the ``on_update`` method we call the physics engine's ``step`` method.

If you run the program, and you have dynamic items that are up in the air, you
should see them fall when the game starts.

.. literalinclude:: pymunk_demo_platformer_05.py
    :caption: Add Physics Engine
    :linenos:
    :emphasize-lines: 29-48, 103-154, 166

Add Player Movement
-------------------

(To be done)

Edit Hit-Boxes in Tiled Map Editor
---------------------------------

Add Bullets
-----------

(To be done)

Destroy Bullets and Items
-------------------------

(To be done)

Add Moving Platforms
--------------------

(To be done)