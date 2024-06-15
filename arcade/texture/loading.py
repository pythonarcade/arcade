from __future__ import annotations

import logging
from typing import Optional, Union, Tuple
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


def load_image(
    file_path: Union[str, Path],
    *,
    mode: str = "RGBA",
) -> PIL.Image.Image:
    """
    Load an image from disk (no caching).

    :param file_path: Path to the image file
    :param mode: The desired mode for the image (default: "RGBA")
    """
    LOG.info("load_image: %s ", file_path)
    if isinstance(file_path, str):
        file_path = resolve(file_path)

    im = PIL.Image.open(file_path)
    if im.mode != mode:
        im = im.convert(mode)
    return im


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
