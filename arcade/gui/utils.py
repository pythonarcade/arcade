import os
from pathlib import Path
from typing import Union, Any, TYPE_CHECKING, Tuple, Optional
from warnings import warn

from PIL.ImageColor import getrgb

from arcade import Sprite, get_viewport

if TYPE_CHECKING:
    from arcade.gui.elements import UIElement
    from arcade.gui.layouts import UILayout


def center_on_viewport(element: Union[Sprite, "UIElement", "UILayout"]):
    """
    Centers a sprite, GUI Element, or layout of elements on the current viewport.

    :param element: Item to center

    """
    left, right, bottom, top = get_viewport()
    element.center_x = left + (right - left) / 2
    element.center_y = bottom + (top - bottom) / 2


def parse_rgb_value(value: Any) -> Optional[Tuple]:
    """
    Parses the input string returning rgb int-tuple.

    Supported formats:

    * RGB ('r,g,b', 'r, g, b')
    * HEX ('00ff00')
    * Arcade colors ('BLUE', 'DARK_BLUE')

    :param value: Color to parse

    """
    import arcade

    if value in (None, "", "None"):
        return None

    if type(value) in (int, float, list):
        return value

    # if a string, then try parsing
    if isinstance(value, str):

        # arcade color
        if isinstance(value, str) and hasattr(arcade.color, value.upper()):
            return getattr(arcade.color, value)

        # hex
        if len(value) in (3, 6) and "," not in value:
            try:
                return getrgb(f"#{value}")
            except ValueError:
                pass

        # rgb
        try:
            return getrgb(f"rgb({value})")
        except ValueError:
            pass

    warn(f"Could not parse style value: {value}")
    return None
