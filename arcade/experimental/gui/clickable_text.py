"""
Flat text button GUI element.
"""

import arcade
from arcade.experimental.gui.ui_element import UIElement

class ClickableText(UIElement):
    def __init__(self, text, center_x, center_y):
        super().__init__(center_x, center_y)

        text_image_normal = arcade.get_text_image(text, arcade.color.BLACK)
        text_image_mouse_over = arcade.get_text_image(text, arcade.color.WHITE)
        text_image_mouse_press = arcade.get_text_image(text, arcade.color.RED)

        self.texture = arcade.Texture(image=text_image_normal, name=text)
        self.normal_texture = self.texture
        self.mouse_press_texture = arcade.Texture(image=text_image_mouse_press, name=text+"3")
        self.mouse_over_texture = arcade.Texture(image=text_image_mouse_over, name=text+"6")
