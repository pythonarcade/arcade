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
from typing import Any, NamedTuple, Union, TYPE_CHECKING, TypeVar, Iterable, Protocol

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

# Vector-like items and collections
from arcade.types.vector_like import Point2
from arcade.types.vector_like import Point3
from arcade.types.vector_like import Point
from arcade.types.vector_like import Point2List
from arcade.types.vector_like import Point3List
from arcade.types.vector_like import PointList
from arcade.types.vector_like import EMPTY_POINT_LIST
from arcade.types.vector_like import AnchorPoint

# Rectangles
from arcade.types.rect import IntRectParams
from arcade.types.rect import RectParams
from arcade.types.rect import RectKwargs

from arcade.types.rect import Rect
from arcade.types.rect import LRBT
from arcade.types.rect import LBWH
from arcade.types.rect import XYWH
from arcade.types.rect import XYRR
from arcade.types.rect import Viewport

# Boxes
from arcade.types.box import Box
from arcade.types.box import LRBTNF
from arcade.types.box import XYZWHD


__all__ = [
    "AsFloat",
    "BufferProtocol",
    "Color",
    "IntRectParams",
    "IPoint",
    "PathOr",
    "PathOrTexture",
    "Point",
    "Point2",
    "Point3",
    "PointList",
    "Point2List",
    "Point3List",
    "OneOrIterableOf",
    "EMPTY_POINT_LIST",
    "AnchorPoint",
    "Rect",
    "LRBT",
    "LBWH",
    "XYWH",
    "XYRR",
    "Viewport",
    "RectParams",
    "RectKwargs",
    "Box",
    "LRBTNF",
    "XYZWHD",
    "HasAddSubMul",
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
    "Velocity",
]


_T = TypeVar("_T")


OneOrIterableOf = Union[_T, Iterable[_T]]
"""Either an instance of something or an iterable of them.

When writing loading code which is not performance critical,
you may also want to see the following:

* :py:func:`arcade.utils.grow_sequence`
* :py:func:`arcade.utils.is_iterable`
* :py:func:`arcade.utils.is_nonstr_iterable`
* :py:func:`arcade.utils.is_str_or_noniterable`

.. tip:: You can inline the contents of these functions when
         performance matters.

You should avoid using this annotation with values which may include
``None``. These include:

* Pipe syntax such as ``OneOrIterable[MyType | None]``
* :py:class:`typing.Optional` equivalents of pipe syntax

Instead, consider one of the following when possible:

.. code-block:: python

   def annotated(argument: OneOrIterableOf[MyType] = tuple()):
      ...

   def annotated2(argument: OneOrIterableOf[MyType] | None = tuple()):
      ...

"""

# --- Begin potentially obsolete annotations ---

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
#        Args:
#:           size: A made-up hypothetical argument.
#:           color: Hypothetical texture-related argument.
#:       """
#:       ...  # No function definition
#:
Size2D = tuple[_T, _T]

#: Used in :py:class:`~arcade.sprite_list.spatial_hash.SpatialHash`.
IPoint = tuple[int, int]


# We won't keep this forever. It's a temp stub for particles we'll replace.
Velocity = tuple[AsFloat, AsFloat]

# --- End potentially obsolete annotations ---


# These are for the argument type + return type. They're separate TypeVars
# to handle cases which take tuple but return Vec2 (e.g. pyglet.math.Vec2).
_T_contra = TypeVar("_T_contra", contravariant=True)  # Same or more general than T
_T_co = TypeVar("_T_co", covariant=True)  # Same or more specific than T


class HasAddSubMul(Protocol[_T_contra, _T_co]):
    """Matches types which work with :py:func:`arcade.math.lerp`."""

    # The / matches float and similar operations to keep pyright
    # happy since built-in arithmetic makes them positional only.
    # See https://peps.python.org/pep-0570/
    def __add__(self, value: _T_contra, /) -> _T_co: ...
    def __sub__(self, value: _T_contra, /) -> _T_co: ...
    def __mul__(self, value: _T_contra, /) -> _T_co: ...


# Path handling
PathLike = Union[str, Path, bytes]
_POr = TypeVar("_POr")  # Allows PathOr[TypeNameHere] syntax
PathOr = Union[PathLike, _POr]


# Specific utility resource aliases with type imports
if TYPE_CHECKING:
    # The linters are wrong: this is used, so we noqa it
    from arcade.texture import Texture  # noqa: F401

PathOrTexture = PathOr["Texture"]


class TiledObject(NamedTuple):
    """Object in a tilemaps"""

    shape: Union[Point, PointList, tuple[int, int, int, int]]
    """Shape of the object"""
    properties: Properties | None = None
    """Properties of the object"""
    name: str | None = None
    """Name of the object"""
    type: str | None = None
    """Type of the object"""


# Stolen from Pylance
class SupportsDunderLT(Protocol[_T_contra]):
    def __lt__(self, other: _T_contra, /) -> bool: ...


class SupportsDunderGT(Protocol[_T_contra]):
    def __gt__(self, other: _T_contra, /) -> bool: ...


SupportsRichComparison = Union[SupportsDunderLT[Any], SupportsDunderGT[Any]]
