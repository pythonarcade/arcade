from typing import Tuple
from typing import List
from typing import Union


Color = Union(Tuple[int, int, int], Tuple[int, int, int, int], List[int, int, int], List[int, int, int, int])
Point = Union(Tuple[int, int], List[int, int])
PointList = Union(Tuple[Point, ...], List[Point, ...])
