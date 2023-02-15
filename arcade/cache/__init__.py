from typing import Any, List
from .hit_box import HitBoxCache
from .texture import TextureCache
from .image_data import ImageDataCache

texture_cache = TextureCache()
image_data_cache = ImageDataCache()
hit_box_cache = HitBoxCache()


def crate_str_from_values(*args, sep: str = "_") -> str:
    """
    Create a string from a list of parameters.

    Example::

        >> entries = ["blue", 5]
        >> crate_str_from_list("blue", 5)
        "blue_5"

    :param params: List of parameters to create a string from.
    :param sep: Separator to use between parameters.
    """
    return sep.join([str(x) for x in args])


def crate_str_from_list(entries: List[Any], sep: str = "_") -> str:
    """
    Create a string from a list of parameters.

    Example::

        >> entries = ["blue", 5]
        >> crate_str_from_list(entries)
        "blue_5"

    :param entries: List of parameters to create a string from.
    :param sep: Separator to use between parameters.
    """
    return crate_str_from_values(*entries, sep=sep)


__all__ = [
    "HitBoxCache",
    "TextureCache",
    "crate_str_from_list",
    "crate_str_from_values",
    "ImageDataCache",
]
