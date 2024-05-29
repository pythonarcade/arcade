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


# Since it's used everywhere, we'll prevent partial submodule
# and circular import problems by isolating it in a little box.
from arcade.types.numbers import AsFloat

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

# We'll be moving our Vec-like items into this (Points, Sizes, etc)
from arcade.types.vector_like import AnchorPoint, Point2, Point3

# Rectangles
from arcade.types.rect import ViewportParams
from arcade.types.rect import RectParams
from arcade.types.rect import RectKwargs

from arcade.types.rect import Rect
from arcade.types.rect import LRBT
from arcade.types.rect import LBWH
from arcade.types.rect import XYWH
from arcade.types.rect import XYRR
from arcade.types.rect import Viewport


__all__ = [
    "AsFloat",
    "BufferProtocol",
    "Color",
    "IPoint",
    "PathOr",
    "PathOrTexture",
    "Point",
    "Point2",
    "Point3",
    "PointList",
    "Point2List",
    "Point3List",
    "EMPTY_POINT_LIST",
    "AnchorPoint",
    "Rect",
    "LRBT",
    "LBWH",
    "XYWH",
    "XYRR",
    "Viewport",
    "ViewportParams",
    "RectParams",
    "RectKwargs",
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
IPoint = Tuple[int, int]
Point = Union[Point2, Point3]


# We won't keep this forever. It's a temp stub for particles we'll replace.
Velocity = Tuple[AsFloat, AsFloat]

PointList = Sequence[Point]
Point2List = Sequence[Point2]
Point3List = Sequence[Point3]
# Speed / typing workaround:
# 1. Eliminate extra allocations
# 2. Allows type annotation to be cleaner, primarily for HitBox & subclasses
EMPTY_POINT_LIST: PointList = tuple()

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
    shape: Union[Point, PointList, Tuple[int, int, int, int]]
    properties: Optional[Properties] = None
    name: Optional[str] = None
    type: Optional[str] = None
