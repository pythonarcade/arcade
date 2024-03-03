from __future__ import annotations

from .texture import Texture, ImageData
from .spritesheet import SpriteSheet
from .loading import (
    load_texture,
    load_spritesheet,
    load_texture_pair,
)
from .generate import (
    make_circle_texture,
    make_soft_circle_texture,
    make_soft_square_texture,
)
from .tools import (
    get_default_texture,
    get_default_image,
)
from .manager import TextureCacheManager

default_manager = TextureCacheManager()


__all__ = [
    "Texture",
    "ImageData",
    "load_texture",
    "load_spritesheet",
    "load_texture_pair",
    "make_circle_texture",
    "make_soft_circle_texture",
    "make_soft_square_texture",
    "get_default_texture",
    "get_default_image",
    "TextureCacheManager",
    "SpriteSheet",
    "default_manager",
]
