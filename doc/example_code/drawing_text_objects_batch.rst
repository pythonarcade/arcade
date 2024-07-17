:orphan:

.. _drawing_text_objects_batch:

The Fastest Text Drawing: pyglet Batches
========================================

.. image:: images/drawing_text_objects.png
    :width: 500px
    :align: center
    :alt: Screenshot of drawing with text objects

This example demonstrates the most efficient way to render
:py:class:`arcade.Text` objects: adding them to pyglet's
:py:class:`~pyglet.graphics.Batch`. Otherwise, it is the
same as the :ref:`drawing_text_objects` example.

For a much simpler and slower approach,  see :ref:`drawing_text`.

.. literalinclude:: ../../arcade/examples/drawing_text_objects_batch.py
    :caption: drawing_text_objects.py
    :linenos:
