.. _gui_style:

GUI Style
---------


Arcade 3.0 added a new approach for styling GUI widgets. It is flexible, yet also
improves clarity and type safety.


.. _gui_style_which_widgets:

Which Widgets Can I Style?
==========================

The following widgets support styling:

- :py:class:`~arcade.gui.UITextureButton`
- :py:class:`~arcade.gui.UIFlatButton`
- :py:class:`~arcade.gui.UISlider`


Basic Usage
===========

This section will style a :py:class:`~arcade.gui.UIFlatButton` as an example. You
can use the same general approach for other stylable widgets, but you may want to
check their documentation for additional values they may support.

To create your own widgets, please see the 'Advanced' section.


Quickstart
``````````

The following example shows how to adjust the style.

.. code-block::

    # Styles are dictionaries of UIStyle objects
    new_style = {
        # You should provide a style for each widget state
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

    # Pass the style dictionary when creating a UI element
    UIFlatButton(style=new_style)


Default style
`````````````

Each stylable widget class has a ``DEFAULT_STYLE`` class attribute to hold the
default style for that type of widget. For example, on
:py:class:`~arcade.gui.UIFlatButton`, you can access this attribute via
``UIFlatButton.DEFAULT_STYLE``.

This default style will be used if no other style is provided when creating an instance
of the class.

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
````````````````

A UIStyle is a typed description of available style options.
For the UIFlatButton the supported attributes are:


================ =================== ======================== ==================================
Name              Type               Default value            Description
================ =================== ======================== ==================================
``font_size``    ``int``             12                       Size of the text on the button
``font_name``    ``FontNameOrNames`` ``("calibri", "arial")`` Font of the text
``font_color``   ``RGBA255``         ``arcade.color.WHITE``   Color of text
``bg``           ``RGBA255``         ``(21, 19, 21, 255)``    Background color
``border``       ``Optional``        ``None``                 Border color
``border_width`` ``int``             0                        Border width
================ =================== ======================== ==================================

The style attribute is a dictionary, which maps states such as ``normal``, ``hover``, ``press``,
and ``disabled`` to an instance of the class's ``UIStyle``.

Common states
`````````````

============ ======================================================
Name         Description
============ ======================================================
``normal``   The default state of a widget.
``hover``    The mouse is hovered over an interactive widget.
``press``    The mouse is pressed while hovering over the widget.
``disabled`` The widget is disabled.
============ ======================================================


Advanced
========

This section describes the styling system itself, and how it can be used to
create your own stylable widgets or extend existing ones.

Stylable widgets inherit from :py:meth:`~arcade.gui.UIStyledWidget`, which
provides two basic features:

1. A :py:attr:`~arcade.gui.UIStyledWidget.style` property, which provides a
   mapping between a widget's state and style to be applied.
2. Provides an ``abstractmethod`` to provide a state, which is a simple string.


Tha basic idea:

- A stylable widget has a state, which can be ``normal``, ``hover``, ``press``,
  or ``disabled``.
- The state is used to define which style will be applied.

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
            """Returns the current state of the widget i.e.disabled, press, hover or normal."""
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
