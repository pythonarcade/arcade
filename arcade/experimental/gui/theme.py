from typing import Union, Tuple
from dataclasses import dataclass
from arcade_types import Color

@dataclass
class Theme:
    text_color: Color = None

    font_size: float = 12
    font_name: Union[str, Tuple[str, ...]] = ('calibri', 'arial')

    background_color: Color = None
    border_color: Color = None

    text_color_mouse_over: Color = None
    border_color_mouse_over: Color = None
    background_color_mouse_over: Color = None

    background_color_mouse_press: Color = None
    text_color_mouse_press: Color = None
    border_color_mouse_press: Color = None