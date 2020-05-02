""" Flat button """
import PIL.Image
from PIL import ImageDraw

import arcade
from .button_abstract import ButtonAbstract
from .theme import Theme

class FlatButton(ButtonAbstract):
    """ Create a flat button with no graphic or text. """
    def __init__(self, center_x, center_y, width, height, theme: Theme):
        super().__init__(center_x, center_y)

        rect = [0, 0, width - theme.border_width / 2, height - theme.border_width / 2]

        color = theme.background_color
        image = PIL.Image.new('RGBA', (width, height), color)
        if theme.border_color and theme.border_width:
            d = ImageDraw.Draw(image)
            d.rectangle(rect, fill=None, outline=theme.border_color, width=theme.border_width)
        self.texture = arcade.Texture(f"Solid-{width},{height}-{color[0]}-{color[1]}-{color[2]}-normal", image)
        self._points = self.texture.hit_box_points

        self.normal_texture = self.texture

        color = theme.background_color_mouse_over
        image = PIL.Image.new('RGBA', (width, height), color)
        if theme.border_color_mouse_over:
            d = ImageDraw.Draw(image)
            d.rectangle(rect, fill=None, outline=theme.border_color_mouse_over, width=theme.border_width)
        self.mouse_over_texture = arcade.Texture(f"Solid-{width},{height}-{color[0]}-{color[1]}-{color[2]}-mouseover", image)

        color = theme.background_color_mouse_press
        image = PIL.Image.new('RGBA', (width, height), color)
        if theme.border_color_mouse_press:
            d = ImageDraw.Draw(image)
            d.rectangle(rect, fill=None, outline=theme.border_color_mouse_press, width=theme.border_width)
        self.mouse_press_texture = arcade.Texture(f"Solid-{width},{height}-{color[0]}-{color[1]}-{color[2]}-mouse-click", image)
