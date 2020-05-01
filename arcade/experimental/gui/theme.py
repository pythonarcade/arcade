from typing import Union, Tuple, Optional
from dataclasses import dataclass
from arcade import Color

@dataclass
class Theme:
    text_color: Optional[Color] = None

    font_size: float = 12
    font_name: Union[str, Tuple[str, ...]] = ('calibri', 'arial')

    background_color: Optional[Color] = None
    border_color: Optional[Color] = None

    text_color_mouse_over: Optional[Color] = None
    border_color_mouse_over: Optional[Color] = None
    background_color_mouse_over: Optional[Color] = None

    background_color_mouse_press: Optional[Color] = None
    text_color_mouse_press: Optional[Color] = None
    border_color_mouse_press: Optional[Color] = None