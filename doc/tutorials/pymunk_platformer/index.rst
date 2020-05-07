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


Create Constants
----------------

Now let's set up the ``import`` statements, and define the constants we are going
to use. In this case, we've got sprite tiles that are 128x128 pixels. They are
scaled down to 50% of the width and 50% of the height (scale of 0.5). The screen
size is set to 25x15 grid.

To keep things simple, this example will not scroll the screen with the player.
See :ref:`platformer_tutorial` or :ref:`sprite_move_scrolling`.

When you run this program, the screen should be larger.

.. literalinclude:: pymunk_demo_platformer_02.py
    :caption: Adding some constants
    :linenos:
    :lines: 1-29
    :emphasize-lines: 4-26

* :ref:`pymunk_demo_platformer_02`
* :ref:`pymunk_demo_platformer_02_diff`

Create Instance Variables
-------------------------

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
    :lines: 29-52
    :emphasize-lines: 10-24

* :ref:`pymunk_demo_platformer_03`
* :ref:`pymunk_demo_platformer_03_diff`

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

.. literalinclude:: pymunk_demo_platformer_04.py
    :caption: Creating our sprites
    :linenos:
    :lines: 54-80

There's no point in having sprites if we don't draw them, so in the ``on_draw``
method, let's draw out sprite lists.

.. literalinclude:: pymunk_demo_platformer_04.py
    :caption: Drawing our sprites
    :linenos:
    :lines: 94-100

With the additions in the program below, running your program should show the
tiled map you created:

.. image:: pymunk_demo_platformer_04.png
    :width: 75%

* :ref:`pymunk_demo_platformer_04`
* :ref:`pymunk_demo_platformer_04_diff`

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

.. literalinclude:: pymunk_demo_platformer_05.py
    :caption: Add Constants for Physics
    :linenos:
    :lines: 28-47

Second, in the ``setup`` method we create the physics engine and add the sprites.
The player, walls, and dynamic items all have different properties so they are
added individually.

.. literalinclude:: pymunk_demo_platformer_05.py
    :caption: Add Sprites to Physics Engine in 'setup' Method
    :linenos:
    :lines: 102-153

Third, in the ``on_update`` method we call the physics engine's ``step`` method.

.. literalinclude:: pymunk_demo_platformer_05.py
    :caption: Add Sprites to Physics Engine in 'setup' Method
    :linenos:
    :lines: 163-165

If you run the program, and you have dynamic items that are up in the air, you
should see them fall when the game starts.

* :ref:`pymunk_demo_platformer_05`
* :ref:`pymunk_demo_platformer_05_diff`

Add Player Movement
-------------------

Next step is to get the player moving. In this section we'll cover how
to move left and right. In the next section we'll show how to jump.

The force that we will move the player is defined as ``PLAYER_MOVE_FORCE_ON_GROUND``.
We'll apply a different force later, if the player happens to be airborne.

.. literalinclude:: pymunk_demo_platformer_06.py
    :caption: Add Player Movement - Constants and Attributes
    :linenos:
    :lines: 49-72
    :emphasize-lines: 1-2, 22-24

We need to track if the left/right keys are held down. To do this we define
instance variables ``left_pressed`` and ``right_pressed``. These are set to
appropriate values in the key press and release handlers.

.. literalinclude:: pymunk_demo_platformer_06.py
    :caption: Handle Key Up and Down Events
    :linenos:
    :lines: 158-172
    :emphasize-lines: 4-7, 12-15

Finally, we need to apply the correct force in ``on_update``. Force is specified
in a tuple with horizontal force first, and vertical force second.

We also set the friction when we are moving to zero, and when we are not moving to
1. This is important to get realistic movement.

.. literalinclude:: pymunk_demo_platformer_06.py
    :caption: Apply Force to Move Player
    :linenos:
    :lines: 174-195
    :emphasize-lines: 4-19


* :ref:`pymunk_demo_platformer_06`
* :ref:`pymunk_demo_platformer_06_diff`

Add Player Jumping
------------------

To get the player to jump we need to:

* Make sure the player is on the ground
* Apply an impulse force to the player upward
* Change the left/right force to the player while they are in the air.

We can see if a sprite has a sprite below it with the ``is_on_ground`` function.
Otherwise we'll be able to jump while we are in the air.
(Double-jumps would allow this once.)

If we don't allow the player to move left-right while in the air, they player
will be very hard to control. If we allow them to move left/right with the same
force as on the ground, that's typically too much. So we've got a different
left/right force depending if we are in the air or not.

.. literalinclude:: pymunk_demo_platformer_07.py
    :caption: Add Player Movement
    :linenos:
    :emphasize-lines: 52-53, 55-56, 171-176, 192-195, 200-203

* :ref:`pymunk_demo_platformer_07`
* :ref:`pymunk_demo_platformer_07_diff`

Add Player Animation
--------------------

To create a player animation, we make a custom child class of ``Sprite``.
We load each frame of animation that we need, including a mirror image of it.

Any sprite moved by the Pymunk engine will have its ``pymunk_moved`` method
called. This can be used to update the animation.

Because the physics engine works with small floating point numbers, it is a good
idea not to change the animation as the x and y float above and below zero. For
that reason, in this code we have a "dead zone."
We don't change the animation until it gets outside of that zone.

For the multi-frame walking animation, we use an "odometer." We need to move
a certain number of pixels before changing the animation. If this value is too
small our character moves her legs like Fred Flintstone, too large and it looks
like you are ice skating.

.. literalinclude:: pymunk_demo_platformer_08.py
    :caption: Add Player Animation
    :linenos:
    :emphasize-lines: 58-157, 181-182, 197

Add Bullets
-----------

(To be done)

.. literalinclude:: pymunk_demo_platformer_09.py
    :caption: Shooting Bullets
    :linenos:
    :emphasize-lines: 68-72, 296-348

Destroy Bullets and Items
-------------------------

(To be done)

Add Moving Platforms
--------------------

(To be done)

Add Ladders
-----------

(To be done)

Add "Hit" Ability
-----------------

(To be done)

Add "Grab" Ability
------------------

(To be done)

Add "Claw-Shot" Ability
-----------------------

(To be done)
