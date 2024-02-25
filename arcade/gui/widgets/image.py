from __future__ import annotations

from typing import Union

from arcade import Texture
from arcade.gui import NinePatchTexture
from arcade.gui.property import Property, bind
from arcade.gui.surface import Surface
from arcade.gui.widgets import UIWidget


class UIImage(UIWidget):
    """
    UIWidget showing a texture.
    """

    texture: Union[Texture, NinePatchTexture] = Property()  # type: ignore

    def __init__(
        self,
        *,
        texture: Union[Texture, NinePatchTexture],
        **kwargs,
    ):
        self.texture = texture

        super().__init__(**kwargs)
        bind(self, "texture", self.trigger_render)

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        if self.texture:
            surface.draw_texture(
                x=0,
                y=0,
                width=self.content_width,
                height=self.content_height,
                tex=self.texture,
            )
