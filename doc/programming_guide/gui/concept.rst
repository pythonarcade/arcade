.. _gui_concepts:

GUI Concepts
------------

GUI elements are represented as instances of :class:`UIWidget`. The GUI is structured like a tree, every widget
can have other widgets as children.

The root of the tree is the :class:`UIManager`. The UIManager connects the user interactions with the GUI.
Read more about :ref:`UIEvent`.

Classes of Arcades GUI code are prefixed with UI- to make them easy to identify and search for in autocompletion.

UIWidget
========

:class:`UIWidget` are the core of Arcades GUI. A widget represents the behaviour and graphical
representation of any element (like Buttons or Text)

A :class:`UIWidget` has following properties

**rect**
    x and y coordinates (bottom left of the widget), width and height

**children**
    Child widgets, rendered within this widget
    A :class:`UIWidget` will not move or resize its children, use a :class:`UILayout` instead.

**size_hint**
    tuple of two floats, defines how much of the parents space it would like to occupy (range: 0.0-1.0).
    For maximal vertical and horizontal expansion, define `size_hint` of 1 for the axis.

**size_hint_min**
    tuple of two ints, defines minimal size of the widget.
    If set, changing the size of a widget to a lower values will use this size instead.

**size_hint_max**
    tuple of two ints, defines maximum size of the widget.
    If set, changing the size of a widget to a higher values will use this size instead.

    *size_hint*, *size_hint_min*, and *size_hint_max* are values that are additional information of a widget, but do not
    effect the widget on its own. :class:`UILayout` may use these information to place or resize a widget.

Rendering
.........

:meth:`UIWidget.do_render` is called recursively if rendering was requested via :meth:`UIWidget.trigger_render`.
In case widgets have to request their parents to render use :meth:`UIWidget.trigger_full_render`

The widget has to draw itself and child widgets within :meth:`UIWidget.do_render`. Due to the deferred functionality
render does not have to check any dirty variables, as long as state changes use the trigger function.

For widgets, that might have transparent areas, they have to request a full rendering.

    Enforced rendering of the whole GUI might be very expensive!

UILayout
========

:class:`UILayout` are widgets, which reserve the option to move or resize children. They might respect special properties
of a widget like *size_hint*, *size_hint_min*, or *size_hint_max*.

The :class:`UILayout` only resize a child's dimension (x or y axis) if size_hint provides a value for the axis, which is not `None` for the dimension.


Algorithm
.........

:class:`UIManager` triggers the layout and render process right before the actual frame draw.
This opens the possibility, to adjust to multiple changes only ones.

Example: Executed steps within :class:`UIBoxLayout`:

1. :meth:`UIBoxLayout.do_layout`
    1. collect current size, size_hint, size_hint_min of children
    2. calculate the new position and sizes
    3. set position and size of children
2. recursive call `do_layout` on child layouts (last step in :meth:`UIBoxLayout.do_layout`)

.. code-block::

         ┌─────────┐          ┌────────┐                      ┌────────┐
         │UIManager│          │UILayout│                      │children│
         └────┬────┘          └───┬────┘                      └───┬────┘
              │   do_layout()    ┌┴┐                              │
              │─────────────────>│ │                              │
              │                  │ │                              │
              │                  │ │                              │
              │     ╔════════════╪═╪════╤═════════════════════════╪══════════════╗
              │     ║ place children    │                         │              ║
              │     ╟────────────────use size, size_hint, ...     │              ║
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
+++++++++++++++++

+--------------------------+------------+----------------+----------------+
|                          | size_hint  | size_hint_min  | size_hint_max  |
+==========================+============+================+================+
| :class:`UIAnchorLayout`  | X          | X              | X              |
+--------------------------+------------+----------------+----------------+
| :class:`UIBoxLayout`     | X          | X              | X              |
+--------------------------+------------+----------------+----------------+
| :class:`UIManager`       | X          | X              |                |
+--------------------------+------------+----------------+----------------+

UIMixin
=======

Mixin classes are a base class which can be used to apply some specific behaviour. Currently the available Mixins are
still under heavy development.

Constructs
==========

