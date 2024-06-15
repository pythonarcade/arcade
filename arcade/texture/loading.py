from __future__ import annotations

import logging
from typing import Optional, Union, Tuple, List
from pathlib import Path

import PIL.Image

from arcade.resources import resolve
from arcade.hitbox import HitBoxAlgorithm
from .texture import Texture, ImageData
from .spritesheet import SpriteSheet

LOG = logging.getLogger(__name__)


def load_texture(
    file_path: Union[str, Path],
    *,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
    hash: Optional[str] = None,
) -> Texture:
    """
    Load a texture from disk (no caching).

    :param file_name: Path to the image file
    :param hit_box_algorithm: The hit box algorithm to use for this texture
    :param hash: (advanced) Optional custom hash for the loaded image
    """
    LOG.info("load_texture: %s ", file_path)
    if isinstance(file_path, str):
        file_path = resolve(file_path)

    im = PIL.Image.open(file_path)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    im_data = ImageData(im, hash=hash)
    return Texture(im_data, hit_box_algorithm=hit_box_algorithm)


def load_spritesheet(file_name: Union[str, Path]) -> SpriteSheet:
    """
    Loads an image from disk returning a sprite sheet that can
    further be used to crop out smaller images.

    :param file_name: Path to the image file
    """
    LOG.info("load_spritesheet: %s ", file_name)
    if isinstance(file_name, str):
        file_name = resolve(file_name)

    im = PIL.Image.open(file_name)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    return SpriteSheet.from_image(im)


def load_texture_pair(
    file_name: Union[str, Path], hit_box_algorithm: Optional[HitBoxAlgorithm] = None
) -> Tuple[Texture, Texture]:
    """
    Load a texture from disk (no caching), and return a tuple containing
    the original texture and left-right flipped texture.

    This is useful for quickly loading textures for a sprite that can face left or right.

    :param file_name: Path to the image file
    :param hit_box_algorithm: The hit box algorithm to use for this texture
    """
    LOG.info("load_texture_pair: %s ", file_name)
    if isinstance(file_name, str):
        file_name = resolve(file_name)

    texture = load_texture(file_name, hit_box_algorithm=hit_box_algorithm)
    return texture, texture.flip_left_right()


# def load_textures(
#     file_name: Union[str, Path],
#     image_location_list: List[Tuple[int, int, int, int]],
#     mirrored: bool = False,
#     flipped: bool = False,
#     hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
# ) -> List[Texture]:
#     """
#     Load a set of textures from a single image file.

#     Note: If the code is to load only part of the image, the given `x`, `y`
#     coordinates will start with the origin `(0, 0)` in the upper left of the
#     image. When drawing, Arcade uses `(0, 0)` in the lower left corner.
#     Be careful with this reversal.

#     For a longer explanation of why computers sometimes start in the upper
#     left, see:
#     http://programarcadegames.com/index.php?chapter=introduction_to_graphics&lang=en#section_5

#     :param file_name: Name of the file.
#     :param image_location_list: List of image sub-locations. Each rectangle should be
#            a `List` of four floats: `[x, y, width, height]`.
#     :param mirrored: If set to `True`, the image is mirrored left to right.
#     :param flipped: If set to `True`, the image is flipped upside down.
#     :param hit_box_algorithm: One of None, 'None', 'Simple' (default) or 'Detailed'.
#     :param hit_box_detail: Float, defaults to 4.5. Used with 'Detailed' to hit box
#     :returns: List of :class:`Texture`'s.

#     :raises: ValueError
#     """
#     LOG.info("load_textures: %s ", file_name)
#     file_name = resolve(file_name)
#     file_name_str = str(file_name)
#     hit_box_algorithm = hit_box_algorithm or hitbox.algo_default
#     image_cache_name = Texture.create_image_cache_name(file_name_str)

#     # Do we have the image in the cache?
#     image_data = _cache.image_data_cache.get(image_cache_name)
#     if not image_data:
#         image_data = ImageData(PIL.Image.open(resolve(file_name)))
#         _cache.image_data_cache.put(image_cache_name, image_data)
#     image = image_data.image

#     texture_sections = []
#     for image_location in image_location_list:
#         x, y, width, height = image_location

#         # Check if we have already created this sub-image
#         image_cache_name = Texture.create_image_cache_name(file_name_str, (x, y, width, height))
#         sub_image = _cache.image_data_cache.get(image_cache_name)
#         if not sub_image:
#             Texture.validate_crop(image, x, y, width, height)
#             sub_image = ImageData(image.crop((x, y, x + width, y + height)))
#             _cache.image_data_cache.put(image_cache_name, sub_image)

#         # Do we have a texture for this sub-image?
#         texture_cache_name = Texture.create_cache_name(hash=sub_image.hash, hit_box_algorithm=hit_box_algorithm)
#         sub_texture = _cache.texture_cache.get(texture_cache_name)
#         if not sub_texture:
#             sub_texture = Texture(sub_image, hit_box_algorithm=hit_box_algorithm)
#             _cache.texture_cache.put(sub_texture)

#         if mirrored:
#             sub_texture = sub_texture.flip_left_right()
#         if flipped:
#             sub_texture = sub_texture.flip_top_bottom()

#         sub_texture.file_path = file_name
#         sub_texture.crop_values = x, y, width, height
#         texture_sections.append(sub_texture)

#     return texture_sections
