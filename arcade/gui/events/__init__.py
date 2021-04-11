"""
The gui interaction is based on :py:class:`~arcade.gui.UIEvent`. Every Pyglet scheduled callback is converted into a
:py:class:`~arcade.gui.UIEvent` and passed to :py:class:`~arcade.gui.UIManager`, which passes it to its children.

.. note::
    :meth:`UIEvent.type` represent the :class:`~arcade.gui.UIEvent` type.
    It is planned to introduce subclasses of :class:`~arcade.gui.UIEvent` to provide better support for
    typing and autocompletion.


Known :py:class:`~arcade.gui.UIEvent` types and attributes:

:py:const:`arcade.gui.events.MOUSE_PRESS`
  * x - coordinate of the event
  * y - coordinate of the event
  * button - pressed mouse button from :py:mod:`pyglet.window.mouse`
  * modifiers - modifier key from :py:mod:`arcade.key`

:py:const:`arcade.gui.events.MOUSE_RELEASE`
  * x - coordinate of the event
  * y - coordinate of the event
  * button - pressed mouse button from :py:mod:`pyglet.window.mouse`
  * modifiers - modifier key from :py:mod:`arcade.key`

:py:const:`arcade.gui.events.MOUSE_SCROLL`
  * x - coordinate of the event
  * y - coordinate of the event
  * scroll_x - 0 for most mice beside Apple Magic mouse
  * scroll_y - number of “clicks” the wheel moved

:py:const:`arcade.gui.events.MOUSE_MOTION`
  * x - coordinate of the event
  * y - coordinate of the event
  * dx - distance the mouse travelled along x axis
  * dy - distance the mouse travelled along y axis

:py:const:`arcade.gui.events.MOUSE_DRAG`
  * x - coordinate of the event
  * y - coordinate of the event
  * dx - distance the mouse travelled along x axis
  * dy - distance the mouse travelled along y axis
  * button - pressed mouse button from :py:mod:`pyglet.window.mouse`
  * modifiers - modifier key from :py:mod:`arcade.key`

:py:const:`arcade.gui.events.KEY_PRESS`
  * symbol - pressed key symbol from :py:mod:`arcade.key`
  * modifiers - modifier key from :py:mod:`arcade.key`

:py:const:`arcade.gui.events.KEY_RELEASE`
  * symbol - pressed key symbol from :py:mod:`arcade.key`
  * modifiers - modifier key from :py:mod:`arcade.key`

:py:const:`arcade.gui.events.RESIZE`
  * width - new width of the window
  * height - new height of the window

:py:const:`arcade.gui.events.TEXT_INPUT`
  * text - typed text

:py:const:`arcade.gui.events.TEXT_TEXT_MOTION`
  * motion - motion from :py:mod:`arcade.key`

:py:const:`arcade.gui.events.TEXT_MOTION_SELECTION`
  * selection - motion from :py:mod:`arcade.key`
"""

from typing import Any

MOUSE_PRESS = "MOUSE_PRESS"
MOUSE_RELEASE = "MOUSE_RELEASE"
MOUSE_SCROLL = "MOUSE_SCROLL"
MOUSE_MOTION = "MOUSE_MOTION"
MOUSE_DRAG = "MOUSE_DRAG"
KEY_PRESS = "KEY_PRESS"
KEY_RELEASE = "KEY_RELEASE"
RESIZE = "RESIZE"
TEXT_INPUT = "TEXT_INPUT"
TEXT_MOTION = "TEXT_MOTION"
TEXT_MOTION_SELECTION = "TEXT_MOTION_SELECTION"


class UIEvent:
    """
    Represents an interaction with the gui.
    """

    def __init__(self, type: str, **kwargs):
        """
        :param type: Type of the event, like :py:attr:`arcade.gui.events.MOUSE_PRESS` :py:attr:`arcade.gui.events.KEY_PRESS`
        :param kwargs: Data of the event
        """
        self.type = type
        self.data = kwargs

    def get(self, key: str) -> Any:
        """
        Retrieve value for given key
        """
        return self.data.get(key)

    def __repr__(self):
        return " ".join(
            [f"{self.type} ", *[f"{key}={value}" for key, value in self.data.items()]]
        )
