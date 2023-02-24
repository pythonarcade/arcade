from .texture import Texture, ImageData
from .loading import (
    load_texture,
    load_textures,
    load_texture_pair,
    load_spritesheet,
)
from .generate import (
    make_circle_texture,
    make_soft_circle_texture,
    make_soft_square_texture,
)
from arcade import cache
from arcade.texture import transforms as transform

def cleanup_texture_cache():
    """
    This cleans up the cache of textures. Useful when running unit tests so that
    the next test starts clean.
    """
    cache.texture_cache.clear()
    cache.image_data_cache.clear()


__all__ = [
    "Texture",
    "ImageData",
    "load_texture",
    "load_textures",
    "load_texture_pair",
    "load_spritesheet",
    "cleanup_texture_cache",
    "make_circle_texture",
    "make_soft_circle_texture",
    "make_soft_square_texture",
    "transform",
]
