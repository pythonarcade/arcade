from __future__ import annotations

import logging
from typing import Optional, Union
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
    :param hit_box_algorithm:
    :param hash: (advanced) Optional custom hash for the loaded image
    """
    LOG.info("load_texture: %s ", file_path)
    if isinstance(file_path, str):
        file_path = resolve(file_path)

    im = PIL.Image.open(file_path)
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
    return SpriteSheet.from_image(im)
