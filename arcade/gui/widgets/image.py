import math

from typing_extensions import override

from arcade import Texture
from arcade.gui import NinePatchTexture
from arcade.gui.property import Property, bind
from arcade.gui.surface import Surface
from arcade.gui.widgets import UIWidget


class UIImage(UIWidget):
    """UIWidget showing a texture.

    If no size given, the texture size is used.

    The UIImage supports rotation and alpha values, which only apply to the texture.
    Border, and background color are not affected by this.
    The size of the image is reduced when rotated to stay within bounce of the widget.

    Args:
        texture: Texture to show
        width: width of widget
        height: height of widget
        angle: angle of the texture in degrees
        alpha: alpha value of the texture, value between 0 and 255
        **kwargs: passed to UIWidget
    """

    texture = Property[Texture | NinePatchTexture]()
    """Texture to show"""
    alpha = Property(255)
    """Alpha value of the texture, value between 0 and 255.
    0 is fully transparent, 255 is fully visible."""
    angle = Property(0)
    """Angle of the texture in degrees.
    The image will be rotated around its center and fitted into the widget size."""

    def __init__(
        self,
        *,
        texture: Texture | NinePatchTexture,
        width: float | None = None,
        height: float | None = None,
        angle: int = 0,
        alpha: int = 255,
        **kwargs,
    ):
        self.texture = texture
        self.angle = angle
        self.alpha = alpha

        super().__init__(
            width=width if width else texture.width,
            height=height if height else texture.height,
            **kwargs,
        )
        bind(self, "texture", UIImage.trigger_render)
        bind(self, "alpha", UIImage.trigger_full_render)
        bind(self, "angle", UIImage.trigger_full_render)

    @override
    def do_render(self, surface: Surface):
        """Render the stored texture in the size of the widget."""
        if self.texture:
            self.prepare_render(surface)

            if self.angle == 0:
                surface.draw_texture(
                    x=0,
                    y=0,
                    width=self.content_width,
                    height=self.content_height,
                    tex=self.texture,
                    alpha=self.alpha,
                )
            else:
                w = self.content_width
                h = self.content_height
                angle_radians = math.radians(self.angle)
                cos_value = abs(math.cos(angle_radians))
                sin_value = abs(math.sin(angle_radians))

                # https://stackoverflow.com/a/33867165/2947505
                # Calculate the minimum size of the rotated image
                # W = w·|cos φ| + h·|sin φ|
                w_rotated = w * cos_value + h * sin_value
                # H = w·|sin φ| + h·|cos φ|
                h_rotated = w * sin_value + h * cos_value
                # a = min(wo / W, ho / H)
                factor = min(w / w_rotated, h / h_rotated)
                # W′ = a·w
                w_fitted = factor * w
                # H′ = a·h
                h_fitted = factor * h

                draw_rect = self.content_rect.align_left(0).align_bottom(0)
                draw_rect = draw_rect.resize(w_fitted, h_fitted)
                surface.draw_texture(
                    x=draw_rect.left,
                    y=draw_rect.bottom,
                    width=draw_rect.width,
                    height=draw_rect.height,
                    tex=self.texture,
                    alpha=self.alpha,
                    angle=self.angle,
                )
