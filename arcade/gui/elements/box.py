from typing import Optional, Tuple

import PIL

import arcade
from arcade.gui.elements import UIElement
from arcade.gui.style import UIStyle
from arcade.gui.exceptions import UIException


class UIColorBox(UIElement):
    """
    Simple UIElement, showing a solid color box.
    """

    def __init__(
        self,
        color: Optional[arcade.Color],
        min_size: Optional[Tuple],
        center_x=0,
        center_y=0,
        size_hint: Optional[Tuple] = None,
        id: Optional[str] = None,
        style: UIStyle = None,
        **kwargs,
    ):
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            min_size=min_size,
            size_hint=size_hint,
            id=id,
            style=style,
            **kwargs,
        )

        if min_size is not None and color is not None:
            width, height = min_size
            image = PIL.Image.new("RGBA", (width, height), color)
            self.texture = arcade.Texture(
                f"Solid-{color[0]}-{color[1]}-{color[2]}",
                image,
                hit_box_algorithm="None",
            )
        else:
            raise UIException("UIBox requires color and min_size")

    def render(self):
        pass


class UITextureBox(UIElement):
    """
    Simple UIElement, showing a texture. Size of the texture is used.
    """

    def __init__(
        self,
        texture: Optional[arcade.Texture],
        center_x=0,
        center_y=0,
        min_size: Optional[Tuple] = None,
        size_hint: Optional[Tuple] = None,
        id: Optional[str] = None,
        style: UIStyle = None,
        **kwargs,
    ):
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            min_size=min_size,
            size_hint=size_hint,
            id=id,
            style=style,
            **kwargs,
        )
        if texture:
            self.texture = texture
        else:
            raise UIException("UIBox texture to be set")

    def render(self):
        pass
