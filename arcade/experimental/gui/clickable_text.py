"""
Flat text button GUI element.
"""

import arcade
from arcade import Color
from arcade.experimental.gui.ui_element import UIElement

class ClickableText(UIElement):
    def __init__(self, text, center_x, center_y,
                 text_color: Color,
                 text_color_mouse_over: Color = None,
                 text_color_mouse_press: Color = None,
                 font_size=None,
                 font=None,
                 ):
        super().__init__(center_x, center_y)

        text_image_normal = arcade.get_text_image(text, text_color, font_size, font)
        text_image_mouse_over = arcade.get_text_image(text, text_color_mouse_over, font_size, font)
        text_image_mouse_press = arcade.get_text_image(text, text_color_mouse_press, font_size, font)

        self.texture = arcade.Texture(image=text_image_normal, name=text)
        self.normal_texture = self.texture
        self.mouse_press_texture = arcade.Texture(image=text_image_mouse_press, name=text+"3")
        self.mouse_over_texture = arcade.Texture(image=text_image_mouse_over, name=text+"6")
