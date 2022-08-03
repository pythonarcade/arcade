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

    def get(self, key):
        return self[key] if key in self else None

    def __contains__(self, item):
        return hasattr(self, item)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


@dataclass
class UISliderStyle(_UIStyleDict):
    bg: Color
    border: Color
    border_width: int
    filled_bar: Color
    unfilled_bar: Color


UISliderDefaultStyle = {
    "normal": UISliderStyle(
        bg=(94, 104, 117),
        border=(77, 81, 87),
        border_width=1,
        filled_bar=(50, 50, 50),
        unfilled_bar=(116, 125, 123),
    ),
    "hover": UISliderStyle(
        bg=(96, 103, 112),
        border=(77, 81, 87),
        border_width=2,
        filled_bar=(50, 50, 50),
        unfilled_bar=(116, 125, 123),
    ),
    "press": UISliderStyle(
        bg=(96, 103, 112),
        border=(77, 81, 87),
        border_width=3,
        filled_bar=(50, 50, 50),
        unfilled_bar=(116, 125, 123),
    ),
    # TODO style for disabled
    "disabled": UISliderStyle(
        bg=(94, 104, 117),
        border=(77, 81, 87),
        border_width=1,
        filled_bar=(50, 50, 50),
        unfilled_bar=(116, 125, 123),
    )
}


@dataclass
class UIFlatButtonStyle(_UIStyleDict):
    font_size: int
    font_name: FontNameOrNames
    font_color: Color
    bg: Color
    border: Optional[Color]
    border_width: int


UIFlatButtonStyle_default = {
    "normal": UIFlatButtonStyle(
        font_size=12,
        font_name=("calibri", "arial"),
        font_color=arcade.color.WHITE,
        bg=(21, 19, 21),
        border=None,
        border_width=0,
    ),
    "hover": UIFlatButtonStyle(
        font_size=12,
        font_name=("calibri", "arial"),
        font_color=arcade.color.WHITE,
        bg=(21, 19, 21),
        border=(77, 81, 87),
        border_width=2,
    ),
    "press": UIFlatButtonStyle(
        font_size=12,
        font_name=("calibri", "arial"),
        font_color=arcade.color.BLACK,
        bg=arcade.color.WHITE,
        border=arcade.color.WHITE,
        border_width=2,
    ),
    "disabled": UIFlatButtonStyle(
        font_size=12,
        font_name=("calibri", "arial"),
        font_color=arcade.color.WHITE,
        bg=arcade.color.GRAY,
        border=None,
        border_width=2,
    )
}