Constructs are predefined structures of widgets and layouts like a message box or (not yet available) file dialogues.


Available Elements
==================

- :class:`UIWidget`:
    - :class:`UIFlatButton` - 2D flat button for simple interactions (hover, press, release, click)
    - :class:`UITextureButton` - textured button (use :meth:`arcade.load_texture()`) for simple interactions (hover, press, release, click)
    - :class:`UILabel` - Simple text, supports multiline, fits content
    - :class:`UIInputText` - field to accept user text input
    - :class:`UITextArea` - Multiline scrollable text widget.
    - :class:`UISpriteWidget` - Embeds a Sprite within the GUI tree
- :class:`UILayout`:
    - :class:`UIBoxLayout` - Places widgets next to each other (vertical or horizontal)
    - :class:`UIAnchorLayout` - Places widgets within itself following anchor information
    - :class:`UIGridLayout` - Places widgets within a grid
- Constructs
    - :class:`UIMessageBox` - Popup box with a message text and a few buttons.
- Mixins
    - :class:`UIDraggableMixin` - Makes a widget draggable.
    - :class:`UIMouseFilterMixin` - Catches mouse events that occure within the widget boundaries.
    - :class:`UIWindowLikeMixin` - Combination of :class:`UIDraggableMixin` and :class:`UIMouseFilterMixin`.

.. _UIEvent:

UIEvents
========

UIEvents are fully typed dataclasses, which provide information about a event effecting the UI.

All pyglet window events are converted by the UIManager into UIEvents and passed via dispatch_event
to the ``on_event`` callbacks.

Widget specific UIEvents like UIOnClick are dispatched via "on_event" and are then  dispatched as specific event types (like 'on_click')

- :class:`UIEvent` - Base class for all events
- :class:`UIMouseEvent` - Base class for mouse related event
    - :class:`UIMouseMovementEvent` - Mouse moves
    - :class:`UIMousePressEvent` - Mouse button pressed
    - :class:`UIMouseDragEvent` - Mouse pressed and moved (drag)
    - :class:`UIMouseReleaseEvent` - Mouse button released
    - :class:`UIMouseScrollEvent` - Mouse scolls
- :class:`UITextEvent` - Text input from user
- :class:`UITextMotionEvent` - Text motion events like arrows
- :class:`UITextMotionSelectEvent` - Text motion events for selection
- :class:`UIOnUpdateEvent` - arcade.Window `on_update` callback

Widget specific events
......................

Widget events are only dispatched as a Pyglet event on a widget itself and are not passed through the widget tree.

- :class:`UIOnClickEvent` - Click event of :class:`UIInteractiveWidget` class
- :class:`UIOnChangeEvent` - A value of a :class:`UIWidget` has changed
- :class:`UIOnActionEvent` - An action results from interaction with the :class:`UIWidget` (mostly used in constructs)

Different Event Systems
=======================

The GUI uses different event systems, dependent on the required flow. A game developer should mostly interact with UIEvents
which are dispatched from specific UIWidgets like ``on_click`` of a button.

In rare cases a developer might implement some UIWidgets or wants to modify the existing GUI behavior. In those cases a
developer might register own Pyglet event types on UIWidgets or overwrite the ``UIWidget.on_event`` method.

Pyglet Window Events
....................

Received by UIManager, dispatched via ``UIWidget.dispatch_event("on_event", UIEvent(...))``.
Window Events are wrapped into subclasses of UIEvent.

Pyglet EventDispatcher - UIWidget
.................................

UIWidgets implement Pyglets EventDispatcher and register an ``on_event`` event type.
``UIWidget.on_event`` contains specific event handling and should not be overwritten without deeper understanding of the consequences.
To add custom event handling use the decorator syntax to add another listener (``@UIWidget.event("on_event")``).

UIEvents
........

UIEvents are typed representations of events that are passed within the GUI. UIWidgets might define and dispatch their own subclasses of UIEvents.

Property
........

``Property`` is an pure-Python implementation of Kivy Properties. They are used to detect attribute
changes of UIWidgets and trigger rendering. They should only be used in arcade internal code.

