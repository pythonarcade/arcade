.. _platformer_part_three:

Step 3 - Many Sprites with SpriteList
-------------------------------------

So far our game is coming along nicely, we have a character on the screen! Wouldn't it be nice
if our character had a world to live in? In order to do that we'll need to draw a lot more sprites.
In this chapter we will explore SpriteList, a class Arcade provides to draw tons of Sprites at once.

At the end, we'll have something like this:

.. image:: images/title_03.png
    :width: 70%

SpriteList
~~~~~~~~~~

Imagine how you (as a human) would draw this picture. Maybe you would draw the character first. Then
the first box, then the second box, etc... Now a long strip of green and brown stuff we will call grass.
So likely your first thought to programming would be to make a loop over a list of sprites and call ``draw()``
on every sprite, one at a time. Computers are fast right? Yes, but this approach is extremely inefficient.
See the note below on how Arcade uses GPUs. What if we could draw EVERY object at the same time! Computers
can surpass the frail limitiation of you mortal humans!

But to do that, the computer does need your help (and the computer humbly apologizes for the insult!).
:class:`arcade.SpriteList` exists to draw a collection of Sprites all at once. Let's say for example that
you have 100,000 box Sprites that you want to draw. You can add all of your boxes to a :class:`arcade.SpriteList`
and then draw the SpriteList. Doing this, you are able to draw all 100,000 sprites for approximately the exact
same cost as drawing one sprite. Which is pretty amazing.

.. note::
    Arcade is a heavily GPU based library. GPUs are really good at doing things in batches.
    This means we can send all the information about our sprites to the GPU, and then tell it to draw them all
    at once. However if we just draw one sprite at a time, then we have to go on a round trip from our CPU to
    our GPU every time.

Even if you are only drawing one Sprite, you should still create a SpriteList for it. Outside of small debugging
it is never better to draw an individual Sprite than it is to add it to a SpriteList. In fact, calling ``draw()``
on a Sprite just creates a SpriteList internally to draw that Sprite with.

Quiz - where in our code should we place the data object of our :class:`arcade.SpriteList`?

.. toggle::

       If you guessed the ``__init__`` function you are correct!

So that is where we are going to put the following code. Just add it to the bottom of the list of other data objects.

.. code-block::

    self.player_list = arcade.SpriteList()
    self.player_list.append(self.player_sprite)

Then in our ``on_draw`` function, we can draw the SpriteList for the character instead of drawing the Sprite directly.
So we will replace this line of code:

.. code-block::

    arcade.draw_sprite(self.player_sprite)

with this line of code:

.. code-block::

    self.player_list.draw()

Now run it and you get your character on the screen. All by herself... alone in an empty world... sad face.

Time to make the world!
~~~~~~~~~~~~~~~~~~~~~~~

Now let's try and build a world for our character. To do this, we'll create a new SpriteList for the objects we'll draw,
we can do this again in our ``__init__`` function.

.. code-block::

    self.wall_list = arcade.SpriteList(use_spatial_hash=True)

Wait, why did we make a new list of Sprites? I thought the idea was to make one master list of everything we needed to draw?
What is a spatial_hash and why is it True?

Great questions!

1. Why not just use the same SpriteList we used for our player, and why is it named walls?

    Eventually we will want to do collision detection between our character and these objects.
    In addition to drawing, SpriteLists also serve as a utility for collision detection. You can
    for example check for collisions between two SpriteLists, or pass SpriteLists into several physics
    engines. We will explore these topics in later chapters. And you will notice that we are going to
    pass in pictures of grass and boxes - which we will treat as barriers. So they will be added to
    the 'walls'

2. What is ``use_spatial_hash``?

    This is also for collision detection. Spatial Hashing is a special algorithm which will make it
    much more performant, at the cost of being more expensive to move sprites. You will often see this
    option enabled on SpriteLists which are not expected to move much, such as walls or a floor.

With our newly created SpriteList, let's go ahead and add some objects to it. We can add these lines to our
``__init__`` function.

.. code-block::

    for x in range(0, 1250, 64):
        wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=TILE_SCALING)
        wall.center_x = x
        wall.center_y = 32
        self.wall_list.append(wall)

    coordinate_list = [[512, 96], [256, 96], [768, 96]]
    for coordinate in coordinate_list:
        wall = arcade.Sprite(
            ":resources:images/tiles/boxCrate_double.png", scale=TILE_SCALING)
        wall.position = coordinate
        self.wall_list.append(wall)

In these lines, we're adding some grass and some crates to our SpriteList.

For the ground we're using Python's ``range`` function to iterate on a list of X positions, which will give us
a horizontal line of Sprites. For the boxes, we're inserting them at specified coordinates from a list.

We're also doing a few new things in the :class:`arcade.Sprite` creation. First off we are passing the image file
directly instead of creating a texture first. This is ultimately doing the same thing, we're just not managing the
texture ourselves, and letting Arcade handle it. We are also adding a scale to these sprites. For fun you can remove
the scale, and see how the images will be much larger.

Finally all we need to do in order to draw our new world, is draw the SpriteList for walls in ``on_draw``:

.. code-block::

    self.wall_list.draw()

Run the code and... wait the image is instantly disappearing! What did we do wrong? Try and debug it!

.. toggle::

       You might have noticed that we use TILE_SCALING but we never defined it! So the image starts creating, but crashes
       before we get to even see what is wrong! This is a hard bug to find as there is no error message.

       Solution: add this up by the '# constants' section
       TILE_SCALING = 0.5


Challenge
~~~~~~~~~
* Try changing the new variable TILE_SCALING, what does it do?
* Make some floating boxes. Do it either randomly or fixed.
* Read the documentation for the :class:`arcade.SpriteList` class
* See if you can change the colors of all the boxes and ground using the SpriteList
* Try and make a SpriteList invisible
* EXTREME Challeng Our __init__ class is getting pretty bloated. The loops we created to make the walls would be better suited
  to have their own function that we call. See if you can make a function 'def build_walls(self):' that has that same
  code. Then call that function with build_walls() after you define the self.wall_list.

Your code should produce the same image as shown on the top of this page. Before proceeding, make sure you comment
out custom code so we are on the same page. Also, if you are still having problems, compare with this code:

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_more_sprites.py
    :caption: 03_more_sprites - Many Sprites with a SpriteList
    :linenos:
    :emphasize-lines: 13-14, 37-39, 41-47, 49-66, 80-82

* Documentation for the :class:`arcade.SpriteList` class
