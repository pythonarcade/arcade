"""
Overview
--------

This module provides classes which can be used to create a GUI.

The central component is the UIManager. You can chose between two of them:

- :py:class:`arcade.gui.UIManager` (will be deprecated)

    - Manages UIElements
    - Supports hover and focus of UIElements

- :py:class:`arcade.gui.UILayoutManager`

    - Like :py:class:`~arcade.gui.UIManager`
    - Place UIElements via :py:class:`~arcade.gui.layouts.UILayout` - :py:meth:`~arcade.gui.UILayoutManager.pack()`
    - Supports window-like modals - :py:meth:`~arcade.gui.UILayoutManager.push()`


Starting with :py:class:`~arcade.gui.UIManager` or :py:class:`~arcade.gui.UILayoutManager` you can add new :py:class:`~arcade.gui.UIElement`
which will be drawn on top of your other sprites.

Creating a UIManager will register to window hooks like `on_key_press`, to handle the interactions automatically.

To draw all added elements within a UIManager use `on_draw()`.

Details
-------

The UI interactions are implemented using Pyglets :py:class:`pyglet.event.EventDispatcher`.
The :py:class:`~arcade.gui.UIManager` subscribes to all :py:class:`~arcade.Window`
events and converts them into a :py:class:`~arcade.gui.UIEvent` object,
which is passed to all added :py:class:`~arcade.gui.UIElement`.

Available :py:class:`~arcade.gui.UIElement`

* :py:class:`~arcade.gui.UILabel`
* :py:class:`~arcade.gui.UIInputBox`
* :py:class:`~arcade.gui.UIImageButton`
* :py:class:`~arcade.gui.UIFlatButton`
* :py:class:`~arcade.gui.UIGhostFlatButton`
* :py:class:`~arcade.gui.UIToggle`

Within the `layouts` subpackage you will find following implementations:

* :py:class:`~arcade.gui.UIBoxLayout` - Places children in a horizontal or vertical line
* :py:class:`~arcade.gui.UIAnchorLayout` - Places children relative to `top`, `left`, `bottom`, `right`, `center_x`, or `center_y`


Examples
--------

Run examples with ``python -m arcade.gui.examples.<example name>``

* show_all - Show all components
* show_decorator_example - Show example interaction using event decorators
* show_id_example - Use id of :py:class:`~arcade.gui.UIElement` for interaction control
* show_image_from_style - Use :py:class:`~arcade.gui.UIStyle` to customize appearance of an element
* show_uiflatbutton - :py:class:`~arcade.gui.UIFlatButton` example
* show_uiflatbutton_custom_style - :py:class:`~arcade.gui.UIFlatButton` with custom styling
* show_uiimagetoggle - Example with an :py:class:`~arcade.gui.UIImageToggle`
* show_uiinputbox - Example with an :py:class:`~arcade.gui.UIInputBox`
* show_uilabel - Show text with an :py:class:`~arcade.gui.UILabel`
* show_uilayouts - Example show of :py:class:`~arcade.gui.UILayouts`
* show_uilayouts_hud_inventory - Example how to build a HUD inventory
* show_uilayouts_inventory - Example how to build a window-like inventory
* show_uilayouts_start_menu - Example how to build a simple start menu

"""
from arcade.gui import utils
from arcade.gui.elements import UIClickable, UIElement
from arcade.gui.elements.flat_button import UIAbstractFlatButton, UIFlatButton, UIGhostFlatButton
from arcade.gui.elements.image_button import UIImageButton
from arcade.gui.elements.inputbox import UIInputBox
from arcade.gui.elements.box import UITextureBox, UIColorBox
from arcade.gui.elements.label import UILabel
from arcade.gui.elements.toggle import UIAbstractToggle, UIToggle, UIImageToggle
from arcade.gui.events import (  # deprecated
    MOUSE_DRAG,
    MOUSE_PRESS,
    MOUSE_RELEASE,
    MOUSE_SCROLL,
    KEY_PRESS,
    KEY_RELEASE,
    TEXT_INPUT,
    TEXT_MOTION,
    TEXT_MOTION_SELECTION,
    RESIZE,
    MOUSE_MOTION,
)
from arcade.gui.events import UIEvent
from arcade.gui.exceptions import UIException
from arcade.gui.layouts import UILayout
from arcade.gui.layouts.anchor import UIAnchorLayout
from arcade.gui.layouts.box import UIBoxLayout
from arcade.gui.layouts.manager import UILayoutManager
from arcade.gui.layouts.manager import UIStack
from arcade.gui.manager import UIManager
from arcade.gui.manager import UIAbstractManager
from arcade.gui.style import UIStyle

__all__ = [
    "UIAbstractFlatButton",
    "UIAbstractManager",
    "UIAbstractToggle",
    "UIAnchorLayout",
    "UIBoxLayout",
    "UIClickable",
    "UIColorBox",
    "UIElement",
    "UIEvent",
    "UIException",
    "UIFlatButton",
    "UIImageButton",
    "UIImageToggle",
    "UIInputBox",
    "UILayoutManager",
    "UILayout",
    "UILabel",
    "UIManager",
    "UIGhostFlatButton",
    "UIStack",
    "UIStyle",
    "UIToggle",
    "UITextureBox",
    ###
    # deprecated, use arcade.gui.events
    ###
    "MOUSE_DRAG",
    "MOUSE_PRESS",
    "MOUSE_RELEASE",
    "MOUSE_SCROLL",
    "KEY_PRESS",
    "KEY_RELEASE",
    "TEXT_INPUT",
    "TEXT_MOTION",
    "TEXT_MOTION_SELECTION",
    "RESIZE",
    "MOUSE_MOTION",
]
