

.. _platformer_part_five:

Step 5 - Add Gravity
--------------------

The previous example great for top-down, but what if it is a side view with
jumping like our platformer? We need to add gravity. First, let's define a 
constant to represent the acceleration for gravity, and one for a jump speed.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/05_add_gravity.py
    :caption: 05_add_gravity.py - Add Gravity
    :lines: 17-18

At the end of the ``setup`` method, change the physics engine to
``PhysicsEnginePlatformer`` and include gravity as a parameter.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/05_add_gravity.py
    :caption: 05_add_gravity.py - Add Gravity
    :lines: 75-78

Then, modify the key down and key up event handlers. We'll remove the up/down
statements we had before, and make 'UP' jump when pressed.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/05_add_gravity.py
    :caption: 05_add_gravity.py - Add Gravity
    :lines: 89-106
    :linenos:
    :emphasize-lines: 4-6

.. note::

    You can change how the user jumps by changing the gravity and jump constants.
    Lower values for both will make for a more "floaty" character. Higher values make
    for a faster-paced game.

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/05_add_gravity.py
    :caption: 05_add_gravity.py - Add Gravity
    :linenos:
    :emphasize-lines: 17-18, 75-78, 92-94