.. _gui_concepts:

GUI Concepts
------------

GUI elements are represented as instances of :py:class:`~arcade.gui.UIWidget`.
The GUI is structured like a tree; every widget can have other widgets as
children.

The root of the tree is the :py:class:`~arcade.gui.UIManager`. The
:py:class:`UIManager` connects the user interactions with the GUI. Read more about
:ref:`UIEvent`.

Classes of Arcade's GUI code are prefixed with ``UI-`` to make them easy to
identify and search for in autocompletion.

Classes
=======

Following classes provide the basic structure of the GUI.

UIManager
`````````

:py:class:`~arcade.gui.UIManager` is the starting point for the GUI.

To use the GUI, you need to create a :py:class:`~arcade.gui.UIManager` instance and
call its :py:meth:`~arcade.gui.UIManager.add` method to add widgets to the GUI.
Each :py:class:`~arcade.View` should have its own :py:class:`~arcade.gui.UIManager`.
(If you don't use views, you can use a single :py:class:`~arcade.gui.UIManager` for the window.)

The :py:class:`~arcade.gui.UIManager` does not react to any user input initially.
You have to call :py:meth:`~arcade.gui.UIManager.enable()` within :py:meth:`~arcade.View.on_show_view`.
And disable it with :py:meth:`~arcade.gui.UIManager.disable()` within :py:meth:`~arcade.View.on_hide_view`.

To draw the GUI, call :py:meth:`~arcade.gui.UIManager.draw` within the :py:meth:`~arcade.View.on_draw` method.

The :py:class`~arcade.gui.UIView` class is a subclass of :py:class:`~arcade.View` and provides
a convenient way to use the GUI. It instanciates a :py:class:`~arcade.gui.UIManager` which can be accessed
via the :py:attr:`~arcade.gui.UIView.ui` attribute.
It automatically enables and disables the
:py:class:`~arcade.gui.UIManager` when the view is shown or hidden.


UIWidget
````````

The :py:class:`~arcade.gui.UIWidget` class is the core of Arcade's GUI system.
Widgets specify the behavior and graphical representation of any UI element,
such as buttons or labels.

User interaction with widgets is processed within :py:meth:`~arcade.gui.UIWidget.on_event`.


A :class:`UIWidget` has following properties.

``rect``
    A tuple with four slots. The first two are x and y coordinates (bottom
    left of the widget), and the last two are width and height.

``children``
    Child widgets rendered within this widget. A :class:`UIWidget` will not
    move or resize its children; use a :py:class:`~arcade.gui.UILayout`
    instead.

``visible``
    A boolean indicating if the widget is visible or not. If a widget is not
    visible, itself and any child widget will not be rendered.
    Especially useful for hiding parts of the GUI like dialogs or popups.

``size_hint``
    A tuple of two normalized floats (``0.0``-``1.0``) describing the portion
    of the parent's width and height this widget prefers to occupy.
    
    Examples::
    
        # Prefer to take up all space within the parent
        widget.size_hint = (1.0, 1.0)
    
        # Prefer to take up the full width & half the height of the parent
        widget.size_hint = (1.0, 0.5)
        # Prefer using 1/10th of the available width & height
        widget.size_hint = (0.1, 0.1)

``size_hint_min``
    A tuple of two integers defining the minimum width and height of the
    widget. These values should be taken into account by :class:`UILayout` when
    a ``size_hint`` is given for the axis.

``size_hint_max``
    A tuple of two integers defining the maximum width and height of the
    widget. These values should be taken into account by :class:`UILayout` when
    a ``size_hint`` is given for the axis.

.. warning:: Size hints do nothing on their own!

    They are hints to :class:`UILayout` instances, which may choose to use or
    ignore them.

UILayout
````````

:py:class:`~arcade.gui.UILayout` are widgets, which reserve the right to move
or resize children. They might respect special properties of a widget like
``size_hint``, ``size_hint_min``, or ``size_hint_max``.

The :py:class:`arcade.gui.UILayout` must only resizes a child's dimension (x or y
axis) if ``size_hint`` provides a value for the axis, which is not ``None`` for
the dimension.


Drawing
=======

The GUI is optimised to be as performant as possible. This means that the GUI
splits up the positioning and rendering of each widget and drawing of the result on screen.

Widgets are positioned and then rendered into a framebuffer (something like a window sized image),
which is only updated if a widget changed and requested rendering
(via :py:meth:`~arcade.gui.UIWidget.trigger_render` or :py:meth:`~arcade.gui.UIWidget.trigger_full_render`).

The :py:class:`~arcade.gui.UIManager` `draw` method, will check if updates are required and
finally draws the framebuffer on screen.

Layouting and Rendering
```````````````````````

