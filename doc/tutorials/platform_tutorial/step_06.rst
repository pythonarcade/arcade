.. _platformer_part_six:

Step 6 - Add a Camera
----------------------

We can have our window be a small viewport into a much larger world by adding
a camera to it. 

First we need to create a new variable in our ``__init__`` method:

.. literalinclude:: ../../../arcade/examples/platform_tutorial/06_camera.py
    :caption: 06_camera.py - Create camera variable
    :lines: 40-41

Next we can initialize the camera in the ``setup`` function:

.. literalinclude:: ../../../arcade/examples/platform_tutorial/06_camera.py
    :caption: 06_camera.py - Setup Camera
    :lines: 48-49

Then to use our camera when drawing, we can activate it in our ``on_draw`` function:

.. literalinclude:: ../../../arcade/examples/platform_tutorial/06_camera.py
    :caption: 06_camera.py - Use camera when drawing
    :lines: 96-97

Now at this point everything should be working the same, but the camera can do a lot
more than this. We can use the ``move`` function of the camera to scroll it to a different
position. We can use this functionality to keep the camera centered on the player:

We can create a function to calculate the coordinates for the center of our player
relative to the screen, then move the camera to those. Then we can call that function in
``on_update`` to actually move it. The new position will be taken into account during
the ``use`` function in ``on_draw``

.. literalinclude:: ../../../arcade/examples/platform_tutorial/06_camera.py
    :caption: 06_camera.py - Center camera on player
    :lines: 121-143
    :emphasize-lines: 1-14, 22-23

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/06_camera.py
    :caption: Add a Camera
    :linenos:
    :emphasize-lines: 40-41, 48-49, 96-97, 121-134, 142-143
