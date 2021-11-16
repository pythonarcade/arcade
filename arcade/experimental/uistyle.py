from dataclasses import dataclass
from typing import Optional

import arcade
from arcade import Color
from arcade.text_pyglet import FontNameOrNames


class _UIStyleDict:
    """
    Support dict like access syntax.
    Can be subclassed by dataclass to be usable as style dict.
    """

    def __contains__(self, item):
        return hasattr(self, item)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


@dataclass
class UISliderStyle(_UIStyleDict):
    normal_bg: Color = (94, 104, 117)
    normal_border: Color = (77, 81, 87)
    normal_border_width: int = 1
    normal_filled_bar: Color = (50, 50, 50)
    normal_unfilled_bar: Color = (116, 125, 123)

    # hovered
    hovered_bg: Color = (96, 103, 112)
    hovered_border: Color = (77, 81, 87)
    hovered_border_width: int = 2
    hovered_filled_bar: Color = (50, 50, 50)
    hovered_unfilled_bar: Color = (116, 125, 123)

    # pressed
    pressed_bg: Color = (96, 103, 112)
    pressed_border: Color = (77, 81, 87)
    pressed_border_width: int = 3
    pressed_filled_bar: Color = (50, 50, 50)
    pressed_unfilled_bar: Color = (116, 125, 123)


@dataclass
class UIFlatButtonStyle(_UIStyleDict):
    normal_font_size: int = 12
    normal_font_name: FontNameOrNames = ("calibri", "arial")
    normal_font_color: Color = arcade.color.WHITE
    normal_bg: Color = (21, 19, 21)
    normal_border: Optional[Color] = None
    normal_border_width: int = 0

    hovered_font_size: int = 12
    hovered_font_name: FontNameOrNames = ("calibri", "arial")
    hovered_font_color: Color = arcade.color.WHITE
    hovered_bg: Color = (21, 19, 21)
    hovered_border: Optional[Color] = (77, 81, 87)
    hovered_border_width: int = 2

    pressed_font_size: int = 12
    pressed_font_name: FontNameOrNames = ("calibri", "arial")
    pressed_font_color: Color = arcade.color.BLACK
    pressed_bg: Color = arcade.color.WHITE
    pressed_border: Optional[Color] = arcade.color.WHITE
    pressed_border_width: int = 2
