from typing import Union

from arcade import Sprite
from arcade.gui import UIElement
from arcade.gui.layouts import UIAbstractLayout


# TODO test this method
def valid(element: Union[Sprite, UIElement, 'UIAbstractLayout']):
    left = element.left
    right = element.right
    top = element.top
    bottom = element.bottom

    if not (left <= right):
        return False
    if not (bottom <= top):
        return False

    if isinstance(element, UIAbstractLayout):
        for element, data in element:
            if not (left <= element.left <= right):
                return False
            if not (left <= element.right <= right):
                return False
            if not (bottom <= element.top <= top):
                return False
            if not (bottom <= element.bottom <= top):
                return False

            if not element.valid():
                return False

    return True
