.. _shader_toy_tutorial:

Shader Toy Tutorial
===================

.. contents::

.. figure:: cyber_fuji_2020.png
   :width: 60%

   :ref:`cyber_fuji_2020`

Graphics cards can run programs written in the C-like language OpenGL Shading Language, or GLSL for short.
These programs can be easily parallelized and run across the processors of the
graphics card GPU.

Shaders take a bit of set-up to write. The ShaderToy website has standardized some
of these and made it easier to experiment with writing shaders. The website is at:

https://www.shadertoy.com/

Arcade includes additional code making it easier to run these ShaderToy shaders
in an Arcade program. This tutorial helps you get started.

Step 1: Open a window
---------------------

This is simple program that just opens a basic Arcade window. We'll add a shader in the next step.

.. literalinclude:: shadertoy_demo_1.py
    :caption: Open a window
    :linenos:

Step 2: Load and display a shader
---------------------------------

This program will load a GLSL program and display it.

.. literalinclude:: shadertoy_demo_2.py
    :caption: Run a shader
    :linenos:
    :emphasize-lines: 2, 11-16, 20

Next, let's create a simple first GLSL program. Our program will:

* Normalize the coordinates. Instead of 0 to 1024, we'll go 0.0 to 1.0. This is standard
  practice, and allows us to work independently of resolution.
  Resolution is already stored for us in a standardized variable named ``iResolution``.
* Next, we'll use a white color as default.
* If we are greater that 0.2 for our coordinate (20% of screen size) we'll use black instead.
* Set our output color, standardized with the variable name ``fracColor``.

.. literalinclude:: circle_1.glsl
    :caption: GLSL code for creating a shader.
    :language: glsl
    :linenos:

The output of the program looks like this:

.. image:: circle_1.png
   :width: 60%

Other default variables you can use:

.. code-block:: glsl

    uniform vec3 iResolution;
    uniform float iTime;
    uniform float iTimeDelta;
    uniform float iFrame;
    uniform float iChannelTime[4];
    uniform vec4 iMouse;
    uniform vec4 iDate;
    uniform float iSampleRate;
    uniform vec3 iChannelResolution[4];
    uniform samplerXX iChanneli;

"Uniform" means the data is the same for each pixel the GLSL program runs on.

Step 3: Move origin to center of screen, adjust for aspect
----------------------------------------------------------

.. literalinclude:: circle_2.glsl
    :caption: Center the origin
    :language: glsl
    :linenos:

.. image:: circle_2.png
   :width: 60%

.. note:: To Be Done...

    The rest of the is TBD


Glow
----

.. literalinclude:: glow.glsl
    :caption: GLSL code for creating a shader.
    :language: glsl
    :linenos:

Other examples
--------------

This short ShaderToy demo loads a GLSL file and displays it:

.. literalinclude:: shadertoy_demo.py
    :caption: Shader Toy Demo
    :linenos:

You can click on the caption below the example shaders here to see the source
code for the shader.

Some other sample shaders:

.. figure:: star_nest.png
   :width: 60%

   :ref:`star_nest`

.. figure:: flame.png
   :width: 60%

   :ref:`flame`

.. figure:: fractal_pyramid.png
   :width: 60%

   :ref:`fractal_pyramid`

Writing shaders is beyond the scope of this tutorial. Unfortunately,
I haven't found one comprehensive tutorial on how to write a shader. There
are several smaller tutorials out there that are good.

Here is one learn-by-example tutorial:

https://www.shadertoy.com/view/Md23DV

Here's a video tutorial that steps through how to do an explosion:

https://www.youtube.com/watch?v=xDxAnguEOn8

