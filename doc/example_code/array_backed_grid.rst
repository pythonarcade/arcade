:orphan:

.. _array_backed_grid:

Array-Backed Grid
=================

.. image:: images/array_backed_grid.png
    :width: 255px
    :height: 255px
    :align: center
    :alt: Screenshot of a program that shows an array backed grid.

If you work with grids much, you'll find this to be slow. You may want to look
at:

* :ref:`array_backed_grid_buffered` - faster and uses buffered shapes
* :ref:`array_backed_grid_sprites_1` - super-fast and uses sprites. Resyncs to number grid in one function call
* :ref:`array_backed_grid_sprites_2` super-fast and uses sprites. Keeps a second 2D grid of sprites to match 2D grid of numbers

.. literalinclude:: ../../arcade/examples/array_backed_grid.py
    :caption: array_backed_grid.py
    :linenos:
