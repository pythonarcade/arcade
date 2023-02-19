import PIL

from .base import Sprite
import arcade
from arcade.types import Color
from arcade import cache
from arcade import hitbox
from arcade.texture import (
    make_circle_texture,
    make_soft_circle_texture,
    Texture,
    ImageData,
)


class SpriteSolidColor(Sprite):
    """
    A rectangular sprite of the given ``width``, ``height``, and ``color``.

    The texture is automatically generated instead of loaded from a
    file. Internally only a single global texture is used for this
    sprite type, so concerns about memory usage non-existent regardless
    of size or number of sprite variations.

    :param int width: Width of the sprite in pixels
    :param int height: Height of the sprite in pixels
    :param float center_x: Initial x position of the sprite
    :param float center_y: Initial y position of the sprite
    :param Color color: The color of the sprite as an RGB or RGBA tuple
    :param float angle: Initial angle of the sprite in degrees
    """
    _default_image = ImageData(
        PIL.Image.new("RGBA", size=(32, 32), color=(255, 255, 255, 255)),
        hash="sprite_solid_color"
    )

    def __init__(
        self,
        width: int,
        height: int,
        center_x: float = 0,
        center_y: float = 0,
        color: Color = (255, 255, 255, 255),
        angle: float = 0,
    ):
        """
        Create a solid-color rectangular sprite.
        """
        texture = Texture(
            self._default_image,
            hit_box_points = (
                (-width / 2, -height / 2),
                (width / 2, -height / 2),
                (width / 2, height / 2),
                (-width / 2, height / 2)
            )
        )
        texture.size = width, height
        super().__init__(
            texture,
            center_x=center_x,
            center_y=center_y,
            angle=angle,
        )
        self.color = arcade.get_four_byte_color(color)


class SpriteCircle(Sprite):
    """
    A circle of the specified `radius <https://simple.wikipedia.org/wiki/Radius>`_.

    The texture is automatically generated instead of loaded from a
    file.

    There may be a stutter the first time a combination of ``radius``,
    ``color``, and ``soft`` is used due to texture generation. All
    subsequent calls for the same combination will run faster because
    they will re-use the texture generated earlier.

    For a gradient fill instead of a solid color, set ``soft`` to
    ``True``. The circle will fade from an opaque center to transparent
    at the edges.

    :param int radius: Radius of the circle in pixels
    :param Color color: The Color of the sprite as an RGB or RGBA tuple
    :param bool soft: If ``True``, the circle will fade from an opaque
                      center to transparent edges.
    """
    def __init__(self, radius: int, color: Color, soft: bool = False):
        radius = int(radius)
        diameter = radius * 2
        color_rgba = arcade.get_four_byte_color(color)

        # We are only creating white textures. The actual color is
        # is applied in the shader through the sprite's color attribute.
        # determine the texture's cache name.
        if soft:
            cache_name = cache.crate_str_from_values("circle_texture_soft", diameter, 255, 255, 255, 255)
        else:
            cache_name = cache.crate_str_from_values("circle_texture", diameter, 255, 255, 255, 255)

        # Get existing texture from cache if possible
        texture = cache.texture_cache.get_with_config(cache_name, hitbox.algo_simple)
        if not texture:
            if soft:
                texture = make_soft_circle_texture(
                    diameter,
                    color=(255, 255, 255, 255),
                    name=cache_name,
                    hit_box_algorithm=hitbox.algo_simple,
                )
            else:
                texture = make_circle_texture(
                    diameter,
                    color=(255, 255, 255, 255),
                    name=cache_name,
                )
            cache.texture_cache.put(texture)

        # apply results to the new sprite
        super().__init__(texture)
        self.color = color_rgba
        self._points = self.texture.hit_box_points
