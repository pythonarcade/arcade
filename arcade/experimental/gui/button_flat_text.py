"""
Flat text button GUI element.
"""

from PIL import ImageDraw

import arcade
from .button_abstract import ButtonAbstract
from .theme import Theme

class FlatTextButton(ButtonAbstract):
    """ Flat button with text """
    def __init__(self,
                 text,
                 center_x,
                 center_y,
                 width,
                 height,
                 theme: Theme
                 ):
        super().__init__(center_x, center_y)

        assert theme.text_color is not None
        assert theme.background_color is not None
        assert theme.text_color_mouse_over is not None
        assert theme.background_color_mouse_over is not None

        text_image_normal = arcade.get_text_image(text,
                                                  theme.text_color,
                                                  width=width,
                                                  height=height,
                                                  align="center",
                                                  valign="middle",
                                                  background_color=theme.background_color,
                                                  font_size=theme.font_size,
                                                  font_name=theme.font_name)
        text_image_mouse_over = arcade.get_text_image(text,
                                                      theme.text_color_mouse_over,
                                                      width=width,
                                                      height=height,
                                                      align="center",
                                                      valign="middle",
                                                      background_color=theme.background_color_mouse_over,
                                                      font_size=theme.font_size,
                                                      font_name=theme.font_name)
        text_image_mouse_press = arcade.get_text_image(text,
                                                       text_color=theme.text_color_mouse_press,
                                                       width=width,
                                                       height=height,
                                                       align="center",
                                                       valign="middle",
                                                       background_color=theme.background_color_mouse_press,
                                                       font_size=theme.font_size,
                                                       font_name=theme.font_name)

        rect = [0, 0, text_image_normal.width - theme.border_width / 2, text_image_normal.height - theme.border_width / 2]

        if theme.border_color and theme.border_width:
            d = ImageDraw.Draw(text_image_normal)
            d.rectangle(rect, fill=None, outline=theme.border_color, width=theme.border_width)

        if theme.border_color_mouse_over:
            d = ImageDraw.Draw(text_image_mouse_over)
            d.rectangle(rect, fill=None, outline=theme.border_color_mouse_over, width=theme.border_width)

        if theme.border_color_mouse_press:
            d = ImageDraw.Draw(text_image_mouse_press)
            d.rectangle(rect, fill=None, outline=theme.border_color_mouse_press, width=theme.border_width)

        self.texture = arcade.Texture(image=text_image_normal, name=text)
        self.normal_texture = self.texture
        self.mouse_press_texture = arcade.Texture(image=text_image_mouse_press, name=text+"4")
        self.mouse_over_texture = arcade.Texture(image=text_image_mouse_over, name=text+"5")
