.. _shader_toy_tutorial_particles:

Shader Toy Tutorial - Particles
===============================

.. contents::

This tutorial assumes you are familiar with the material in
:ref:`shader_toy_tutorial_glow`. If you haven't gone through that
tutorial, you might want to do that first.

Load the shader
---------------

.. literalinclude:: shadertoy_demo_1.py
   :linenos:


Initial shader with particles
-----------------------------

.. image:: step_2.png
   :width: 50%

.. literalinclude:: explosion_1.glsl
   :linenos:
   :language: glsl

Add particle movement
---------------------

.. image:: step_3.gif

.. literalinclude:: explosion_2.glsl
   :linenos:
   :language: glsl
   :emphasize-lines: 13-14, 50-51

Fade-out
--------

.. literalinclude:: explosion_3.glsl
   :linenos:
   :language: glsl
   :emphasize-lines: 59


Glowing Particles
-----------------

.. image:: glow.png

.. literalinclude:: explosion_4.glsl
   :linenos:
   :language: glsl
   :emphasize-lines: 15-16, 57-58

Twinkling Particles
-------------------

.. literalinclude:: explosion_5.glsl
   :linenos:
   :language: glsl
   :emphasize-lines: 60
