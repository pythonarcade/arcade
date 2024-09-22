.. _gui_own_widgets:

Own Widgets
-----------

Creating own widgets is a powerful feature of the GUI module.
It allows you to create custom widgets that can be used in your application.

In most cases this is even the easiest way to implement your desired interface.

The following sections will guide you through the process of creating own widgets.



Where to start
~~~~~~~~~~~~~~

To create own widgets, you need to create a new class that inherits from :class:`arcade.gui.UIWidget`.

While inheriting from :class:`arcade.gui.UIWidget`, provides the highest flexibility,
you can also make use of other base classes, which provide a more specialized interface.

Further baseclasses are:

- :class:`arcade.gui.UIInteractiveWidget`
    `UIInteractiveWidget` is a baseclass for widgets that can be interacted with.
    It provides a way to handle mouse events and properties like `hovered` or `pressed`.
    In addition it already implements the `on_click` method,
    which can be used to react to a click event.

- :class:`arcade.gui.UIAnchorLayout`
    `UIAnchorLayout` is basically a frame, which can be used to position widgets
    to a place within the widget. This makes it a great baseclass for a widget containing
    multiple other widgets. (Examples: `MessageBox`, `Card`, etc.)

If your widget should act more as a general layout, position various widgets and handle their size,
you should inherit from :class:`arcade.gui.UILayout` instead.

In the following example, we will create two progress bar widgets
to show the differences between two of the base classes.


Example `ProgressBar`
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/gui/own_progressbar.py


