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

# Don't lint import order since we have conditional compatibility shims
# flake8: noqa: E402
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
    "RGBA",
    "RGBOrA",
    "RGB255",
    "RGBA255",
    "RGBOrA255",
    "RGBNormalized",
    "RGBANormalized",
    "RGBOrANormalized",
    "Size2D",
    "TiledObject",
    "Velocity"
]


_T = TypeVar('_T')

#: ``Size2D`` helps mark int or float sizes. Use it like a
#: :py:class:`typing.Generic`'s bracket notation as follows:
#:
#: .. code-block:: python
#:
#:    def example_Function(size: Size2D[int], color: RGBA255) -> Texture:
#:       """An example of how to use Size2D.
#:
#:       Look at signature above, not the missing function body. The
#:       ``size`` argument is how you can mark texture sizes, while
#:       you can use ``Size2D[float]`` to denote float regions.
#:
#:       :param size: A made-up hypothetical argument.
#:       :param color: Hypothetical texture-related argument.
#:       """
#:       ...  # No function definition
#:
Size2D = Tuple[_T, _T]

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
    # The linters are wrong: this is used, so we noqa it
    from arcade.texture import Texture  # noqa: F401

PathOrTexture = PathOr["Texture"]


class TiledObject(NamedTuple):
    shape: Union[Point, PointList, Rect]
    properties: Optional[Properties] = None
    name: Optional[str] = None
    type: Optional[str] = None
