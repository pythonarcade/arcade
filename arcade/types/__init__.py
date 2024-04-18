"""
Module specifying data custom types used for type hinting.
"""
from __future__ import annotations

import sys
from array import array
import ctypes
from collections import namedtuple
from collections.abc import ByteString
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

if TYPE_CHECKING:
    from arcade.texture import Texture


#: 1. Makes pyright happier while also telling readers
#: 2. Tells readers we're converting any ints to floats
AsFloat = Union[float, int]


# Generic color aliases
from arcade.types.color import RGB
from arcade.types.color import RGBA
from arcade.types.color import RGBOrA

# Specific color aliases
from arcade.types.color import RGBA255
from arcade.types.color import RGBANormalized
from arcade.types.color import RGBOrA255
from arcade.types.color import RGBOrANormalized

# The Color helper type
from arcade.types.color import Color


RGBA255OrNormalized = Union[RGBA255, RGBANormalized]


__all__ = [
    "BufferProtocol",
    "Color",
    "ColorLike",
    "IPoint",
    "PathOrTexture",
    "Point",
    "PointList",
    "EMPTY_POINT_LIST",
    "NamedPoint",
    "Rect",
    "RectList",
    "RGB",
    "RGBA255",
    "RGBANormalized",
    "RGBA255OrNormalized",
    "TiledObject",
    "Vector"
]

ColorLike = Union[RGB, RGBA255]

# Point = Union[Tuple[float, float], List[float]]
# Vector = Point
Point = Tuple[float, float]
Point3 = Tuple[float, float, float]
IPoint = Tuple[int, int]
Vector = Point
NamedPoint = namedtuple("NamedPoint", ["x", "y"])


PointList = Sequence[Point]
# Speed / typing workaround:
# 1. Eliminate extra allocations
# 2. Allows type annotation to be cleaner, primarily for HitBox & subclasses
EMPTY_POINT_LIST: PointList = tuple()


Rect = Union[Tuple[int, int, int, int], List[int]]  # x, y, width, height
RectList = Union[Tuple[Rect, ...], List[Rect]]
FloatRect = Union[Tuple[float, float, float, float], List[float]]  # x, y, width, height

PathOrTexture = Optional[Union[str, Path, "Texture"]]


class TiledObject(NamedTuple):
    shape: Union[Point, PointList, Rect]
    properties: Optional[Properties] = None
    name: Optional[str] = None
    type: Optional[str] = None


if sys.version_info >= (3, 12):
    from collections.abc import Buffer as BufferProtocol
else:
    # This is used instead of the typing_extensions version since they
    # use an ABC which registers virtual subclasses. This will not work
    # with ctypes.Array since virtual subclasses must be concrete.
    # See: https://peps.python.org/pep-0688/
    BufferProtocol = Union[ByteString, memoryview, array, ctypes.Array]
