"""
Module specifying data custom types used for type hinting.
"""
from array import array
from pathlib import Path
from collections import namedtuple
from collections.abc import ByteString
from typing import (
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Union,
    TYPE_CHECKING,
)
from pytiled_parser import Properties
from arcade.utils import outside_range_msg

if TYPE_CHECKING:
    from arcade.texture import Texture


RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]


# Color = Union[RGB, RGBA]
class Color(tuple):

    def __new__(cls, r: int = 0, g: int = 0, b: int = 0, a: int = 255):

        if not 0 <= r <= 255:
            raise ValueError(outside_range_msg("r", r))

        if not 0 <= g <= 255:
            raise ValueError(outside_range_msg("g", g))

        if not 0 <= g <= 255:
            raise ValueError(outside_range_msg("b", b))

        if not 0 <= a <= 255:
            raise ValueError(outside_range_msg("a", a))

        super().__new__(cls, (r, g, b, a))

    @property
    def r(self) -> int:
        return self[0]

    @property
    def g(self) -> int:
        return self[1]

    @property
    def b(self) -> int:
        return self[2]

    @property
    def a(self) -> int:
        return self[3]

    @property
    def normalized(self) -> Tuple[float, float, float, float]:
        """
        Return this color as a tuple of normalized floats.

        Examples::

            >>> arcade.color.WHITE.normalized
            (1.0, 1.0, 1.0, 1.0)

            >>> arcade.color.BLACK.normalized
            (0.0, 0.0, 0.0, 1.0)

            >>> arcade.color.TRANSPARENT_BLACK.normalized
            (0.0, 0.0, 0.0, 0.0)

        """
        return self[0] / 255, self[1] / 255, self[2] / 255, self[3] / 255

    @classmethod
    def from_intensity(cls, intensity: int, a: int = 255) -> "Color":
        """
        Return a shade of gray of the given intensity.

        Example::

            >>> Color.from_intensity(255)
            Color(255, 255, 255, 255)

            >>> Color.from_intensity(128)
            Color(128, 128, 128, 255)

        :param intensity: How bright the shade should be
        :param a: a transparency value, fully opaque by default
        :return:
        """

        if not 0 <= intensity <= 255:
            raise ValueError(outside_range_msg("intensity", intensity))

        if not 0 <= a <= 255:
            raise ValueError(outside_range_msg("a", a))

        return Color(intensity, intensity, intensity, a)

    @classmethod
    def from_uint24(cls, color: int, a: int = 255) -> "Color":
        """
        Return a Color from an unsigned 3-byte (24 bit) integer.

        These ints may be between 0 and 16777215 (``0xFFFFFF``), inclusive.

        Example::

            >>> Color.from_uint24(16777215)
            (255, 255, 255, 255)

            >>> Color.from_uint24(0xFF0000)
            (255, 0, 0, 255)

        :param color: a 3-byte int between 0 and 16777215 (``0xFFFFFF``)
        :param a: an alpha value to use between 0 and 255, inclusive.
        """

        if not 0 <= color <= 0xFFFFFF:
            raise ValueError(outside_range_msg("color", color, upper=0xFFFFFF))

        if not 0 <= a <= 255:
            raise ValueError(outside_range_msg("a", a))

        return cls(
            r=(color & 0xFF0000) >> 16,
            g=(color & 0xFF00) >> 8,
            b=color & 0xFF,
            a=a
        )

    @classmethod
    def from_uint32(cls, color: int) -> "Color":
        """
        Return a Color tuple for a given unsigned 4-byte (32-bit) integer

        The bytes are interpreted as R, G, B, A.

        Examples::

            >>> Color.from_uint32(4294967295)
            (255, 255, 255, 255)

            >>> Color.from_uint32(0xFF0000FF)
            (255, 0, 0, 255)

        :param int color: An int between 0 and 4294967295 (``0xFFFFFFFF``)
        """
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError(outside_range_msg("color", color, upper=0xFFFFFFFF))

        return cls(
            r=(color & 0xFF000000) >> 24,
            g=(color & 0xFF0000) >> 16,
            b=(color & 0xFF00) >> 8,
            a=(color & 0xFF)
        )


ColorLike = Union[Color, RGB, RGBA]


# Point = Union[Tuple[float, float], List[float]]
# Vector = Point
Point = Tuple[float, float]
IPoint = Tuple[int, int]
Vector = Point
NamedPoint = namedtuple("NamedPoint", ["x", "y"])

PointList = Sequence[Point]
Rect = Union[Tuple[int, int, int, int], List[int]]  # x, y, width, height
RectList = Union[Tuple[Rect, ...], List[Rect]]

PathOrTexture = Optional[Union[str, Path, "Texture"]]


class TiledObject(NamedTuple):
    shape: Union[Point, PointList, Rect]
    properties: Optional[Properties] = None
    name: Optional[str] = None
    type: Optional[str] = None


# This is a temporary workaround for the lack of a way to type annotate
# objects implementing the buffer protocol. Although there is a PEP to
# add typing, it is scheduled for 3.12. Since that is years away from
# being our minimum Python version, we have to use a workaround. See
# the PEP and Python doc for more information:
# https://peps.python.org/pep-0688/
# https://docs.python.org/3/c-api/buffer.html
BufferProtocol = Union[ByteString, memoryview, array]
