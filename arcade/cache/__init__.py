from typing import Any
from .hit_box import HitBoxCache
from .texture import TextureCache
from .image_data import ImageDataCache


def crate_str_from_values(*args, sep: str = "_") -> str:
    """
    Create a string from a list of parameters.

    Example::

        >> entries = ["blue", 5]
        >> crate_str_from_list("blue", 5)
        "blue_5"

    Args:
        params: List of parameters to create a string from.
        sep: Separator to use between parameters.
    """
    return sep.join([str(x) for x in args])


def crate_str_from_list(entries: list[Any], sep: str = "_") -> str:
    """
    Create a string from a list of parameters.

    Example::

        >> entries = ["blue", 5]
        >> crate_str_from_list(entries)
        "blue_5"

    Args:
        entries: List of parameters to create a string from.
        sep: Separator to use between parameters.
    """
    return crate_str_from_values(*entries, sep=sep)


__all__ = [
    "HitBoxCache",
    "TextureCache",
    "crate_str_from_list",
    "crate_str_from_values",
    "ImageDataCache",
]
