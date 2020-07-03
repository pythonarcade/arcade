GPU Particle Burst
==================

.. image:: explosions.gif
    :width: 80%

In this example, we show how to create explosions using particles. The particles
are tracked by the GPU, significantly improving the performance.

Step 1: Open a Blank Window
---------------------------

First, let's start with a blank window.

.. literalinclude:: gpu_particle_burst_01.py
    :caption: gpu_particle_burst_01.py
    :linenos:

Step 2: Create One Particle For Each Click
------------------------------------------

.. image:: gpu_particle_burst_02.png
    :width: 50%

For this next section, we are going to draw a dot each time the user clicks
her mouse on the screen.

For each click, we are going to create an instance of a "burst" that will eventually
be turned into a full explosion. Each burst instance will be added to a list.

Imports
~~~~~~~

First, we'll import some more items for our program:

.. literalinclude:: gpu_particle_burst_02.py
    :lines: 4-7

Burst Dataclass
~~~~~~~~~~~~~~~

Next, we'll create a dataclass to track our data for each burst. For each burst
we need to track a Vertex Array Object (VAO) which stores information about
our burst. Inside of that, we'll have a Vertex Buffer Object (VBO) which will
be a high-speed memory buffer where we'll store locations, colors, velocity, etc.

.. literalinclude:: gpu_particle_burst_02.py
    :pyobject: Burst

Init method
~~~~~~~~~~~

Next, we'll create an empty list attribute called ``burst_list``. We'll also
create our OpenGL shader program. The program will be a collection of two
shader programs. These will be stored in separate files, saved in the same
directory.

.. note::

    In addition to loading the program via the `load_program()` method of
    `ArcadeContext` shown, it is also possible to keep the GLSL programs in triple-
    quoted string by using `program()` of `Context`.

.. literalinclude:: gpu_particle_burst_02.py
    :pyobject: MyWindow.__init__
    :caption: MyWindow.__init__

.. _open_gl_shaders:

OpenGL Shaders
~~~~~~~~~~~~~~

The OpenGL Shading Language (GLSL) is C-style language that runs on your
graphics card (GPU) rather than your CPU. Unfortunately a full explanation
of the language is beyond the scope of this tutorial. I hope, however,
the tutorial can get you started understanding how it works.

We'll have two shaders. A vertex shader, and a fragment shader.
A vertex shader runs for each vertex point of the geometry we are rendering,
and a fragment shader runs for each pixel.
For example, vertex shader might run four times for each point on a
rectangle, and the fragment shader would run for each pixel on the screen.

The vertex shader takes in the position of our vertex.
We'll set `in_pos` in our Python program, and pass that data to this shader.

The vertex shader outputs the color of our vertex.
Colors are in Red-Green-Blue-Alpha (RGBA) format, with floating-point numbers
ranging from 0 to 1.
In our program below case, we set the color to (1, 1, 1) which is white,
and the fourth 1 for completely opaque.

.. literalinclude:: vertex_shader_v1.glsl
   :language: glsl
   :linenos:
   :caption: vertex_shader_v1.glsl

There's not much to the fragment shader, it just takes in ``color`` from the vertex
shader and passes it back out as the pixel color. We'll use the same fragment
shader for every version in this tutorial.


.. literalinclude:: fragment_shader.glsl
   :language: glsl
   :linenos:
   :caption: fragment_shader.glsl

Mouse Pressed
~~~~~~~~~~~~~

Each time we press the mouse button, we are going to create a burst at that
location.

The data for that burst will be stored in an instance of the ``Burst`` class.

The ``Burst`` class needs our data buffer. The data buffer contains
information about each particle. In this case, we just have one particle and
only need to store the x, y of that particle in the buffer. However, eventually
we'll have hundreds of particles, each with a position, velocity, color, and
fade rate. To accommodate creating that data, we have made a generator
function ``_gen_initial_data``. It is totally overkill at this point, but we'll
add on to it in this tutorial.

The ``buffer_description`` says that each vertex has two floating data points (``2f``)
and those data points will come into the shader with the reference name ``in_pos``
which we defined above in our :ref:`open_gl_shaders`

.. literalinclude:: gpu_particle_burst_02.py
    :pyobject: MyWindow.on_mouse_press
    :caption: MyWindow.on_mouse_press

Drawing
~~~~~~~

Finally, draw it.

.. literalinclude:: gpu_particle_burst_02.py
    :pyobject: MyWindow.on_draw
    :caption: MyWindow.on_draw


* :ref:`fragment_shader`
* :ref:`vertex_shader_v1`
* :ref:`gpu_particle_burst_02`
* :ref:`gpu_particle_burst_02_diff`

Step 3: Multiple Moving Particles
---------------------------------

.. image:: gpu_particle_burst_03.png
    :width: 50%

* :ref:`gpu_particle_burst_03`
* :ref:`gpu_particle_burst_03_diff`

Step 4: Random Angle and Speed
------------------------------

.. image:: gpu_particle_burst_04.png
    :width: 50%

* :ref:`gpu_particle_burst_04`
* :ref:`gpu_particle_burst_04_diff`

Step 5: Gaussian Distribution
-----------------------------

Step 6: Add Color
-----------------

Step 7: Fade Out
----------------

Final Program
-------------

* :ref:`gpu_particle_burst_final`

