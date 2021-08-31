.. _shader_toy_tutorial:

Shader Toy Tutorial
===================

.. figure:: cyber_fuji_2020.png
   :width: 60%

   :ref:`cyber_fuji_2020`

Graphics cards can run programs written in the C-like language GLSL.
These programs can be easily parallelized and run across the processors of the
graphics card GPU.

Shaders take a bit of set-up to write. The ShaderToy website has standardized some
of these and made it easier to experiment with writing shaders. The website is at:

https://www.shadertoy.com/

Arcade includes additional code making it easier to run these shaders in an Arcade
program. This short ShaderToy demo loads a GLSL file and displays it:

.. literalinclude:: shadertoy_demo.py
    :caption: Shader Toy Demo
    :linenos:

Some sample shaders:

.. figure:: star_nest.png
   :width: 60%

   :ref:`star_nest`

.. figure:: flame.png
   :width: 60%

   :ref:`flame`

.. figure:: fractal_pyramid.png
   :width: 60%

   :ref:`fractal_pyramid`
