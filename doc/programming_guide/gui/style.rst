.. _gui_style:

GUI Style
---------

    ``arcade.experimental.uistyle`` is an experimental component, which might change in upcoming versions.

``arcade.experimental.uistyle`` provides style dicts, which are used within :class:`UIWidget` to provide the colors for default appearance.

Style Parameters
================

:class:`UIWidget` load style parameters from a dict like object, which can be passed as :attr:`UIWidget.style`.

Style Parameters
................

Following parameters are used within multiple :class:`UIWidget`. Style parameters are prefixed with the :class:`UIWidget` state (``normal``, ``hovered`` and ``pressed``)

**<state>_font_size**
    Font size of any text within the :class:`UIWidget`

**<state>_font_name**
    Font of any text within the :class:`UIWidget`

**<state>_font_color**
    Color of any text within the :class:`UIWidget`

**<state>_bg**
    Background color, also used as the primary color within an :class:`UIWidget`

**<state>_border**
    Color of :class:`UIWidget` border

**<state>_border_width**
    Width of :class:`UIWidget` border in pixel

**<state>_filled_bar**
    Color used within bars like slider to indicate fill state

**<state>_unfilled_bar**
    Color used within bars like slider for unfilled background


UIWidget Style
==============

UISlider
........

- ``<state>_filled_bar``
- ``<state>_unfilled_bar``
- ``<state>_bg`` - color of cursor
- ``<state>_border`` - outline of cursor
- ``<state>_border_width``

UIFlatButton
............

- ``<state>_font_name``
- ``<state>_font_size``
- ``<state>_font_color``
- ``<state>_bg``
- ``<state>_border``
- ``<state>_border_width``
