import math
import random
from arcade.arcade_types import Point, Vector


def lerp(v1: float, v2: float, u: float) -> float:
    """linearly interpolate between two values"""
    return v1 + ((v2 - v1) * u)


def lerp_vec(v1: Vector, v2: Vector, u: float) -> Vector:
    return (
        lerp(v1[0], v2[0], u),
        lerp(v1[1], v2[1], u)
    )


def rand_in_rect(bottom_left: Point, width: float, height: float) -> Point:
    return (
        random.uniform(bottom_left[0], bottom_left[0] + width),
        random.uniform(bottom_left[1], bottom_left[1] + height)
    )


def rand_in_circle(center: Point, radius: float):
    """
    Generate a point in a circle, or can think of it as a vector pointing
    a random direction with a random magnitude <= radius
    Reference: http://stackoverflow.com/a/30564123
    Note: This algorithm returns a higher concentration of points around the center of the circle
    """
    # random angle
    angle = 2 * math.pi * random.random()
    # random radius
    r = radius * random.random()
    # calculating coordinates
    return (
        r * math.cos(angle) + center[0],
        r * math.sin(angle) + center[1]
    )


def rand_on_circle(center: Point, radius: float) -> Point:
    """Note: by passing a random value in for float, you can achieve what rand_in_circle() does"""
    angle = 2 * math.pi * random.random()
    return (
        radius * math.cos(angle) + center[0],
        radius * math.sin(angle) + center[1]
    )


def rand_on_line(pos1: Point, pos2: Point) -> Point:
    u = random.uniform(0.0, 1.0)
    return lerp_vec(pos1, pos2, u)


def rand_angle_360_deg():
    return random.uniform(0.0, 360.0)


def rand_angle_spread_deg(angle: float, half_angle_spread: float) -> float:
    s = random.uniform(-half_angle_spread, half_angle_spread)
    return angle + s


def rand_vec_spread_deg(angle: float, half_angle_spread: float, length: float) -> Vector:
    a = rand_angle_spread_deg(angle, half_angle_spread)
    vel = _Vec2.from_polar(a, length)
    return vel.as_tuple()


def rand_vec_magnitude(angle: float, lo_magnitude: float, hi_magnitude: float) -> Vector:
    mag = random.uniform(lo_magnitude, hi_magnitude)
    vel = _Vec2.from_polar(angle, mag)
    return vel.as_tuple()


class _Vec2:
    """
    2D vector used to do operate points and vectors

    Note: intended to be used for internal implementations only. Should not be part of public interfaces
    (ex: function parameters or return values).
    """

    __slots__ = ['x', 'y']

    def __init__(self, x, y=None):
        try:
            # see if first argument is an iterable with two items
            self.x = x[0]
            self.y = x[1]
        except TypeError:
            self.x = x
            self.y = y

    @staticmethod
    def from_polar(angle, radius):
        rads = math.radians(angle)
        return _Vec2(radius * math.cos(rads), radius * math.sin(rads))

    def __add__(self, other):
        return _Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return _Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return _Vec2(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        return _Vec2(self.x / other.x, self.y / other.y)

    def __iter__(self):
        yield self.x
        yield self.y

    def length(self):
        """return the length (magnitude) of the vector"""
        return math.sqrt(self.x**2 + self.y**2)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def __repr__(self):
        return f"Vec2({self.x},{self.y})"

    def rotated(self, angle):
        """Returns the new vector resulting when this vector is rotated by the given angle in degrees"""
        rads = math.radians(angle)
        cosine = math.cos(rads)
        sine = math.sin(rads)
        return _Vec2(
            (self.x*cosine) - (self.y*sine),
            (self.y*cosine) + (self.x*sine)
        )

    def as_tuple(self) -> Point:
        return self.x, self.y
