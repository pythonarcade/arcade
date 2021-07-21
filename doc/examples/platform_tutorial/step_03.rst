.. _platformer_part_three:

Step 3 - Scene Object
---------------------

Next we will add a Scene to our game. A Scene is a tool to manage a number of different
SpriteLists by assigning each one a name, and maintaining a draw order.

SpriteLists can be drawn directly like we saw in step 2 of this tutorial, but a Scene can
be helpful to handle a lot of different lists at once and being able to draw them all with
one call to the scene.

To start with we will remove our sprite lists from the ``__init__`` function, and replace them
with a scene object.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_scene_object.py
    :caption: 03_scene_object.py - Scene Object Definition
    :lines: 21-32
    :emphasize-lines: 6-7

Next we will initialize the scene object in the ``setup`` function and then add the SpriteLists to it
instead of creating new SpriteList objects directly.

Then instead of appending the Sprites to the SpriteLists directly, we can add them to the Scene and
specify by name what SpriteList we want them added to.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_scene_object.py
    :caption: 03_scene_object.py - Add SpriteLists to the Scene
    :lines: 34-69
    :emphasize-lines: 4-9, 16, 24, 36

Lastly in our ``on_draw`` function we can draw the scene.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_scene_object.py
    :caption: 03_scene_object.py - Draw the Scene
    :lines: 71-78
    :emphasize-lines: 7-8

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/03_scene_object.py
    :caption: 03_scene_object - Scene Object
    :linenos:
    :emphasize-lines: 26-27, 37-42, 49, 57, 69, 77-78
    