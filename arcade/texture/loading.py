from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Union

import PIL.Image

from arcade.hitbox import HitBoxAlgorithm
from arcade.resources import resolve

from .spritesheet import SpriteSheet
from .texture import ImageData, Texture

LOG = logging.getLogger(__name__)


def load_texture(
    file_path: Union[str, Path],
    *,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
    hash: Optional[str] = None,
) -> Texture:
    """
    Load a texture from disk (no caching).

    When loading a texture a set of hit box points will be generated by default
    based on the pixel data. The default hit box algorithm is a simple 4 to 8
    point hit box. This can be overridden by passing a different hit box or
    the global default can be set in the hitbox module.

    Examples::

        # We can load a texture using resource handles, string path or Path object
        texture = load_texture(":resources:image.png")
        texture = load_texture("image.png")
        texture = load_texture(Path("image.png"))

        # We can also specify a hit box algorithm to use for this texture
        texture = load_texture(
            ":resources:images/enemies/slimeBlock.png",
            hit_box_algorithm=arcade.hitbox.algo_detailed.
        )

    :param file_path: Path to the image file
    :param hit_box_algorithm: The hit box algorithm to use for this texture
    :param hash: (advanced) Optional custom hash for the loaded image
    """
    LOG.debug("load_texture: %s ", file_path)
    if isinstance(file_path, str):
        file_path = resolve(file_path)

    im = PIL.Image.open(file_path)
    if im.mode != "RGBA":
        im = im.convert("RGBA")

    im_data = ImageData(im, hash=hash)
    tex = Texture(im_data, hit_box_algorithm=hit_box_algorithm)
    tex.file_path = file_path
    return tex


def load_image(
    file_path: Union[str, Path],
    *,
    mode: str = "RGBA",
) -> PIL.Image.Image:
    """
    Load a Pillow image from disk (no caching).

    Normally you would use ``load_texture`` instead of this function.
    This function is useful when you want to load an image and then
    manipulate it before creating a texture.

    Note that arcade mainly works with RGBA images. If you override
    the mode you might need to convert the final image to RGBA.

    :param file_path: Path to the image file
    :param mode: The desired mode for the image (default: "RGBA")
    """
    LOG.debug("load_image: %s ", file_path)
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
    LOG.debug("load_spritesheet: %s ", file_name)
    if isinstance(file_name, str):
        file_name = resolve(file_name)

    im = PIL.Image.open(file_name)
    if im.mode != "RGBA":
        im = im.convert("RGBA")

    return SpriteSheet.from_image(im)