:py:class:`~arcade.gui.UIManager` triggers layouting and rendering of the GUI before the actual frame draw (if necessary).
This way, the GUI can adjust to multiple changes only once.

Layouting is a two-step process:
1. Prepare layout, which prepares children and updates own values
2. Do layout, which actually sets the position and size of the children

Rendering is not executed during each draw call.
Changes to following widget properties will trigger rendering:

- rect
- children
- background
- border_width, border_color
- padding
- widget-specific properties (like text, texture, ...)

:py:meth:`~arcade.gui.UIWidget.do_render` is called recursively if rendering
was requested via :py:meth:`~arcade.gui.UIWidget.trigger_render`. In case
widgets have to request their parents to render, use
:py:meth:`arcade.gui.UIWidget.trigger_full_render`.

The widget has to draw itself and child widgets within
:py:meth:`~arcade.gui.UIWidget.do_render`. Due to the deferred functionality
render does not have to check any dirty variables, as long as state changes use
the :py:meth:`~arcade.gui.UIWidget.trigger_full_render` method.

For widgets, that might have transparent areas, they have to request a full
rendering.

.. warning::

    Enforced rendering of the whole GUI might be very expensive!

Layout Algorithm by example
```````````````````````````

:py:class:`arcade.gui.UIManager` triggers the layout and render process right
before the actual frame draw. This opens the possibility to adjust to multiple
changes only once.

**Example**: Executed steps within :py:class:`~arcade.gui.UIBoxLayout`:

1. :py:meth:`~arcade.UIBoxLayout.prepare_layout` updates own size_hints
2. :py:meth:`~arcade.UIBoxLayout.do_layout`
    1. Collect current ``size``, ``size_hint``, ``size_hint_min`` of children
    2. Calculate the new position and sizes
    3. Set position and size of children
3. Recursively call ``do_layout`` on child layouts (last step in
   :py:meth:`~arcade.gui.UIBoxLayout.do_layout`)

.. code-block::

         ┌─────────┐          ┌────────┐                      ┌────────┐
         │UIManager│          │UILayout│                      │children│
         └────┬────┘          └───┬────┘                      └───┬────┘
              │ prepare_layout() ┌┴┐                              │
              │─────────────────>│ │                              │
              │                  │ │                              │
              │     ╔═══════╤════╪═╪══════════════════════════════╪══════════════╗
              │     ║ LOOP  │  sub layouts                        │              ║
              │     ╟───────┘    │ │                              │              ║
              │     ║            │ │       prepare_layout()       │              ║
              │     ║            │ │ ─────────────────────────────>              ║
              │     ╚════════════╪═╪══════════════════════════════╪══════════════╝
              │                  │ │                              │
              │<─ ─ ─ ─ ─ ─ ─ ─ ─│ │                              │
              │                  │ │                              │
              │ do_layout()      │ │                              │
              │─────────────────>│ │                              │
              │     ╔════════════╪═╪════╤═════════════════════════╪══════════════╗
              │     ║ place children    │                         │              ║
              │     ╟───────────────────┘                         │              ║
              │     ║            │ │   use size, size_hint, ...   │              ║
              │     ║            │ │ <─────────────────────────────              ║
              │     ║            │ │                              │              ║
              │     ║            │ │       set size and pos       │              ║
              │     ║            │ │ ─────────────────────────────>              ║
              │     ╚════════════╪═╪══════════════════════════════╪══════════════╝
              │                  │ │                              │
              │                  │ │                              │
              │     ╔═══════╤════╪═╪══════════════════════════════╪══════════════╗
              │     ║ LOOP  │  sub layouts                        │              ║
              │     ╟───────┘    │ │                              │              ║
              │     ║            │ │          do_layout()         │              ║
              │     ║            │ │ ─────────────────────────────>              ║
              │     ╚════════════╪═╪══════════════════════════════╪══════════════╝
              │                  └┬┘                              │
              │                   │                               │
              │<─ ─ ─ ─ ─ ─ ─ ─ ─ │                               │
         ┌────┴────┐          ┌───┴────┐                      ┌───┴────┐
         │UIManager│          │UILayout│                      │children│
         └─────────┘          └────────┘                      └────────┘

Size hint support
^^^^^^^^^^^^^^^^^

+--------------------------+------------+----------------+----------------+
|                          | size_hint  | size_hint_min  | size_hint_max  |
+==========================+============+================+================+
| :class:`UIAnchorLayout`  | X          | X              | X              |
+--------------------------+------------+----------------+----------------+
| :class:`UIBoxLayout`     | X          | X              | X              |
+--------------------------+------------+----------------+----------------+
| :class:`UIGridLayout`    | X          | X              | X              |
+--------------------------+------------+----------------+----------------+
| :class:`UIManager`       | X          | X              | X              |
+--------------------------+------------+----------------+----------------+

UIMixin
=======

Mixin classes are a base class which can be used to apply some specific
behaviour. Currently the available Mixins are still under heavy development.

Available:

- :py:class:`UIDraggableMixin` - Makes a widget draggable with the mouse.
- :py:class:`UIMouseFilterMixin` - Captures all mouse events.
- :py:class:`UIWindowLikeMixin` - Makes a widget behave like a window, combining draggable and mouse filter behaviour.

UIConstructs
============

Constructs are predefined structures of widgets and layouts like a message box.

Available:

- :py:class:`UIMessageBox` - A simple message box with a title, message and buttons.
- :py:class:`UIButtonRow` - A row of buttons.

Available Elements
==================

Buttons
```````

