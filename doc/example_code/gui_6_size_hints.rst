:orphan:

.. _gui_5_size_hints:

GUI Size Hints
==============

This example shows how to use size hints to control the size of a GUI element.

The `size_hint` property is a tuple of two values.
The first value is the width, and the second value is the height.
The values are in percent of the parent element.
For example, a size hint of (0.5, 0.5) would make the element half
the width and half the height of the parent element.


.. image:: images/gui_5_size_hints.png
    :width: 600px
    :align: center
    :alt: Screen shot

.. literalinclude:: ../../arcade/examples/gui/5_size_hints.py
    :caption: 5_size_hints.py
    :linenos:
