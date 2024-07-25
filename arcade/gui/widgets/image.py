from __future__ import annotations

from typing import Union

from typing_extensions import override

from arcade import Texture
from arcade.gui import NinePatchTexture
from arcade.gui.property import Property, bind
from arcade.gui.surface import Surface
from arcade.gui.widgets import UIWidget


class UIImage(UIWidget):
    """UIWidget showing a texture.

    If no size given, the texture size is used.

    Args:
        texture: Texture to show
        width: width of widget
        height: height of widget
        **kwargs: passed to UIWidget
    """

    texture: Union[Texture, NinePatchTexture] = Property()  # type: ignore

    def __init__(
        self,
        *,
        texture: Union[Texture, NinePatchTexture],
        width: float = None,
        height: float = None,
        **kwargs,
    ):
        self.texture = texture

        super().__init__(
            width=width if width else texture.width,
            height=height if height else texture.height,
            **kwargs,
        )
        bind(self, "texture", self.trigger_render)

    @override
    def do_render(self, surface: Surface):
        """Render the stored texture in the size of the widget."""
        self.prepare_render(surface)
        if self.texture:
            surface.draw_texture(
                x=0,
                y=0,
                width=self.content_width,
                height=self.content_height,
                tex=self.texture,
            )