As with most widgets, buttons take ``x``, ``y``, ``width``, and ``height``
parameters for their sizing. Buttons specifically have two more parameters -
``text`` and ``multiline``.

All button types support styling. And they are text widgets, which means you
can use the :py:attr:`~arcade.gui.UITextWidget.ui_label` attribute to get the
:py:class:`~arcade.gui.UILabel` component of the button.

Flat button
^^^^^^^^^^^

**Name**: :py:class:`~arcade.gui.FlatButton`

A flat button for simple interactions (hover, press, release, click). This
button is created with a simple rectangle. Flat buttons can quickly create a
nice-looking button. However, depending on your use case, you may want to use
a texture button to further customize your look and feel.

Styling options are shown in the table below.

+----------------+------------------------------------------------------------+
|Name            |Description                                                 |
+================+============================================================+
|``font_size``   |Font size for the button text. Defaults to 12.              |
+----------------+------------------------------------------------------------+
|``font_name``   |Font name or family for the button text. If a tuple is      |
|                |supplied then Arcade will attempt to load all of the fonts, |
|                |prioritizing the first one. Defaults to                     |
|                |``("calibri", "arial")``.                                   |
+----------------+------------------------------------------------------------+
|``font_color``  |Font color for the button text (foreground). Defaults to    |
|                |white for normal, hover, and disabled states. Defaults to   |
|                |black for pressed state.                                    |
+----------------+------------------------------------------------------------+
|``bg``          |Background color of the button. This modifies the color of  |
|                |the rectangle within the button and not the border. Instead |
|                |of making each of these different colors for each of your   |
|                |buttons, set these towards a common color theme. Defaults to|
|                |gray for hover and disabled states. Otherwise it is white.  |
+----------------+------------------------------------------------------------+
|``border``      |Border color. It is common to only modify this in a focus or|
|                |hover state. Defaults to white or turquoise for hover.      |
+----------------+------------------------------------------------------------+
|``border_width``|Width of the border/outline of the button. It is common to  |
|                |make this thicker on a hover or focus state, however an     |
|                |overly thick border will result in your GUI looking old or  |
|                |low-quality. Defaults to 2.                                 |
+----------------+------------------------------------------------------------+

Image/texture button
^^^^^^^^^^^^^^^^^^^^

**Name**: :py:class:`~arcade.gui.UITextureButton`

An image button. Textures are supplied from :py:func:`arcade.load_texture` for
simple interactions (hover, press, release, click). A texture lets you further
customize the look of the widget better than styling.

A texture button has a few more arguments than a flat button. ``texture``,
``texture_hovered``, and ``texture_pressed`` will change the texture displayed
on the button respectively. ``scale`` will change the scaling or size of the
button - it's similar to the sprite :py:attr:`~arcade.BasicSprite.scale`.

.. hint::
    This widget *does* have ``width`` and ``height`` parameters, but they only
    stretch the texture instead of resizing it with keeping the borders. This
    feature is currently in-progress.

Texture buttons have fewer styling options when they have a texture compared to
flat buttons.

+----------------+------------------------------------------------------------+
|Name            |Description                                                 |
+================+============================================================+
|``font_size``   |Font size for the button text. Defaults to 12.              |
+----------------+------------------------------------------------------------+
|``font_name``   |Font name or family for the button text. If a tuple is      |
|                |supplied then Arcade will attempt to load all of the fonts, |
|                |prioritizing the first one. Defaults to                     |
|                |``("calibri", "arial")``.                                   |
+----------------+------------------------------------------------------------+
|``font_color``  |Font color for the button text (foreground). Defaults to    |
|                |white for normal, hover, and disabled states. Defaults to   |
|                |black for pressed state.                                    |
+----------------+------------------------------------------------------------+
|``border_width``|Width of the border/outline of the button. It is common to  |
|                |make this thicker on a hover or focus state, however an     |
|                |overly thick border will result in your GUI looking old or  |
|                |low-quality. Defaults to 2.                                 |
+----------------+------------------------------------------------------------+

