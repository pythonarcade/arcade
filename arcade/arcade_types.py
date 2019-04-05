"""
Module specifying data custom types used for type hinting.
"""
from typing import Tuple
from typing import List
from typing import Union

RGB = Union[Tuple[int, int, int], List[int]]
RGBA = Union[Tuple[int, int, int, int], List[int]]
Color = Union[RGB, RGBA]
Point = Union[Tuple[float, float], List[float]]
Vector = Point
PointList = Union[Tuple[Point, ...], List[Point]]
