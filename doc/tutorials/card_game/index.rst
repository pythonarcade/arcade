.. include:: <isonum.txt>

.. _solitaire_tutorial:

Solitaire Tutorial
==================

.. image:: animated.gif

This solitaire tutorial takes you though the basics of creating a card game, and
doing extensive drag/drop work.

.. warning::

    This tutorial requires Arcade version 2.4a9 or greater.
    As this is an Alpha version,
    you'll need to specifically install it, as 2.3 will be default.

Open a Window
-------------

.. image:: solitaire_01.png
    :width: 25%
    :class: right-image

To begin with, let's start with a program that will use Arcade to open a blank
window. The listing below also has stubs for methods we'll fill in later.

Get started with this code and make sure you can run it.
It should pop open a green window.

.. literalinclude:: solitaire_01.py
    :caption: Starting Program
    :linenos:

Create Card Sprites
-------------------

Our next step is the create a bunch of sprites, one for each card.

Constants
~~~~~~~~~

First, we'll create some constants used in positioning the cards, and keeping
track of what card is which.

We could just hard-code numbers, but I like to calculate things out. The "mat"
will eventually be a square slightly larger than each card that tracks where
we can put cards. (A mat where we can put a pile of cards on.)

.. literalinclude:: solitaire_02.py
    :caption: Create constants for positioning
    :linenos:
    :lines: 11-36

Card Class
~~~~~~~~~~

Next up, we'll create a card class. The card class is a subclass of
``arcade.Sprite``. It will have attributes for the suit and value of the
card, and auto-load the image for the card based on that.

We'll use the entire image as the hit box, so we don't need to go through the
time consuming hit box calculation. Therefore we turn that off. Otherwise loading
the sprites would take a long time.

.. literalinclude:: solitaire_02.py
    :caption: Create card sprites
    :linenos:
    :pyobject: Card

Creating Cards
~~~~~~~~~~~~~~

We'll start by creating an attribute for the ``SpriteList`` that will hold all
the cards in the game.

.. literalinclude:: solitaire_02.py
    :caption: Create card sprites
    :linenos:
    :pyobject: MyGame.__init__
    :emphasize-lines: 4-5

In ``setup`` we'll create the list and the cards. We don't do this in ``__init__``
because by separating the creation into its own method, we can easily restart the
game by calling ``setup``.

.. literalinclude:: solitaire_02.py
    :caption: Create card sprites
    :linenos:
    :pyobject: MyGame.setup
    :emphasize-lines: 4-12

Drawing Cards
~~~~~~~~~~~~~

Finally, draw the cards:

.. literalinclude:: solitaire_02.py
    :caption: Create card sprites
    :linenos:
    :pyobject: MyGame.on_draw
    :emphasize-lines: 6-7

You should end up with all the cards stacked in the lower-left corner:

.. image:: solitaire_02.png
    :width: 80%

* :ref:`solitaire_02` |larr| Full listing of where we are right now
* :ref:`solitaire_02_diff` |larr| What we changed to get here

Implement Drag and Drop
-----------------------

Next up, let's add the ability to pick up, drag, and drop the cards.

Track the Cards
~~~~~~~~~~~~~~~

First, let's add attributes to track what cards we are moving. Because we can
move multiple cards, we'll keep this as a list. If the user drops the card in
an illegal spot, we'll need to reset the card to its original position. So we'll
also track that.

Create the attributes:

.. literalinclude:: solitaire_03.py
    :caption: Add attributes to __init__
    :linenos:
    :pyobject: MyGame.__init__
    :emphasize-lines: 9-14

Set the initial values (an empty list):

.. literalinclude:: solitaire_03.py
    :caption: Create empty list attributes
    :linenos:
    :pyobject: MyGame.setup
    :emphasize-lines: 4-9

Pull Card to Top of Draw Order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When we click on the card, we'll want it to be the last card drawn, so it
appears on top of all the other cards. Otherwise we might drag a card underneath
another card, which would look odd.

