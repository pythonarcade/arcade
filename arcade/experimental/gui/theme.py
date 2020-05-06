""" Theme information for GUI elements. """
from typing import Union, Tuple
from dataclasses import dataclass
from arcade import Color

@dataclass
class Theme:
    """ Theme information for GUI elements. """
    text_color: Color

    font_size: float
    font_name: Union[str, Tuple[str, ...]]

    background_color: Color
    border_color: Color
    border_width: int

    text_color_mouse_over: Color
    border_color_mouse_over: Color
    background_color_mouse_over: Color

    background_color_mouse_press: Color
    text_color_mouse_press: Color
    border_color_mouse_press: Color