Text widgets
````````````

All text widgets take ``x`` and ``y`` positioning parameters. They also accept
``text`` and ``multiline`` options.

Label
^^^^^

**Name**: :py:class:`~arcade.gui.UILabel`

A label is used to display text as instruction for the user. Multiline text is
supported, and what would have been its style options were moved into the
parameters.

This widget has no style options whatsoever, and they have been moved into the
parameters. ``bold`` and ``italic`` will set the text to bold or italic.
``align`` specifies the justification of the text. Additionally it takes
``font_name``, ``font_size``, and ``text_color`` options.

Using the :py:attr:`~arcade.gui.UILabel.label` property accesses the internal
:py:class:`~arcade.Text` class. 

.. hint::
    A :py:attr:`~arcade.gui.UILabel.text` attribute can modify the displayed
    text. Beware-calling this again and again will give a lot of lag. Use
    :py:meth:`~arcade.Text.begin_update` and py:meth:`~arcade.Text.end_update`
    to speed things up.

Text input field
^^^^^^^^^^^^^^^^

**Name**: :py:class:`~arcade.gui.UIInputText`

A text field allows a user to input a basic string. It uses pyglet's
:py:class:`~pyglet.text.layout.IncrementalTextLayout` and its
:py:class:`~pyglet.text.caret.Caret`. These are stored in ``layout`` and
``caret`` properties.

This widget takes ``width`` and ``height`` properties and uses a rectangle to
display a background behind the layout.

A text input field allows the user to move a caret around text to modify it, as
well as selecting parts of text to replace or delete it. Motion symbols for a
text field are listed in :py:mod:`pyglet.window.key` module.

Text area
^^^^^^^^^

**Name**: :py:class:`~arcade.gui.UITextArea`

A text area is a scrollable text widget. A user can scroll the mouse to view a
rendered text document. **This does not support editing text**. Think of it as
a scrollable label instead of a text field.

``width`` and ``height`` allocate a size for the text area. If text does not
fit within these dimensions then only part of it will be displayed. Scrolling
the mouse will display other sections of the text incrementally. Other
parameters include ``multiline`` and ``scroll_speed``. See
:py:attr:`~pyglet.text.layout.ScrollableTextLayout.view_y` on scroll speed.

Use ``layout`` and ``doc`` to get the pyglet layout and document for the
text area, respectively.

.. _UIEvent:

User-interface events
=====================

Arcade's GUI events are fully typed dataclasses, which provide information
about an event affecting the UI.

All pyglet window events are converted by the
:py:class:`~arcade.gui.UIManager` into :class:`UIEvents` and passed via
:py:meth:`~pyglet.event.EventDispatcher.dispatch_event` to the
:py:meth:`~arcade.gui.UIWidget.on_event` callbacks.

