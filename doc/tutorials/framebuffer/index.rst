Working With FrameBuffer Objects
================================

Start with a simple window:

.. literalinclude:: starting_template_simple.py
    :caption: Starting template
    :linenos:

Then create a simple program with a frame buffer:

.. literalinclude:: step_01.py
    :caption: Pass-through frame buffer
    :linenos:

Now, color everything that doesn't have an alpha of zero as green:

.. literalinclude:: step_02.py
    :caption: Green where alpha is not zero in the FBO
    :linenos:

Something about passing uniform data to the shader:

.. literalinclude:: step_03.py
    :caption: Passing uniform data to the shader
    :linenos:
