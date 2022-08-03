"""
Module specifying data custom types used for type hinting.
"""
from array import array
from collections import namedtuple
from collections.abc import ByteString
from typing import List, NamedTuple, Optional, Sequence, Tuple, Union

from pytiled_parser import Properties


RGB = Union[Tuple[int, int, int], List[int]]
RGBA = Union[Tuple[int, int, int, int], List[int]]
Color = Union[RGB, RGBA]
# Point = Union[Tuple[float, float], List[float]]
# Vector = Point
Point = Tuple[float, float]
Vector = Point
NamedPoint = namedtuple("NamedPoint", ["x", "y"])

Sequence[int]
PointList = Sequence[Point]
Rect = Union[Tuple[float, float, float, float], List[float]]  # x, y, width, height
RectList = Union[Tuple[Rect, ...], List[Rect]]


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
