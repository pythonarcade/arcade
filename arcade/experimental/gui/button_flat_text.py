"""
Flat text button GUI element.
"""

from PIL import ImageDraw
from typing import Union, Tuple

import arcade
from arcade import Color
from .button_abstract import ButtonAbstract

class FlatTextButton(ButtonAbstract):
    def __init__(self,
                 text,
                 center_x,
                 center_y,
                 width,
                 height,

                 text_color: Color,

                 font_size: float = 12,
                 font_name: Union[str, Tuple[str, ...]] = ('calibri', 'arial'),

                 background_color: Color = None,
                 border_color: Color = None,

                 text_color_mouse_over: Color = None,
                 border_color_mouse_over: Color = None,
                 background_color_mouse_over: Color = None,

                 background_color_mouse_press: Color = None,
                 text_color_mouse_press: Color = None,
                 border_color_mouse_press: Color = None
                 ):
        super().__init__(center_x, center_y)

        if text_color_mouse_over is None:
            text_color_mouse_over = text_color

        if text_color_mouse_press is None:
            text_color_mouse_press = text_color

        if background_color and not background_color_mouse_over:
            background_color_mouse_over = background_color

        if background_color and not background_color_mouse_press:
            background_color_mouse_press = background_color


        text_image_normal = arcade.get_text_image(text,
                                                  text_color,
                                                  width=width,
                                                  height=height,
                                                  align="center",
                                                  valign="middle",
                                                  background_color=background_color,
                                                  font_size=font_size,
                                                  font_name=font_name)
        text_image_mouse_over = arcade.get_text_image(text,
                                                      text_color_mouse_over,
                                                      width=width,
                                                      height=height,
                                                      align="center",
                                                      valign="middle",
                                                      background_color=background_color_mouse_over,
                                                      font_size=font_size,
                                                      font_name=font_name)
        text_image_mouse_press = arcade.get_text_image(text,
                                                       text_color_mouse_press,
                                                       width=width,
                                                       height=height,
                                                       align="center",
                                                       valign="middle",
                                                       background_color=background_color_mouse_press,
                                                       font_size=font_size,
                                                       font_name=font_name)

        rect = [0, 0, text_image_normal.width - 1, text_image_normal.height - 1]

        if border_color:
            d = ImageDraw.Draw(text_image_normal)
            d.rectangle(rect, fill=None, outline=border_color, width=1)

        if border_color_mouse_over:
            d = ImageDraw.Draw(text_image_mouse_over)
            d.rectangle(rect, fill=None, outline=border_color_mouse_over, width=1)

        if border_color_mouse_press:
            d = ImageDraw.Draw(text_image_mouse_press)
            d.rectangle(rect, fill=None, outline=border_color_mouse_press, width=1)

        self.texture = arcade.Texture(image=text_image_normal, name=text)
        self.normal_texture = self.texture
        self.mouse_press_texture = arcade.Texture(image=text_image_mouse_press, name=text+"4")
        self.mouse_over_texture = arcade.Texture(image=text_image_mouse_over, name=text+"5")
