import PIL.Image

import arcade
from arcade.experimental.gui.ui_element import UIElement

class FlatButton(UIElement):
    def __init__(self, center_x, center_y, width, height):
        super().__init__(center_x, center_y, width, height, )


        color = (127, 127, 127)
        image = PIL.Image.new('RGBA', (width, height), color)
        self.texture = arcade.Texture(f"Solid-{color[0]}-{color[1]}-{color[2]}", image)
        self._points = self.texture.hit_box_points

        self.normal_texture = self.texture

        color = (80, 80, 80)
        image = PIL.Image.new('RGBA', (width, height), color)
        self.mouse_over_texture = arcade.Texture(f"Solid-{color[0]}-{color[1]}-{color[2]}", image)

        color = (127, 0, 0)
        image = PIL.Image.new('RGBA', (width, height), color)
        self.mouse_press_texture = arcade.Texture(f"Solid-{color[0]}-{color[1]}-{color[2]}", image)


