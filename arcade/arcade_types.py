"""
Module specifying data custom types used for type hinting.
"""
from collections import namedtuple
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