Widget-specific events (such as :py:class:`~arcade.gui.UIOnClickEvent` are
dispatched via ``on_event`` and are then  dispatched as specific event types
(like ``on_click``).

A full list of event attributes is shown below.

+---------------------------+-----------------------------------------+
|Event                      |Attributes                               |
+===========================+=========================================+
|``UIEvent``                |None                                     |
+---------------------------+-----------------------------------------+
|``UIMouseEvent``           |``x``, ``y``                             |
+---------------------------+-----------------------------------------+
|``UIMouseMovementEvent``   |``dx``, ``dy``                           |
+---------------------------+-----------------------------------------+
|``UIMousePressEvent``      |``dx``, ``dy``, ``button``, ``modifiers``|
+---------------------------+-----------------------------------------+
|``UIMouseDragEvent``       |``dx``, ``dy``                           |
+---------------------------+-----------------------------------------+
|``UIMouseScrollEvent``     |``scroll_x``, ``scroll_y``               |
+---------------------------+-----------------------------------------+
|``UIKeyEvent``             |``symbol``, ``modifiers``                |
+---------------------------+-----------------------------------------+
|``UIKeyReleaseEvent``      |None                                     |
+---------------------------+-----------------------------------------+
|``UITextEvent``            |``text``                                 |
+---------------------------+-----------------------------------------+
|``UITextMotionEvent``      |``motion``                               |
+---------------------------+-----------------------------------------+
|``UITextMotionSelectEvent``|``selection``                            |
+---------------------------+-----------------------------------------+
|``UIOnClickEvent``         |None                                     |
+---------------------------+-----------------------------------------+
|``UIOnUpdateEvent``        |``dt``                                   |
+---------------------------+-----------------------------------------+
|``UIOnChangeEvent``        |``old_value``, ``new_value``             |
+---------------------------+-----------------------------------------+
|``UIOnActionEvent``        |``action``                               |
+---------------------------+-----------------------------------------+

- :py:class:`arcade.gui.UIEvent`. Base class for all events.
- :py:class:`arcade.gui.UIMouseEvent`. Base class for mouse-related events.
    - :py:class:`arcade.gui.UIMouseMovementEvent`. Mouse motion. This event
      has an additional ``pos`` property that returns a tuple of the x and y
      coordinates.
    - :py:class:`~arcade.gui.UIMousePressEvent`. Mouse button pressed.
    - :py:class:`~arcade.gui.UIMouseDragEvent`. Mouse pressed and moved (drag).
    - :py:class:`~arcade.gui.UIMouseReleaseEvent`. Mouse button release.
    - :py:class:`~arcade.gui.UIMouseScrollEvent`. Mouse scroll.
- :py:class:`~arcade.gui.UITextEvent`. Text input from user. This is only used
  for text fields and is the text as a string that was inputed.
- :py:class:`~arcade.gui.UITextMotionEvent`. Text motion events. This includes
  moving the text around with the caret. Examples include using the arrow
  keys, backspace, delete, or any of the home/end and PgUp/PgDn keys. Holding
  ``Control`` with an arrow key shifts the caret by a entire word or paragraph.
  Moving the caret via the mouse does not trigger this event.
- :py:class:`~arcade.gui.UITextMotionSelectEvent`. Text motion events for
  selection. Holding down the ``Shift`` key and pressing arrow keys
  (``Control`` optional) will select character(s). Additionally, using a
  ``Control-A`` keyboard combination will select all text. Selecting text via
  the mouse does not trigger this event.
- :py:class:`~arcade.gui.UIOnUpdateEvent`. This is a callback to the arcade
  :py:class:`~arcade.Window.on_update` method.

Widget-specific events
``````````````````````

Widget events are only dispatched as a pyglet event on a widget itself and are
not passed through the widget tree.

- :py:class:`~arcade.gui.UIOnClickEvent`. Click event of
  :py:class:`~arcade.gui.UIInteractiveWidget` class. This is triggered on
  widget press.
- :py:class:`~arcade.gui.UIOnChangeEvent`. A value of a
  :py:class:`~arcade.gui.UIWidget` has changed.
- :py:class:`~arcade.gui.UIOnActionEvent`. An action results from interaction
  with the :py:class:`~arcade.gui.UIWidget` (mostly used in constructs)

Different event systems
=======================

Arcade's GUI uses different event systems, dependent on the required flow. A
game developer should mostly interact with user-interface events, which are
dispatched from specific :py:class:`~arcade.gui.UIWidget`s like an ``on_click``
of a button.

In cases where a developer implement own widgets themselves or want to
modify the existing GUI behavior, the developer might register own
pyglet event types on widgets or overwrite the
:py:class:`~arcade.gui.UIWidget.on_event` method. In that case, refer to
existing widgets as an example.

Pyglet window events
````````````````````

Pyglet window events are received by :py:class:`~arcade.gui.UIManager`.

You can dispatch them via::

    UIWidget.dispatch_event("on_event", UIEvent(...))

Window events are wrapped into subclasses of :py:class:`~arcade.gui.UIEvent`.

Pyglet event dispatcher - UIWidget
``````````````````````````````````

Widgets implement pyglet's :py:class:`~pyglet.event.EventDispatcher` and
register an ``on_event`` event type.

:py:meth:`~arcade.gui.UIWidget.on_event` contains specific event handling and
should not be overwritten without deeper understanding of the consequences.

To add custom event handling, use the decorator syntax to add another
listener::

    @UIWidget.event("on_event")

User-interface events
`````````````````````

User-interface events are typed representations of events that are passed
within the GUI. Widgets might define and dispatch their own subclasses of these
events.

Property
````````

:py:class:`~arcade.gui.Property` is an pure-Python implementation of Kivy-like Properties.
They are used to detect attribute changes of widgets and especially to trigger
rendering. They are mostly used within GUI widgets, but are globally available since 3.0.0.

Properties are a less verbose way to implement the observer pattern compared to the property decorator.
