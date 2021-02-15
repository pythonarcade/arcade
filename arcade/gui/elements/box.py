from typing import Optional, Tuple

import PIL

import arcade
from arcade.gui import UIElement, UIException


class UIBox(UIElement):
    """
    Simple UIElement, showing either a given texture or a solid color.
    """

    def __init__(self,
                 width: int = None,
                 height: int = None,
                 color: Optional[arcade.Color] = None,
                 center_x=0,
                 center_y=0,
                 texture: Optional[arcade.Texture] = None,
                 min_size: Optional[Tuple] = None,
                 size_hint: Optional[Tuple] = None,
                 **kwargs):
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            min_size=min_size,
            size_hint=size_hint,
            **kwargs
        )

        if None not in (width, height) and color is not None:
            image = PIL.Image.new('RGBA', (width, height), color)
            self.texture = arcade.Texture(f"Solid-{color[0]}-{color[1]}-{color[2]}", image, hit_box_algorithm='None')
        elif texture:
            self.texture = texture
        else:
            raise UIException('UIBox requires either (color, width, height) or texture to be set')

    def render(self):
        pass
