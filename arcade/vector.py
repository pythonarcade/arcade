from typing import Union
import math

from arcade.arcade_types import Point


class Vector:
    __slots__ = ['x', 'y']

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    # TODO: add __copy__ medhod

    def normalize(self) -> 'Vector':
        """Normalizes Vector magnitude scaled to 1.0"""
        mag = self.magnitude

        try:
            self.x = self.x / mag
            self.y = self.y / mag
        except ZeroDivisionError:
            pass
        return self

    @property
    def magnitude_sq(self):
        return self.x**2 + self.y**2

    @property
    def magnitude(self):
        return math.sqrt(self.magnitude_sq)

    # TODO: implement set_magnitude?
    # TODO: implement limit
    # TODO: implement static from_angle and from_angle_radians

    @property
    def heading_radians(self) -> float:
        return math.atan2(self.y, self.x)

    @property
    def heading(self) -> float:
        return math.degrees(self.heading_radians)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x={self.x}, y={self.y})"

    def __getitem__(self, item) -> float:
        key = self.__slots__[item]
        return getattr(self, key)

    def __setitem__(self, index: int, value: float):
        d = dict(enumerate(self.__slots__))
        setattr(self, d[index], value)

    def __eq__(self, other: Union['Vector', Point]) -> bool:
        return self.x == other[0] and self.y == other[1]

    def __add__(self, other: Union['Vector', Point]) -> 'Vector':
        return Vector(self.x + other[0], self.y + other[1])

    def __iadd__(self, other: Union['Vector', Point]) -> 'Vector':
        self.x += other[0]
        self.y += other[1]
        return self

    def __sub__(self, other: Union['Vector', Point]) -> 'Vector':
        return Vector(self.x - other[0], self.y - other[1])

    def __isub__(self, other: Union['Vector', Point]) -> 'Vector':
        self.x -= other[0]
        self.y -= other[1]
        return self

    def __mul__(self, other: Union['Vector', Point, float]) -> 'Vector':
        try:
            return Vector(self.x * other[0], self.y * other[1])
        except TypeError:
            return Vector(self.x * other, self.y * other)

    __rmul__ = __mul__

    def __imul__(self, other: Union['Vector', Point, float]) -> 'Vector':
        try:
            self.x *= other[0]
            self.y *= other[1]
        except TypeError:
            self.x *= other
            self.y *= other
        return self

    def __truediv__(self, other: Union['Vector', Point, float]) -> 'Vector':
        try:
            return Vector(self.x / other[0], self.y / other[1])
        except TypeError:
            return Vector(self.x / other, self.y / other)

    def __itruediv__(self, other):
        try:
            self.x /= other[0]
            self.y /= other[1]
        except TypeError:
            self.x /= other
            self.y /= other
        return self

    def __rtruediv__(self, other):
        try:
            return Vector(other[0] / self.x, other[1] / self.y)
        except TypeError:
            return Vector(other / self.x, other / self.y)
