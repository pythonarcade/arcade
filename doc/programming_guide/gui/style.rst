.. _gui_style:

GUI Style
---------


With arcade 3.0 a whole new styling mechanism for GUI widgets was introduced.
The new styling allows more type safe and clear styling while staying flexible.

Following widgets support styling:

- :py:class:`~arcade.gui.UITextureButton`
- :py:class:`~arcade.gui.UIFlatButton`
- :py:class:`~arcade.gui.UISlider`

For an advanced description about the style system read the 'Advanced' section.

Basic Usage
===========

This section covers how to use the existing stylable widgets.

    In the following examples we will use the UIFlatButton as the stylable widget,
    you can do the same with any stylable widget listed above.


Quickstart
```````````

The following example shows how to adjust the style of a UIFlatButton.


.. code-block::

    # create an own style
    new_style = {
        # provide a style for each widget state
        "normal": UIFlatButton.UIStyle(), # use default values for `normal` state
        "hover": UIFlatButton.UIStyle(
            font_color=arcade.color.BLACK,
            bg=arcade.color.WHITE,
        ),
        "press": UIFlatButton.UIStyle(
            font_color=arcade.color.BLACK,
            bg=arcade.color.WHITE,
            border=arcade.color.WHITE,
        ),
        "disabled": UIFlatButton.UIStyle(
            bg=arcade.color.GRAY,
        )
    }

    UIFlatButton(style=new_style)


Default style
``````````````

Stylable widgets have a property which holds the default style for
the type of widget. For the UIFLatButton this is `UIFlatButton.DEFAULT_STYLE`.

This default style will be used if no other style is provided within the constructor.
The default style looks like this:

.. code-block::

    class UIFlatButton(UIInteractiveWidget, UIStyledWidget, UITextWidget):

        DEFAULT_STYLE = {
            "normal": UIStyle(),
            "hover": UIStyle(
                font_size=12,
                font_name=("calibri", "arial"),
                font_color=arcade.color.WHITE,
                bg=(21, 19, 21, 255),
                border=(77, 81, 87, 255),
                border_width=2,
            ),
            "press": UIStyle(
                font_size=12,
                font_name=("calibri", "arial"),
                font_color=arcade.color.BLACK,
                bg=arcade.color.WHITE,
                border=arcade.color.WHITE,
                border_width=2,
            ),
            "disabled": UIStyle(
                font_size=12,
                font_name=("calibri", "arial"),
                font_color=arcade.color.WHITE,
                bg=arcade.color.GRAY,
                border=None,
                border_width=2,
            )
        }

Style attributes
`````````````````

A UIStyle is a typed description of available style options.
For the UIFlatButton the supported attributes are:


================ ================= ===================== ==================================
Name              Type              Default value         Description
================ ================= ===================== ==================================
font_size        int                12                    Size of the text on the button
font_name        FontNameOrNames    ("calibri", "arial")  Font of the text
font_color       RGBA255            arcade.color.WHITE    Color of text
bg               RGBA255            (21, 19, 21, 255)     Background color
border           Optional           None                  Border color
border_width     int                0                     Border width
================ ================= ===================== ==================================

The style attribute is a dictionary, which maps a state like 'normal, 'hover' etc.
to an instance of UIFlatButton.UIStyle.

Wellknown states
`````````````````

======== ======================================================
Name     Description
======== ======================================================
normal   The default state of a widget.
hover    Mouse hovered over an interactive widget.
press    Mouse is pressed while hovering over the widget.
disabled The widget is disabled.
======== ======================================================


Advanced
========

This section describes the styling system itself,
and how it can be used to create own stylable widgets or extend existing ones.

Stylable widgets inherit from `UIStyledWidget`, which provides two basic features:

1. owns a style property, which provides a mapping between a widgets state and style to be applied
2. provides an abstractmethod which have to provide a state (which is a simple string)


Tha basic idea:
- a stylable widget has a state (e.g. 'normal', 'hover', 'press', or 'disabled')
- the state is used to define, which style will be applied

Your own stylable widget
````````````````````````

.. code-block::

    class MyColorBox(UIStyledWidget, UIInteractiveWidget, UIWidget):
        """
        A colored box, which changes on mouse interaction
        """

        # create the style class, which will be used to define style for any widget state
        @dataclass
        class UIStyle(UIStyleBase):
            color: RGBA255 = arcade.color.GREEN


        DEFAULT_STYLE = {
            "normal": UIStyle(),
            "hover": UIStyle(color=arcade.color.YELLOW),
            "press": UIStyle(color=arcade.color.RED),
            "disabled": UIStyle(color=arcade.color.GRAY)
        }

    def get_current_state(self) -> str:
        """Returns the current state of the widget i.e disabled, press, hover or normal."""
        if self.disabled:
            return "disabled"
        elif self.pressed:
            return "press"
        elif self.hovered:
            return "hover"
        else:
            return "normal"

    def do_render(self, surface: Surface):
        self.prepare_render(surface)

        # get current style
        style: MyColorBox.UIStyle = self.get_current_style()

        # Get color from current style, it is a good habit to be
        # bullet proven for missing values in case a dict is provided instead of a UIStyle
        color = style.get("color", MyColorBox.UIStyle.bg)

        # render
        if color: # support for not setting a color at all
            surface.clear(bg_color)



