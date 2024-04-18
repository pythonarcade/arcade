"""Fundamental aliases, classes, and related constants.

As general rules:

#. Things only go in this module if they serve multiple purposes
   throughout arcade
#. Only expose the most important classes at this module's top level

For example, color-related types and related aliases go in
``arcade.types`` because they're used throughout the codebase. This
includes all the following areas:

#. :py:class:`~arcade.Sprite`
#. :py:class:`~arcade.SpriteList`
#. :py:class:`~arcade.Text`
#. The :py:mod:`arcade.gui` widgets
#. Functions in :py:mod:`arcade.drawing_commands`

However, since the color types, aliases, and constants are all related,
they go in the :py:mod:`arcade.types.color` submodule.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import (
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Union,
    TYPE_CHECKING,
    TypeVar
)

from pytiled_parser import Properties


# Backward-compatibility for buffer protocol objects
# To learn more, see https://docs.python.org/3.8/c-api/buffer.html
if sys.version_info >= (3, 12):
    from collections.abc import Buffer as BufferProtocol
else:
    # The most common built-in buffer protocol objects
    import ctypes
    from array import array
    from collections.abc import ByteString

    # This is used instead of the typing_extensions version since they
    # use an ABC which registers virtual subclasses. This will not work
    # with ctypes.Array since virtual subclasses must be concrete.
    # See: https://peps.python.org/pep-0688/
    BufferProtocol = Union[ByteString, memoryview, array, ctypes.Array]


#: 1. Makes pyright happier while also telling readers
#: 2. Tells readers we're converting any ints to floats
AsFloat = Union[float, int]


# Generic color aliases
from arcade.types.color import RGB
from arcade.types.color import RGBA
from arcade.types.color import RGBOrA

# Specific color aliases
from arcade.types.color import RGB255
from arcade.types.color import RGBA255
from arcade.types.color import RGBNormalized
from arcade.types.color import RGBANormalized
from arcade.types.color import RGBOrA255
from arcade.types.color import RGBOrANormalized

# The Color helper type
from arcade.types.color import Color


__all__ = [
    "AsFloat",
    "BufferProtocol",
    "Color",
    "IPoint",
    "PathOr",
    "PathOrTexture",
    "Point",
    "Point3",
    "PointList",
    "EMPTY_POINT_LIST",
    "Rect",
    "RectList",
    "RGB",
    "RGBOrA",
    "RGBA255",
    "RGB255",
    "RGBNormalized",
    "RGBOrA255",
    "RGBANormalized",
    "TiledObject",
    "Velocity"
]


# Point = Union[Tuple[AsFloat, AsFloat], List[AsFloat]]
Point = Tuple[AsFloat, AsFloat]
Point3 = Tuple[AsFloat, AsFloat, AsFloat]
IPoint = Tuple[int, int]

# We won't keep this forever. It's a temp stub for particles we'll replace.
Velocity = Tuple[AsFloat, AsFloat]

PointList = Sequence[Point]
# Speed / typing workaround:
# 1. Eliminate extra allocations
# 2. Allows type annotation to be cleaner, primarily for HitBox & subclasses
EMPTY_POINT_LIST: PointList = tuple()


Rect = Union[Tuple[int, int, int, int], List[int]]  # x, y, width, height
RectList = Union[Tuple[Rect, ...], List[Rect]]
FloatRect = Union[Tuple[AsFloat, AsFloat, AsFloat, AsFloat], List[AsFloat]]  # x, y, width, height


# Path handling
PathLike = Union[str, Path, bytes]
_POr = TypeVar('_POr') # Allows PathOr[TypeNameHere] syntax
PathOr = Union[PathLike, _POr]


# Specific utility resource aliases with type imports
if TYPE_CHECKING:
    from arcade.texture import Texture

PathOrTexture = PathOr["Texture"]


class TiledObject(NamedTuple):
    shape: Union[Point, PointList, Rect]
    properties: Optional[Properties] = None
    name: Optional[str] = None
    type: Optional[str] = None
