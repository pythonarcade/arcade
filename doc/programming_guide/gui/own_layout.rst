.. _gui_own_layout:

Own Layout
----------

Creating your own layouts is the master class of creating own widgets.
It allows you to create custom layouts that can be used in your application to position widgets.

General use cases for own layouts are:

- Create a layout that positions widgets in a specific way, like in a circle.
- Animate widgets in a specific way, like a carousel.

Where to start
~~~~~~~~~~~~~~

To create your own layout, you need to create a new class that inherits from :class:`arcade.gui.UILayout`.

The main method you need to implement is:

- :meth:`arcade.gui.UILayout.do_layout` - This method is called to layout the child widgets.

Widgets added to the layout are accessible via the :attr:`arcade.gui.UILayout._children` attribute,
which is a list of all added widgets with the parameter provided when added.

Children should be placed within the bounds of the layout.
And should respect size_hint, size_hint_min and size_hint_max of the children.


It also provides a great user experience when you provide custom docs for the :meth:`arcade.gui.UIWidget.add` method.
So the user knows how to add widgets to your layout and which parameter are supported.

In the following example, we will create a layout that positions widgets in a circle and slowly rotating them.

Example `CircleLayout`
~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/gui/own_layout.py


