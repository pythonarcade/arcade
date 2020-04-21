"""
Module specifying data custom types used for type hinting.
"""
from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from collections import namedtuple


RGB = Union[Tuple[int, int, int], List[int]]
RGBA = Union[Tuple[int, int, int, int], List[int]]
Color = Union[RGB, RGBA]
Point = Union[Tuple[float, float], List[float]]
NamedPoint = namedtuple('Point', ['x', 'y'])

Vector = Point
PointList = Sequence[Point]
Rect = Union[Tuple[float, float, float, float], List[float]]  # x, y, width, height
RectList = Union[Tuple[Rect, ...], List[Rect]]
