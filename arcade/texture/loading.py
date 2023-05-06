import logging
from typing import Optional, List, Union, Tuple
from pathlib import Path

import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw

from arcade.types import RectList
from arcade.resources import resolve
from arcade.hitbox import HitBoxAlgorithm
from arcade import cache as _cache
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
    file_path = resolve(file_path)
    crop = (x, y, width, height)
    return _load_or_get_texture(
        file_path,
        hit_box_algorithm=hit_box_algorithm,
        crop=crop,
    )


def _load_tilemap_texture(
    file_path: Path,
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
    crop = (x, y, width, height)
    return _load_or_get_texture(
        file_path,
        hit_box_algorithm=hit_box_algorithm,
        crop=crop,
    )


def _load_or_get_texture(
    file_path: Path,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
    crop: Tuple[int, int, int, int] = (0, 0, 0, 0),
    hash: Optional[str] = None,
) -> Texture:
    """Load a texture, or return a cached version if it's already loaded."""
    hit_box_algorithm = hit_box_algorithm or hitbox.algo_default
    image_data: Optional[ImageData] = None
    texture = None

    # Load the image data from disk or get from cache
    image_data, cached = _load_or_get_image(file_path, hash=hash)
    # If the image was fetched from cache we might have cached texture
    if cached:
        texture = _cache.texture_cache.get_with_config(image_data.hash, hit_box_algorithm)
    # If we still don't have a texture, create it
    if texture is None:
        texture = Texture(image_data, hit_box_algorithm=hit_box_algorithm)
        texture.file_path = file_path
        texture.crop_values = crop
        _cache.texture_cache.put(texture, file_path=file_path)

    # If we have crop values we need to dig deeper looking for cached versions
    if crop != (0, 0, 0, 0):
        image_data = _cache.image_data_cache.get(Texture.create_image_cache_name(file_path, crop))
        # If we don't have and cached image data we can crop from the base texture
        if image_data is None:
            texture = texture.crop(*crop)
            _cache.texture_cache.put(texture)
            _cache.image_data_cache.put(Texture.create_image_cache_name(file_path, crop), texture.image_data)
        else:
            # We might have a texture for this image data
            texture = _cache.texture_cache.get_with_config(image_data.hash, hit_box_algorithm)
            if texture is None:
                texture = Texture(image_data, hit_box_algorithm=hit_box_algorithm)
                texture.file_path = file_path
                texture.crop_values = crop
                _cache.texture_cache.put(texture, file_path=file_path)

    return texture


def _load_or_get_image(
    file_path: Path,
    hash: Optional[str] = None,
) -> Tuple[ImageData, bool]:
    """
    Load an image, or return a cached version

    :param str file_path: Path to image
    :param str hit_box_algorithm: The hit box algorithm
    :param hash: Hash of the image
    :return: Tuple of image data and a boolean indicating if the image
             was fetched from cache
    """
    file_path_str = str(file_path)
    cached = True

    # Do we have cached image data for this file?
    image_data = _cache.image_data_cache.get(
        Texture.create_image_cache_name(file_path_str)
    )
    if not image_data:
        cached = False
        im = PIL.Image.open(file_path).convert("RGBA")
        image_data = ImageData(im, hash)
        _cache.image_data_cache.put(
            Texture.create_image_cache_name(file_path_str),
            image_data,
        )

    return image_data, cached


def load_texture_pair(
    file_name: Union[str, Path],
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
    return texture, texture.flip_left_right()


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
    file_name = resolve(file_name)
    file_name_str = str(file_name)
    hit_box_algorithm = hit_box_algorithm or hitbox.algo_default
    image_cache_name = Texture.create_image_cache_name(file_name_str)

    # Do we have the image in the cache?
    image_data = _cache.image_data_cache.get(image_cache_name)
    if not image_data:
        image_data = ImageData(PIL.Image.open(resolve(file_name)))
        _cache.image_data_cache.put(image_cache_name, image_data)
    image = image_data.image

    texture_sections = []
    for image_location in image_location_list:
        x, y, width, height = image_location

        # Check if we have already created this sub-image
        image_cache_name = Texture.create_image_cache_name(file_name_str, (x, y, width, height))
        sub_image = _cache.image_data_cache.get(image_cache_name)
        if not sub_image:
            Texture.validate_crop(image, x, y, width, height)
            sub_image = ImageData(image.crop((x, y, x + width, y + height)))
            _cache.image_data_cache.put(image_cache_name, sub_image)

        # Do we have a texture for this sub-image?
        texture_cache_name = Texture.create_cache_name(hash=sub_image.hash, hit_box_algorithm=hit_box_algorithm)
        sub_texture = _cache.texture_cache.get(texture_cache_name)
        if not sub_texture:
            sub_texture = Texture(sub_image, hit_box_algorithm=hit_box_algorithm)
            _cache.texture_cache.put(sub_texture)

        if mirrored:
            sub_texture = sub_texture.flip_left_right()
        if flipped:
            sub_texture = sub_texture.flip_top_bottom()

        sub_texture.file_path = file_name
        sub_texture.crop_values = x, y, width, height
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
    file_name = resolve(file_name)
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
        texture.file_path = file_name
        texture.crop_values = start_x, start_y, sprite_width, sprite_height
        texture_list.append(texture)

    return texture_list
