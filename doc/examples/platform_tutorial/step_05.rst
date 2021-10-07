

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

We are sending our ``SpriteList`` for the things the player should collide with to the ``walls``
parameter of the the physics engine. As we'll see in later chapters, the platformer physics engine
has a ``platforms`` and ``walls`` parameter. The difference between these is very important. Static
non-moving spritelists should always be sent to the ``walls`` parameter, and moving sprites should
be sent to the ``platforms`` parameter. Ensuring you do this will have extreme benefits to performance.

Adding static sprites via the ``platforms`` parameter is roughly an O(n) operation, meaning performance will
linearly get worse as you add more sprites. If you add your static sprites via the ``walls`` parameter, then
it is nearly O(1) and there is essentially no difference between for example 100 and 50,000 non-moving sprites.

We also see here some new syntax relating to our ``Scene`` object. You can access the scene like you would a
Python dictionary in order to get your SpriteLists from it. There are multiple ways to access the SpriteLists
within a Scene but this is the easiest and most straight forward. You could alternatively use ``scene.get_sprite_list("My Layer")``.

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