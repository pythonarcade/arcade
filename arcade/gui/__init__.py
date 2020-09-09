"""
This module provides UIElements which can be used to ease the interaction
with the player.

Starting with :py:class:`arcade.gui.UIManager` you can add new :py:class:`arcade.gui.UIElement`
which will be drawn on top of your other sprites.

The UI interactions are implemented using Pyglets :py:class:`pyglet.event.EventDispatcher`.
The :py:class:`arcade.gui.UIManager` subscribes to all :py:class:`arcade.Window`
events and converts them into a :py:class:`arcade.gui.UIEvent` object,
which is passed to all added :py:class:`arcade.gui.UIElement`.

Available :py:class:`arcade.gui.UIElement`

* :py:class:`arcade.gui.UILabel`
* :py:class:`arcade.gui.UIInputBox`
* :py:class:`arcade.gui.UIImageButton`
* :py:class:`arcade.gui.UIFlatButton`
* :py:class:`arcade.gui.UIGhostFlatButton`
* :py:class:`arcade.gui.UIToggel`

Run examples with `python -m arcade.gui.examples.<example name>`

* show_all - Show all components
* show_decorator_example - Show example interaction using event decorators
* show_id_example - Using id off an :py:class:`arcade.gui.UIElement`
* show_uiflatbutton - :py:class:`arcade.gui.UIFlatButton` example
* show_uiflatbutton_custom_style - Flatbutton with custom styleing
* show_uiinputbox - Example with a :py:class:`arcade.gui.UIInputBox`
* show_uilabel - Show text with a :py:class:`arcade.gui.UILabel`

"""
from arcade.gui import utils
from arcade.gui.core import (
    UIEvent,
    UIElement,
    UIException,
    MOUSE_MOTION,
    MOUSE_PRESS,
    MOUSE_RELEASE,
    MOUSE_SCROLL,
    KEY_PRESS,
    KEY_RELEASE,
    TEXT_INPUT,
    TEXT_MOTION,
    TEXT_MOTION_SELECTION
)
from arcade.gui.elements import UIClickable
from arcade.gui.elements.flat_button import UIFlatButton, UIGhostFlatButton
from arcade.gui.elements.image_button import UIImageButton
from arcade.gui.elements.inputbox import UIInputBox
from arcade.gui.elements.label import UILabel
from arcade.gui.elements.toggle import UIToggle, UIImageToggle
from arcade.gui.manager import UIManager

__all__ = [
    'UIEvent',
    'UIManager',
    'UIElement',
    'UIException',
    'UILabel',
    'UIInputBox',
    'UIClickable',
    'UIFlatButton',
    'UIGhostFlatButton',
    'UIImageButton',
    'UIToggle',
    'UIImageToggle',
    'MOUSE_MOTION',
    'MOUSE_PRESS',
    'MOUSE_RELEASE',
    'MOUSE_SCROLL',
    'KEY_PRESS',
    'KEY_RELEASE',
    'TEXT_INPUT',
    'TEXT_MOTION',
    'TEXT_MOTION_SELECTION',
]
