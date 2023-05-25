.. _compute_shader_tutorial:

Compute Shader Tutorial
=======================

.. raw:: html

   <div style="width: 100%; height: 0px; position: relative; padding-bottom: 56.250%;"><iframe src="https://streamable.com/e/ab8d87" frameborder="0" width="100%" height="100%" allowfullscreen style="width: 100%; height: 100%; position: absolute;"></iframe></div>

Using the compute shader, you can use the GPU to perform calculations thousands
of times faster than just by using the CPU.

In this example, we will simulate a star field using an 'N-Body simulation'. Each
star is affected by the gravity of every other star. For 1,000 stars, this means we have
1,000 x 1,000 = 1,000,000 million calculations to perform for each frame.
The video has 65,000 stars, requiring 4.2 billion gravity force calculations per frame.
On high-end hardware it can still run at 60 fps!

How does this work?
There are three major parts to this program:

* The Python code, which glues everything together.
* The visualization shaders, which let us see the data.
* The compute shader, which moves everything.

Visualization Shaders
---------------------

There are multiple visualization shaders, which operate in this order:

.. image:: shaders.svg

The Python program creates a **shader storage buffer object** (SSBO) of
floating point numbers. This buffer
has the x, y, z and radius of each star stored in ``in_vertex``. It also
stores the color in ``in_color``.

The **vertex shader** doesn't do much more than separate out the radius
variable from the group of floats used to store position.

.. literalinclude:: shaders/vertex_shader.glsl
    :language: glsl
    :caption: shaders/vertex_shader.glsl
    :linenos:

The **geometry shader** converts the single point (which we can't render) to
a square, which we can render. It changes the one point, to four points of a quad.

.. literalinclude:: shaders/geometry_shader.glsl
    :language: glsl
    :caption: shaders/geometry_shader.glsl
    :linenos:

The **fragment shader** runs for each pixel. It produces the soft glow effect of the
star, and rounds off the quad into a circle.

.. literalinclude:: shaders/fragment_shader.glsl
    :language: glsl
    :caption: shaders/fragment_shader.glsl
    :linenos:


Compute Shaders
---------------

This program runs two buffers. We have an **input buffer**, with all our current data. We perform
calculations on that data and write to the **output buffer**. We then swap those buffers for the
next frame, where we use the output of the previous frame as the input to the next frame.

.. literalinclude:: shaders/compute_shader.glsl
    :language: glsl
    :caption: shaders/compute_shader.glsl
    :linenos:

Python Program
--------------

Read through the code here, I've tried hard to explain all the parts in the comments.

.. literalinclude:: main.py
    :caption: main.py
    :linenos:

An expanded version of this, with support for 3D, is available at: https://github.com/pvcraven/n-body