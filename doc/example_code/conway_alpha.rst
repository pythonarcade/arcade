:orphan:

.. _conway_alpha:

Conway's Game of Life
=====================

This version of Conway's Game of Life speeds everything up by using controlling
a cell's visibility through its alpha value, and handing the drawing logic off
to the graphics card.

Grid-based games can take a while to render the program uses classic raster-based
graphics. Every cell has to be re-drawn every single frame. If the cells are complex
at all, that adds to the rendering time.

In this program, we create all cells in the grid to begin with.
(This does causes the program to pause a while at start-up.)

After the sprites are created, we turn the cells on and off
by their alpha value. We can update the entire grid by simply sending a list of
alpha values to the graphics card. This significantly improves drawing time.

.. raw:: html

   <iframe width="560" height="315" src="https://www.youtube.com/embed/6TZ_lwbioRA" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

.. literalinclude:: ../../arcade/examples/conway_alpha.py
    :caption: conway_alpha.py
    :linenos:
