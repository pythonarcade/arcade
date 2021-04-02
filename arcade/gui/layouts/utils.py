from typing import Union

from arcade import Sprite
from arcade.gui import UIElement
from arcade.gui.layouts import UILayout


def valid(element: Union[Sprite, UIElement, "UILayout"]):
    """
    Checks if :class:`UILayout` has a valid size and all children are within the bounds of the given layout.
    """
    left = element.left
    right = element.right
    top = element.top
    bottom = element.bottom

    if not (left <= right):
        return False
    if not (bottom <= top):
        return False

    if isinstance(element, UILayout):
        for element in element:
            if not (left <= element.left <= right):
                return False
            if not (left <= element.right <= right):
                return False
            if not (bottom <= element.top <= top):
                return False
            if not (bottom <= element.bottom <= top):
                return False

            if not valid(element):
                return False

    return True
