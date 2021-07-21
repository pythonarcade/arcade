.. include:: <isonum.txt>

Ray-casting Shadows
===================

.. image:: example.png

A common effect for many games is **ray-casting**. Having the user only be able to see
what is directly in their line-of-sight.

This can be done quickly using **shaders**. These are small programs that run on the graphics
card. They can take advantage of the "Graphics Processing Units", the many mini-CPUs that are
on your graphics card and can calculate items in parallel.

Starting Program
----------------

First, let's start with a program that has some crates to block our vision,
some bombs to hide in them, and a player character:

.. image:: start.png
   :width: 50%

The listing for this starting program is available at :ref:`raycasting_start`.

Add-In the ShaderToy
--------------------

Now, let's create a shader. We can program shaders using the :class:`Shadertoy` class.
This class is designed to mimic the `Shadertoy <https://www.shadertoy.com/>`_ website.
The website makes it easy to experiment with shaders, and those shaders can be run
using the Arcade library.

Start by importing the class:

.. literalinclude:: step_01.py
    :caption: Import Shadertoy
    :lines: 3

.. sidebar:: Note

   FBOs can hold more than just image-related data, but for now, just think of them as images.

Next, we'll need some shader-related variables. In addition to a variable to hold the shader, we are also
going to need to keep track of a couple **frame buffer objects** (FBOs). You can store image data in an
FBO and send it to the shader program. An FBO is held on the graphics card, so manipulating an FBO there
is much faster than working with one in loaded into main memory.

Shadertoy has four built-in **channels** that our shader programs can work with. Channels can be mapped to FBOs.
We'll be using two of them in this program. Like most things in computer-ville, we start counting at zero.
The ``channel0`` variable will hold our barriers that can cast shadows. The ``channel1`` variable holds the
ground, bombs, or anything we want to be hidden by shadows.

.. literalinclude:: step_01.py
    :caption: Create shader variables
    :pyobject: MyGame.__init__
    :emphasize-lines: 4-8

These are just empty place-holders. We'll load our shader and create FBOs to hold the image data we send
the shader in a ``load_shader`` method: This code creates the shader and the FBOs:

.. literalinclude:: step_01.py
    :caption: Create the shader, and the FBOs
    :pyobject: MyGame.load_shader

As you'll note, the method loads the source code from another file. So we'll need two files for this
program.

Our first shader will be super-easy. It will take whatever input we get from the channel 0's FBO
called ``iChannel0``. As there are a lot of points in that image, this ``mainImage`` function we will
write will run for each point in the image. This point is stored in ``fragCoord``. We normalize
this coordinate to x, y numbers between 0.0 and 1.0. This normalized two-number x/y vector we store
in ``p``.

.. code-block:: glsl

    vec2 p = fragCoord/iResolution.xy;

We need to grab the color at this point ``curPoint`` from the FBO:

.. code-block:: glsl

    texture(iChannel0, curPoint)

There is a pre-defined output variable called ``fragColor`` that defines our output color
in RGBA format, where each component is a number 0.0 - 1.0.

.. literalinclude:: step_01.glsl
    :caption: GLSL Program for Step 1
    :language: glsl

Now that we have our shader, a couple FBOs, and our initial GLSL program, we can draw with them.
Note that we draw the walls to the FBO, then draw run the shader had have it draw to the screen.

* Select the FBO to draw our walls to
* Select the window

.. literalinclude:: step_01.py
    :caption: Drawing using the shader
    :pyobject: MyGame.on_draw

Running the program, our output should look like:

.. image:: step_01.png
   :width: 50%

* :ref:`raycasting_step_01` |larr| Full listing of where we are right now
* :ref:`raycasting_step_01_diff` |larr| What we changed to get here

Simple Shader Experiments
-------------------------

How do we know our shader is really working? As it is just straight copying everything across,
it is hard to tell.

We can modify our shader to get the current texture color and store it in the variable ``inColor``.
A color has four components, red-green-blue and alpha. If the alpha is above zero, we can output
a red color. If the alpha is zero, we output a blue color.

.. literalinclude:: step_02.glsl
    :caption: GLSL Program for Step 2
    :language: glsl

Giving us a resulting image that looks like:

.. image:: step_02.png
   :width: 50%

Creating a Light
----------------

Our next step is to create a light. We'll be fading between no light (black) and whatever we draw
in Channel 1.

.. image:: step_03.png
   :width: 50%

In this step, we won't worry about the walls yet.

This step will require to pass additional data into our shader. We'll do this using **uniforms**.
We will pass in *where* the light is, and the light *size*.

We first declare and use the variables in our shader program.

.. literalinclude:: step_03.glsl
    :caption: GLSL Program for Step 3
    :language: glsl

We'll update our ``on_draw`` method to:

* Draw the bombs into channel 1.
* Send the player position and the size of the light using the uniform.
* Draw the player character on the window.

.. note::

   If you set a uniform variable using ``program``, that variable has to exist in the
   glsl program, *and be used* or you'll get an error. The glsl compiler will automatically
   drop unused variables, causing a confusing error when the program says a variable
   is missing even if you've declared it.

.. literalinclude:: step_03.py
    :caption: Drawing using the shader
    :pyobject: MyGame.on_draw
    :emphasize-lines: 7-9, 15-20


* :ref:`raycasting_step_03` |larr| Full listing of where we are right now
* :ref:`raycasting_step_03_diff` |larr| What we changed to get here

Make the Walls Shadowed
-----------------------

.. image:: step_04.png
   :width: 50%

.. literalinclude:: step_04.glsl
    :caption: GLSL Program for Step 4
    :language: glsl

Cast the Shadows
----------------


Ref: https://www.shadertoy.com/view/tddXzj