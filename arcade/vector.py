from typing import Union
import math

from arcade.arcade_types import Point


class Vector(list):
    def __init__(self, x: float = 0, y: float = 0):
        self.append(x)
        self.append(y)

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    # TODO: add __copy__ medhod

    @property
    def magnitude_sq(self) -> float:
        return self.x**2 + self.y**2

    @property
    def magnitude(self) -> float:
        return math.sqrt(self.magnitude_sq)

    @magnitude.setter
    def magnitude(self, value: float):
        if value < 0:
            raise ValueError("Magnitudes cannot be negative.")
        self.normalize()
        self.x *= value
        self.y *= value

    @property
    def heading_radians(self) -> float:
        return math.atan2(self.y, self.x)

    @property
    def heading(self) -> float:
        return math.degrees(self.heading_radians)

    def normalize(self) -> 'Vector':
        """Normalizes Vector magnitude scaled to 1.0"""
        mag = self.magnitude

        try:
            self.x = self.x / mag
            self.y = self.y / mag
        except ZeroDivisionError:
            pass
        return self

    # TODO: create normalized() method

    def rotate_radians(self, radians: float):
        x, y = self[0], self[1]
        self.x = x * math.cos(radians) - y * math.sin(radians)
        self.y = x * math.sin(radians) + y * math.cos(radians)
        return self

    def rotate(self, degrees: float):
        """Rotates Vector in degrees"""
        return self.rotate_radians(math.radians(degrees))

    def limit(self, magnitude_limit: float):
        if self.magnitude > magnitude_limit:
            self.magnitude = magnitude_limit
        return self

    @staticmethod
    def from_angle_radians(radians: float) -> 'Vector':
        v = Vector(1, 0)
        v.rotate_radians(radians)
        return v

    @staticmethod
    def from_angle(degrees: float) -> 'Vector':
        """Get a new Vector object pointed toward a particular angle.
        Args:
            degrees: Angle in degrees

        Returns:
            Normalized Vector with heading matching angle.
        """
        return Vector.from_angle_radians(math.radians(degrees))

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x={self.x}, y={self.y})"

    def __eq__(self, other: Union['Vector', Point]) -> bool:
        return self.x == other[0] and self.y == other[1]

    def __add__(self, other: Union['Vector', Point]) -> 'Vector':
        return Vector(self.x + other[0], self.y + other[1])

    def __iadd__(self, other: Union['Vector', Point]) -> 'Vector':
        """In-place add vectors, allowing for `sprite.positon += sprite.velocity`

        The method must return a new Vector because if the Vector is modified
        in-place, `Sprite._set_position` new_value argument is the sprites very 
        own position vector object.

        sprite.position += sprite.velocity
            (equivalent to)
        sprite.position = sprite.position + sprite.velocity
                |                 /            /
                |         Updates vector object directltly via the Vector class
                |       /
            calls the sprite._set_position(new_value=returned vector computed above)

            If the new value modified in place, the method's if statement will be checking
            an already changed vector. `new_value` is actually the sprites very own position
            vector object.
        """
        return Vector(self.x + other[0], self.y + other[1])

    def __sub__(self, other: Union['Vector', Point]) -> 'Vector':
        return Vector(self.x - other[0], self.y - other[1])

    def __isub__(self, other: Union['Vector', Point]) -> 'Vector':
        """In-place subtraction. Returns new Vector, see __iadd__ note"""
        return Vector(self.x - other[0], self.y - other[1])

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
