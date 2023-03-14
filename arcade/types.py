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

if TYPE_CHECKING:
    from arcade.texture import Texture


RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]


# Color = Union[RGB, RGBA]
class Color(tuple):

    def __new__(cls, r: int = 0, g: int = 0, b: int = 0, a: int = 255):

        if not 0 <= r <= 255:
            raise ValueError("r must be between 0 and 255, inclusive")

        if not 0 <= g <= 255:
            raise ValueError("g must be between 0 and 255, inclusive")

        if not 0 <= g <= 255:
            raise ValueError("b must be between 0 and 255, inclusive")

        if not 0 <= a <= 255:
            raise ValueError("a must be between 0 and 255, inclusive")

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

    @classmethod
    def from_intensity(cls, intensity: int, a: int = 255) -> "Color":
        if not 0 <= intensity <= 255:
            raise ValueError("intensity must be between 0 and 255, inclusive")

        if not 0 <= a <= 255:
            raise ValueError("a must be between 0 and 255, inclusive")

        return Color(intensity, intensity, intensity, a)


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
