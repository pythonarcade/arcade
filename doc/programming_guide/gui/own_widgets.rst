.. _gui_own_widgets:

Own Widgets
-----------

Creating your own widgets is a powerful feature of the GUI module.
It allows you to create custom widgets that can be used in your application.

In most cases this is even the easiest way to implement your desired interface.

The following sections will guide you through the process of creating own widgets.



Where to start
~~~~~~~~~~~~~~

To create your own widgets, you need to create a new class that inherits from :class:`arcade.gui.UIWidget`.

While inheriting from :class:`arcade.gui.UIWidget`, provides the highest flexibility.
The main methods you need to implement are:
- :meth:`arcade.gui.UIWidget.do_render` - This method is called to render the widget.
- :meth:`arcade.gui.UIWidget.on_event` - This method is called to handle events like mouse or keyboard input.
- :meth:`arcade.gui.UIWidget.on_update` - This method is called to update the widget (same frequency like window).

You can also make use of other base classes, which provide a more specialized interface.
Further baseclasses are:

- :class:`arcade.gui.UIInteractiveWidget`
    `UIInteractiveWidget` is a baseclass for widgets that can be interacted with.
    It handles mouse events and provides properties like `hovered` or `pressed` and an :meth:`on_click` method.

- :class:`arcade.gui.UIAnchorLayout`
    `UIAnchorLayout` is basically a frame, which can be used to place widgets
    to a position within itself. This makes it a great baseclass for a widget containing
    multiple other widgets. (Examples: `MessageBox`, `Card`, etc.)

If your widget should act more as a general layout, position various widgets and handle their size,
you should inherit from :class:`arcade.gui.UILayout` instead.

In the following example, we will create two progress bar widgets
to show the differences between two of the base classes.


Example `ProgressBar`
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/gui/own_widget.py


