from __future__ import annotations

from PIL import Image, ImageDraw
import arcade
import arcade.cache
from .texture import ImageData, Texture
from arcade.types import IPoint
from arcade import cache

_DEFAULT_TEXTURE = None
_DEFAULT_IMAGE_SIZE = (128, 128)


def cleanup_texture_cache():
    """
    This cleans up the cache of textures. Useful when running unit tests so that
    the next test starts clean.
    """
    cache.texture_cache.clear()
    arcade.cache.image_data_cache.clear()


def get_default_texture(size: IPoint = _DEFAULT_IMAGE_SIZE) -> Texture:
    """
    Creates and returns a default texture and caches it internally for future use.

    :param size: Size of the texture to create
    :return: The default texture.
    """
    global _DEFAULT_TEXTURE
    if _DEFAULT_TEXTURE:
        return _DEFAULT_TEXTURE

    _DEFAULT_TEXTURE = Texture(
        get_default_image(size),
        hit_box_algorithm=arcade.hitbox.algo_bounding_box,
    )
    return _DEFAULT_TEXTURE


def get_default_image(size: IPoint = _DEFAULT_IMAGE_SIZE) -> ImageData:
    """
    Generates and returns a default image and caches it internally for future use.

    :param size: Size of the image to create.
    :return: The default image.
    """
    name = f"arcade-default-texture|{size}"
    image_data = cache.image_data_cache.get(name)
    if image_data:
        return image_data

    w, h = size
    im = Image.new("RGBA", (w, h), arcade.color.BLACK)
    draw = ImageDraw.Draw(im)
    draw.rectangle(((0, 0), (w // 2 - 1, h // 2 - 1)), arcade.color.MAGENTA)  # Upper left
    draw.rectangle(((w // 2, h // 2), (w, h)), arcade.color.MAGENTA)  # Lower right

    image_data = ImageData(im, hash=name)
    cache.image_data_cache.put(name, image_data)
    return image_data


if __name__ == "__main__":
    get_default_texture().image.show()
