.. _gui_layouts:

GUI Layouts
-----------

Included Layouts
================

The GUI module provides a way to layout your GUI elements in a structured way.
Layouts dynamically resize the elements based on the size of the window.

The layouts are an optional part of the GUI, but highly recommended to use.
Mixing self positioning and layout positioning is possible, but can lead to unexpected results.

Layouts apply their layouting right before the rendering phase,
so the layout is always up-to-date for the rendering,
but will not be consistent after instantiation in your ``__init__()`` method.

To circumvent this, you can trigger a layout run by calling the `UIManager.execute_layout()`.


The following layouts are available:

- :class:`arcade.gui.UIBoxLayout`

    The `UIBoxLayout` class is used to arrange widgets in a
    horizontal or vertical box layout. Here are some key points to understand:

    1. **Orientation**:
    The layout can be either horizontal or vertical, controlled by the `vertical` parameter.

    2. **Alignment**:
    Widgets can be aligned within the layout using the `align` parameter.

    3. **Spacing**:
    The layout can have spacing between the widgets, controlled by the `space_between` parameter.

    4. **Size Hints**:
    The layout resizes widgets based on their `size_hint`, `size_hint_min` and `size_hint_max`.

    5. **Size**:
    The layout automatically updates its `size_hint_min` based on the minimal
    required space by its children after layout phase.

    In summary, `UIBoxLayout` provides a simple way to arrange widgets in a horizontal or
    vertical layout, allowing for alignment and spacing between the widgets.

- :class:`arcade.gui.UIAnchorLayout`

    The `UIAnchorLayout` class is used to arrange widgets
    in the center or at the edges of the layout.
    All children are independently anchored the specified anchor points.

    Here are some key points to understand:

    1. **Anchor**:
    The widget can be anchored to the center or at the edges of the layout using
    the `anchor_x` and `anchor_y` parameters. In addition to the anchor point,
    the widget can be offset from the anchor point using the `offset_x` and `offset_y` parameters.

    2. **Padding**:
    The layout can have padding to ensure spacing to the borders,
    controlled by the `padding` parameter.

    3. **Size**:
    The `UIAnchorLayout` is the only layout which by default fills the whole available space.
    (Default `size_hint=(1, 1)`)

    3. **Size Hints**:
    The layout resizes widgets based on their `size_hint`, `size_hint_min` and `size_hint_max`.

    In summary, `UIAnchorLayout` provides a way to anchor widgets to a position within the layout.
    This allows for flexible positioning of widgets within the layout.


- :class:`arcade.gui.UIGridLayout`

    The `UIGridLayout` class is used to arrange widgets in a grid format. Here are some key points to understand:

    1. **Grid Structure**:
    The layout is divided into a specified number of columns and rows. Widgets can be placed in these grid cells.

    2. **Spanning**:
    Widgets can span multiple columns and/or rows using the `column_span` and `row_span` parameters.

    3. **Dynamic Sizing**:
    Widgets can provide a `size_hint` to request dynamic space relative to the layout size.
    This means that the widget can grow or shrink based on the available space in the layout.

    4. **Alignment**:
    Widgets can be aligned within their grid cells using the `align_horizontal` and `align_vertical` parameters.

    5. **Spacing**:
    The layout can have horizontal and vertical spacing between the grid cells,
    controlled by the `horizontal_spacing` and `vertical_spacing` parameters.

    6. **Size**:
    The layout automatically updates its `size_hint_min` based on the minimal
    required space by its children after layouting.

    7. **Size Hints**:
    The layout resizes widgets based on their `size_hint`, `size_hint_min` and `size_hint_max`.

    In summary, `UIGridLayout` provides a flexible way to arrange widgets in a grid,
    allowing for dynamic resizing and alignment based on the layout's size
    and the widgets' size hints.

When to use which layout?
=========================

Choosing the right layout depends on the desired layout structure.
But often there are multiple ways to achieve the same layout.

Here are some guidelines to help you choose the right layout:

- Use `UIAnchorLayout` for anchoring widgets to a position within the layout.
  This is mostly useful to position widgets freely within the bounds of the layout.
  Commonly used as the root layout for the whole GUI.

- Use `UIBoxLayout` for simple horizontal or vertical layouts.
  This is useful for arranging widgets in a row or column.
  Multiple `UIBoxLayout` can be nested to create more complex layouts.

- Use `UIGridLayout` for arranging widgets in a grid format.
  This is useful for creating a grid of widgets, where columns and rows should each have a fixed size.

