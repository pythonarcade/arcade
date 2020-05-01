"""
Flat text button GUI element.
"""

from typing import Union, Tuple

import arcade
from arcade.arcade_types import Color
from .button_abstract import ButtonAbstract

class ClickableText(ButtonAbstract):
    def __init__(self, text, center_x, center_y,
                 text_color: Color,
                 text_color_mouse_over: Color = None,
                 text_color_mouse_press: Color = None,
                 font_size: float = 12,
                 font_name: Union[str, Tuple[str, ...]] = ('calibri', 'arial'),
                 ):
        super().__init__(center_x, center_y)

        if text_color_mouse_over is None:
            text_color_mouse_over = text_color

        if text_color_mouse_press is None:
            text_color_mouse_press = text_color

        text_image_normal = arcade.get_text_image(text=text, text_color=text_color, font_size=font_size, font_name=font_name)
        text_image_mouse_over = arcade.get_text_image(text=text, text_color=text_color_mouse_over, font_size=font_size, font_name=font_name)
        text_image_mouse_press = arcade.get_text_image(text=text, text_color=text_color_mouse_press, font_size=font_size, font_name=font_name)

        self.texture = arcade.Texture(image=text_image_normal, name=text)
        self.normal_texture = self.texture
        self.mouse_press_texture = arcade.Texture(image=text_image_mouse_press, name=text+"3")
        self.mouse_over_texture = arcade.Texture(image=text_image_mouse_over, name=text+"6")
