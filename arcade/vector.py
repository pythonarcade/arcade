from typing import Union
import math

from arcade.arcade_types import Point


class Vector:
    __slots__ = ['x', 'y']

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    @property
    def magnitude_sq(self):
        return self.x**2 + self.y**2

    @property
    def magnitude(self):
        return math.sqrt(self.magnitude_sq)

    @property
    def heading_radians(self) -> float:
        return math.atan2(self.y, self.x)

    @property
    def heading(self) -> float:
        return math.degrees(self.heading_radians)

    @staticmethod
    def normalize(vector: Union['Vector', Point]) -> 'Vector':
        """Returns a Vector whose magnitude is scaled to 1.0"""
        x, y = vector
        try:
            return Vector(
                x/max(abs(x), abs(y)),
                y/max(abs(x), abs(y))
            )
        except ZeroDivisionError:
            return Vector(0, 0)

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

    def __mul__(self, value: Union['Vector', Point, float]) -> 'Vector':
        try:
            return Vector(self.x * value[0], self.y * value[1])
        except TypeError:
            return Vector(self.x*value, self.y*value)

    def __imul__(self, value: Union['Vector', Point, float]) -> 'Vector':
        try:
            self.x *= value[0]
            self.y *= value[1]
        except TypeError:
            self.x *= value
            self.y *= value
        return self
