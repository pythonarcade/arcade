import logging
from typing import Optional, List, Union, Tuple
from pathlib import Path

import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw

from arcade.types import RectList
from arcade.resources import resolve_resource_path
from arcade.hitbox import HitBoxAlgorithm
from arcade import cache
from arcade import hitbox
from .texture import Texture, ImageData

LOG = logging.getLogger(__name__)


def load_texture(
    file_path: Union[str, Path],
    *,
    x: int = 0,
    y: int = 0,
    width: int = 0,
    height: int = 0,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
) -> Texture:
    """
    Load an image from disk and create a texture.

    The ``x``, ``y``, ``width``, and ``height`` parameters are used to
    specify a sub-rectangle of the image to load. If not specified, the
    entire image is loaded.

    :param str file_name: Name of the file to that holds the texture.
    :param int x: X coordinate of the texture in the image.
    :param int y: Y coordinate of the texture in the image.
    :param int width: Width of the texture in the image.
    :param int height: Height of the texture in the image.
    :param str hit_box_algorithm: 
    :returns: New :class:`Texture` object.
    :raises: ValueError
    """
    LOG.info("load_texture: %s ", file_path)
    file_path = resolve_resource_path(file_path)
    file_path_str = str(file_path)
    hit_box_algorithm = hit_box_algorithm or hitbox.algo_default
    image_cache_name = Texture.create_image_cache_name(file_path_str, (x, y, width, height))

    # Check if ths file was already loaded and in cache
    image_data = cache.image_data_cache.get(image_cache_name)
    if not image_data:
        image_data = ImageData(PIL.Image.open(file_path).convert("RGBA"))
        cache.image_data_cache.put(image_cache_name, image_data)

    # Attempt to find a texture with the same configuration
    texture = cache.texture_cache.get_with_config(image_data.hash, hit_box_algorithm)
    if not texture:
        texture = Texture(image_data, hit_box_algorithm=hit_box_algorithm)
        texture.origin = file_path_str
        cache.texture_cache.put(texture, file_path=file_path_str)

    # If the crop values give us a different texture, return that instead
    texture_cropped = texture.crop(x, y, width, height)
    if texture_cropped != texture:
        texture = texture_cropped

    return texture


def load_texture_pair(
    file_name: str,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None
) -> Tuple[Texture, Texture]:
    """
    Load a texture pair, with the second being a mirror image of the first.
    Useful when doing animations and the character can face left/right.

    :param str file_name: Path to texture
    :param str hit_box_algorithm: The hit box algorithm
    """
    LOG.info("load_texture_pair: %s ", file_name)
    texture = load_texture(file_name, hit_box_algorithm=hit_box_algorithm)
    return texture, texture.flip_left_to_right()


def load_textures(
    file_name: Union[str, Path],
    image_location_list: RectList,
    mirrored: bool = False,
    flipped: bool = False,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
) -> List[Texture]:
    """
    Load a set of textures from a single image file.

    Note: If the code is to load only part of the image, the given `x`, `y`
    coordinates will start with the origin `(0, 0)` in the upper left of the
    image. When drawing, Arcade uses `(0, 0)` in the lower left corner.
    Be careful with this reversal.

    For a longer explanation of why computers sometimes start in the upper
    left, see:
    http://programarcadegames.com/index.php?chapter=introduction_to_graphics&lang=en#section_5

    :param str file_name: Name of the file.
    :param List image_location_list: List of image sub-locations. Each rectangle should be
           a `List` of four floats: `[x, y, width, height]`.
    :param bool mirrored: If set to `True`, the image is mirrored left to right.
    :param bool flipped: If set to `True`, the image is flipped upside down.
    :param str hit_box_algorithm: One of None, 'None', 'Simple' (default) or 'Detailed'.
    :param float hit_box_detail: Float, defaults to 4.5. Used with 'Detailed' to hit box
    :returns: List of :class:`Texture`'s.

    :raises: ValueError
    """
    LOG.info("load_textures: %s ", file_name)
    file_name = resolve_resource_path(file_name)
    file_name_str = str(file_name)
    hit_box_algorithm = hit_box_algorithm or hitbox.algo_default
    image_cache_name = Texture.create_image_cache_name(file_name_str)

    # Do we have the image in the cache?
    image_data = cache.image_data_cache.get(image_cache_name)
    if not image_data:
        image_data = ImageData(PIL.Image.open(resolve_resource_path(file_name)))
        cache.image_data_cache.put(image_cache_name, image_data)
    image = image_data.image

    texture_sections = []
    for image_location in image_location_list:
        x, y, width, height = image_location

        # Check if we have already created this sub-image
        image_cache_name = Texture.create_image_cache_name(file_name_str, (x, y, width, height))
        sub_image = cache.image_data_cache.get(image_cache_name)
        if not sub_image:
            Texture.validate_crop(image, x, y, width, height)
            sub_image = ImageData(image.crop((x, y, x + width, y + height)))
            cache.image_data_cache.put(image_cache_name, sub_image)            

        # Do we have a texture for this sub-image?
        texture_cache_name = Texture.create_cache_name(hash=sub_image.hash, hit_box_algorithm=hit_box_algorithm)
        sub_texture = cache.texture_cache.get(texture_cache_name)
        if not sub_texture:
            sub_texture = Texture(sub_image, hit_box_algorithm=hit_box_algorithm)
            cache.texture_cache.put(sub_texture)

        if mirrored:
            sub_texture = sub_texture.flip_left_to_right()
        if flipped:
            sub_texture = sub_texture.flip_top_to_bottom()

        sub_texture.origin = image_cache_name
        texture_sections.append(sub_texture)

    return texture_sections


def load_spritesheet(
    file_name: Union[str, Path],
    sprite_width: int,
    sprite_height: int,
    columns: int,
    count: int,
    margin: int = 0,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
) -> List[Texture]:
    """
    :param str file_name: Name of the file to that holds the texture.
    :param int sprite_width: Width of the sprites in pixels
    :param int sprite_height: Height of the sprites in pixels
    :param int columns: Number of tiles wide the image is.
    :param int count: Number of tiles in the image.
    :param int margin: Margin between images
    :param str hit_box_algorithm: The hit box algorithm
    :returns List: List of :class:`Texture` objects.
    """
    LOG.info("load_spritesheet: %s ", file_name)
    texture_list = []

    # TODO: Support caching?
    file_name = resolve_resource_path(file_name)
    source_image = PIL.Image.open(file_name).convert("RGBA")

    for sprite_no in range(count):
        row = sprite_no // columns
        column = sprite_no % columns
        start_x = (sprite_width + margin) * column
        start_y = (sprite_height + margin) * row
        image = source_image.crop(
            (start_x, start_y, start_x + sprite_width, start_y + sprite_height)
        )
        texture = Texture(
            image,
            hit_box_algorithm=hit_box_algorithm,
        )
        texture.origin = f"{file_name}|{sprite_no}"
        texture_list.append(texture)

    return texture_list