.. literalinclude:: solitaire_03.py
    :caption: Pull card to top
    :linenos:
    :pyobject: MyGame.pull_to_top

Mouse Button Pressed
~~~~~~~~~~~~~~~~~~~~

When the user presses the mouse button, we will:

* See if they clicked on a card
* If so, put that card in our held cards list
* Save the original position of the card
* Pull it to the top of the draw order

.. literalinclude:: solitaire_03.py
    :caption: Pull card to top
    :linenos:
    :pyobject: MyGame.on_mouse_press

Mouse Moved
~~~~~~~~~~~

If the user moves the mouse, we'll move any held cards with it.

.. literalinclude:: solitaire_03.py
    :caption: Pull card to top
    :linenos:
    :pyobject: MyGame.on_mouse_motion

Mouse Released
~~~~~~~~~~~~~~

When the user releases the mouse button, we'll clear the held card list.

.. literalinclude:: solitaire_03.py
    :caption: Pull card to top
    :linenos:
    :pyobject: MyGame.on_mouse_release

Test the Program
~~~~~~~~~~~~~~~~

You should now be able to pick up and move cards around the screen.
Try it out!

.. image:: solitaire_03.png

* :ref:`solitaire_03` |larr| Full listing of where we are right now
* :ref:`solitaire_03_diff` |larr| What we changed to get here

Draw Pile Mats
--------------

Next, we'll create sprites that will act as guides to where the piles of cards
go in our game. We'll create these as sprites, so we can use collision detection
to figure out of we are dropping a card on them or not.

Create Constants
~~~~~~~~~~~~~~~~

First, we'll create constants for the middle row of seven piles, and for the
top row of four piles. We'll also create a constant for how far apart each pile
should be.

Again, we could hard-code numbers, but I like calculating them so I can change
the scale easily.

.. literalinclude:: solitaire_04.py
    :caption: Add constants
    :linenos:
    :lines: 34-41

Create Mat Sprites
~~~~~~~~~~~~~~~~~~

Create an attribute for the mat sprite list:

.. literalinclude:: solitaire_04.py
    :caption: Create the mat sprites
    :linenos:
    :pyobject: MyGame.__init__
    :emphasize-lines: 16-17

Then create the mat sprites in the ``setup`` method

.. literalinclude:: solitaire_04.py
    :caption: Create the mat sprites
    :linenos:
    :pyobject: MyGame.setup
    :emphasize-lines: 21-45

Draw Mat Sprites
~~~~~~~~~~~~~~~~

Finally, the mats aren't going to display if we don't draw them:

.. literalinclude:: solitaire_04.py
    :caption: Draw the mat sprites
    :linenos:
    :pyobject: MyGame.on_draw
    :emphasize-lines: 6-7

Test the Program
~~~~~~~~~~~~~~~~

Run the program, and see if the mats appear:

.. image:: solitaire_04.png
    :width: 80%

* :ref:`solitaire_04` |larr| Full listing of where we are right now
* :ref:`solitaire_04_diff` |larr| What we changed to get here

Snap Cards to Piles
-------------------

Right now, you can drag the cards anywhere. They don't have to go onto a
pile. Let's add code that "snaps" the card onto a pile. If we don't drop
on a pile, let's reset back to the original location.

.. literalinclude:: solitaire_05.py
    :caption: Snap to nearest pile
    :linenos:
    :pyobject: MyGame.on_mouse_release
    :emphasize-lines: 9-29

* :ref:`solitaire_05` |larr| Full listing of where we are right now
* :ref:`solitaire_05_diff` |larr| What we changed to get here

Shuffle the Cards
-----------------

Having all the cards in order is boring. Let's shuffle them in the ``setup``
method:

.. literalinclude:: solitaire_06.py
    :caption: Shuffle Cards
    :linenos:
    :lines: 107-110

Don't forget to ``import random`` at the top.

Run your program and make sure you can move cards around.

.. image:: solitaire_06.png
    :width: 80%

* :ref:`solitaire_06` |larr| Full listing of where we are right now
* :ref:`solitaire_06_diff` |larr| What we changed to get here
