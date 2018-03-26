:orphan:

.. _pymunk_platformer:

Pymunk Platformer
=================

This example uses both the Arcade library and the `PyMunk <http://www.pymunk.org/>`_ library to demo full
2D physics in a platformer.

Video
-----
.. raw:: html

    <iframe width="700" height="400" src="https://www.youtube.com/embed/cr2swAA_Tb8" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

Code
----

This file has some constants used throughout the game.

.. literalinclude:: ../../arcade/examples/pymunk_platformer/constants.py
    :caption: constants.py
    :linenos:

This code creates the level.

.. literalinclude:: ../../arcade/examples/pymunk_platformer/create_level.py
    :caption: create_level.py
    :linenos:

Some utility functions for physics.

.. literalinclude:: ../../arcade/examples/pymunk_platformer/physics_utility.py
    :caption: physics_utility.py
    :linenos:

The main program.

.. literalinclude:: ../../arcade/examples/pymunk_platformer/main_window.py
    :caption: main_window.py
    :linenos:

