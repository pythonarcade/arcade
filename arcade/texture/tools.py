from PIL import Image, ImageDraw

import arcade
import arcade.cache
from arcade.types import Size2D

from .texture import ImageData, Texture

_DEFAULT_TEXTURE = None
_DEFAULT_IMAGE_SIZE = (128, 128)


def get_default_texture(size: Size2D[int] = _DEFAULT_IMAGE_SIZE) -> Texture:
    """
    Creates and returns a default texture and caches it internally for future use.

    Args:
        size: Size of the texture to create
    """
    global _DEFAULT_TEXTURE
    if _DEFAULT_TEXTURE:
        return _DEFAULT_TEXTURE

    _DEFAULT_TEXTURE = Texture(
        get_default_image(size),
        hit_box_algorithm=arcade.hitbox.algo_bounding_box,
    )
    return _DEFAULT_TEXTURE


def get_default_image(size: Size2D[int] = _DEFAULT_IMAGE_SIZE) -> ImageData:
    """
    Generates and returns a default image of the specified size
    and caches it in the default texture cache.

    Args:
        size: Size of the image
    """
    name = f"arcade-default-texture|{size}"
    image_data = arcade.texture.default_texture_cache.image_data_cache.get(name)
    if image_data:
        return image_data

    w, h = size
    im = Image.new("RGBA", (w, h), arcade.color.BLACK)
    draw = ImageDraw.Draw(im)
    draw.rectangle(((0, 0), (w // 2 - 1, h // 2 - 1)), arcade.color.MAGENTA)  # Upper left
    draw.rectangle(((w // 2, h // 2), (w, h)), arcade.color.MAGENTA)  # Lower right

    image_data = ImageData(im, hash=name)
    arcade.texture.default_texture_cache.image_data_cache.put(name, image_data)
    return image_data
