from __future__ import annotations

from weakref import WeakValueDictionary

import PIL
import PIL.Image

import arcade
import arcade.cache
from arcade.texture import (
    ImageData,
    Texture,
    make_circle_texture,
    make_soft_circle_texture,
)
from arcade.types import RGBA255, Color
from arcade.types.rect import Rect

from .sprite import Sprite


class SpriteSolidColor(Sprite):
    """
    A rectangular sprite of the given ``width``, ``height``, and ``color``.

    The texture is automatically generated instead of loaded from a
    file. Internally only a single global image is used for this
    sprite type so concerns about memory usage non-existent regardless
    of size or number of sprite variations.

    Different texture configurations (width, height) are weakly cached internally
    to avoid creating multiple textures with the same configuration.

    Args:
        width:
            Width of the sprite in pixels
        height:
            Height of the sprite in pixels
        center_x:
            Initial x position of the sprite
        center_y:
            Initial y position of the sprite
        color:
            The color of the sprite as a :py:class:`~arcade.types.Color`,
            an RGBA tuple, or an RGB tuple.
        angle:
            Initial angle of the sprite in degrees
    """

    __slots__ = ()
    _default_image: ImageData | None = None
    # To avoid making lots of texture instances with the same configuration
    # we cache them here weakly. Making a 100 x 100 grid of white sprites
    # only create 1 texture instead of 1000. This saves memory and processing
    # time for the default texture atlas.
    _texture_cache: WeakValueDictionary[tuple[int, int], Texture] = WeakValueDictionary()

    def __init__(
        self,
        width: int,
        height: int,
        center_x: float = 0,
        center_y: float = 0,
        color: RGBA255 = Color(255, 255, 255, 255),
        angle: float = 0,
        **kwargs,
    ):
        texture = self.__class__._texture_cache.get((width, height))
        if texture is None:
            texture = Texture(
                self._get_default_image(),
                hit_box_points=(
                    (-width / 2, -height / 2),
                    (width / 2, -height / 2),
                    (width / 2, height / 2),
                    (-width / 2, height / 2),
                ),
            )
            texture.size = width, height
            self.__class__._texture_cache[(width, height)] = texture

        super().__init__(
            texture,
            center_x=center_x,
            center_y=center_y,
            angle=angle,
        )
        self.color = Color.from_iterable(color)

    @classmethod
    def from_rect(cls, rect: Rect, color: Color, angle: float = 0.0) -> SpriteSolidColor:
        """
        Construct a new SpriteSolidColor from a :py:class:`~arcade.types.rect.Rect`.

        Args:
            rect:
                The rectangle to use for the sprite's dimensions and position.
            color:
                The color of the sprite as a :py:class:`~arcade.types.Color`,
                an RGBA tuple, or an RGB tuple.
            angle:
                The angle of the sprite in degrees.
        """
        return cls(int(rect.width), int(rect.height), rect.x, rect.y, color, angle)

    def _get_default_image(self) -> ImageData:
        """Lazy-load the default image for this sprite type."""
        im = self.__class__._default_image
        if im is None:
            im = ImageData(
                PIL.Image.new("RGBA", size=(32, 32), color=(255, 255, 255, 255)),
                hash="sprite_solid_color",
            )
            self.__class__._default_image = im
        return im


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

    Args:
        radius:
            Radius of the circle in pixels
        color:
            The Color of the sprite as an RGB or RGBA tuple
        soft:
            If ``True``, the circle will fade from an opaque
            center to transparent edges.
    """

    # Local weak cache for textures to avoid creating multiple instances with the same configuration
    _texture_cache: WeakValueDictionary[tuple[int, RGBA255, bool], Texture] = WeakValueDictionary()

    def __init__(self, radius: int, color: RGBA255, soft: bool = False, **kwargs):
        radius = int(radius)
        diameter = radius * 2

        cache_key = diameter, color, soft
        # Get existing texture from cache if possible
        texture = self.__class__._texture_cache.get(cache_key)

        if not texture:
            if soft:
                texture = make_soft_circle_texture(
                    diameter,
                    color=(255, 255, 255, 255),
                    hit_box_algorithm=arcade.hitbox.algo_simple,
                )
            else:
                texture = make_circle_texture(
                    diameter,
                    color=(255, 255, 255, 255),
                )

            self.__class__._texture_cache[cache_key] = texture

        # apply results to the new sprite
        super().__init__(texture)
        self.color = Color.from_iterable(color)
