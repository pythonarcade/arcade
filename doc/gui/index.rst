.. _gui_concepts:

GUI Concept
-----------

GUI elements are represented as instances of :class:`UIWidget`. The GUI is structured like a tree, every widget
can have other widgets as children.

The root of the tree is the :class:`UIManager`. The UIManager connects the user interactions with the GUI.
Read more about :ref:`UIEvents`.

Classes of Arcades GUI code are prefixed with UI- to make them easy to identify and search for in autocompletion.

UIWidget
========

:class:`UIWidgets` are the core of Arcades GUI. A widget represents the behaviour and graphical
representation of any element (like Buttons or Text)

A :class:`UIWidget` has following properties

**rect**
    x and y coordinates (bottom left of the widget), width and height

**children**
    Child widgets, rendered within this widget
    A :class:`UIWidget` will not move or resize its children, use a :class:`UILayout` instead.

**min_size**
    tuple of two ints, defines the minimal size the element has to get in pixel.

**size_hint**
    tuple of two floats, defines how much of the parents space it would like to occupy (range: 0.0-1.0).
    For maximal vertical and horizontal expansion, define `size_hint` of 1 for the axis.

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
    effect the widget on its own. :class:`UILayouts` may use these information to place or resize a widget.

UILayout and UIWrapper
======================

:class:`UILayout` are widgets, which reserve the option to move or resize children. They might respect special properties
of a widget like *size_hint*, *size_hint_min*, or *size_hint_max*.

:class:`UIWrapper` are widgets that are used to wrap a child widget to apply additional effects like borders or space around.
They only contain one child widget, and raise Exceptions, if another widget is added.

Constructs
==========

Constructs are predefined structures of widgets and layouts like a message box or (not yet available) file dialogues.

Available Constructs



Available Widgets
=================

- :class:`UIWidgets`:
    - :class:`UIFlatButton` - 2D flat button for simple interactions (hover, press, release, click)
    - :class:`UITextureButton` - textured button (use :meth:`arcade.load_texture()`) for simple interactions (hover, press, release, click)
    - :class:`UILabel` - Simple text, supports multiline
    - :class:`UIInputText` - field to accept user text input
    - :class:`UITextArea` - Multiline scrollable text widget.
    - :class:`UISpriteWidget` - Embeds a Sprite within the GUI tree
- :class:`UILayout`:
    - :class:`UIBoxLayout` - Places widgets next to each other (vertical or horizontal)
- :class:`UIWrapper`:
    - :class:`UIPadding` - Add space around a widget
    - :class:`UIBorder` - Add border around a widget
    - :class:`UIAnchorWidget` - Used to position UIWidgets relative on screen
- Constructs
    - :class:`UIMessageBox` - Popup box with a message text and a few buttons.

UIEvents
--------

UIEvents are fully typed dataclasses, which provide information about a event effecting the UI.
Events are passed top down to every :class:`UIWidget` by the UIManager.

General pyglet window events are converted by the UIManager into UIEvents and passed via dispatch_event
to the on_event callbacks.

Widget specific UIEvents like UIOnClick are dispatched via "on_event" and are then  dispatched as specific event types (like 'on_click')

UIEventTypes
++++++++++++

- :class:`UIEvent` - Base class for all events
- :class:`UIMouseEvent` - Base class for mouse related event
    - :class:`UIMouseMovement` - Mouse moves
    - :class:`UIMousePress` - Mouse button pressed
    - :class:`UIMouseDrag` - Mouse pressed and moved (drag)
    - :class:`UIMouseRelease` - Mouse button released
    - :class:`UIMouseScroll` - Mouse scolls
- :class:`UITextEvent` - Text input from user
- :class:`UITextMotion` - Text motion events like arrows
- :class:`UITextMotionSelect` - Text motion events for selection
- :class:`UIOnClick` - Click event of :class:`UIInteractiveWidget` class
