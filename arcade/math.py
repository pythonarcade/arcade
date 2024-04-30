from __future__ import annotations

import math
import random
from typing import Sequence, Tuple, Union
from arcade.types import AsFloat, Point


_PRECISION = 2


__all__ = [
    "round_fast",
    "clamp",
    "lerp",
    "lerp_2d",
    "lerp_3d",
    "lerp_angle",
    "rand_in_rect",
    "rand_in_circle",
    "rand_on_circle",
    "rand_on_line",
    "rand_angle_360_deg",
    "rand_angle_spread_deg",
    "rand_vec_spread_deg",
    "rand_vec_magnitude",
    "get_distance",
    "rotate_point",
    "get_angle_degrees",
    "get_angle_radians",
    "quaternion_rotation"
]


def round_fast(value: float, precision: int) -> float:
    """
    A high performance version of python's built-in round() function.

    .. note:: This function is not as accurate as the built-in round() function.
              But is sufficient in some cases.

    Example::

        >>> round(3.5662457892, 1)
        3.6
        >>> round(3.5662457892, 2)
        3.57
        >>> round(3.5662457892, 3)
        3.566
        >>> round(3.5662457892, 4)
        3.5662

    :param value: The value to round
    :param precision: The number of decimal places to round to
    :return: The rounded value
    """
    precision = 10 ** precision
    return math.trunc(value * precision) / precision


def clamp(a, low: float, high: float) -> float:
    """ Clamp a number between a range. """
    return high if a > high else max(a, low)


V_2D = Union[Tuple[AsFloat, AsFloat], Sequence[AsFloat]]
V_3D = Union[Tuple[AsFloat, AsFloat, AsFloat], Sequence[AsFloat]]


def lerp(v1: AsFloat, v2: AsFloat, u: float) -> float:
    """linearly interpolate between two values"""
    return v1 + ((v2 - v1) * u)


def lerp_2d(v1: V_2D, v2: V_2D, u: float) -> Tuple[float, float]:
    return (
        lerp(v1[0], v2[0], u),
        lerp(v1[1], v2[1], u)
    )


def lerp_3d(v1: V_3D, v2: V_3D, u: float) -> Tuple[float, float, float]:
    return (
        lerp(v1[0], v2[0], u),
        lerp(v1[1], v2[1], u),
        lerp(v1[2], v2[2], u)
    )


def lerp_angle(start_angle: float, end_angle: float, u: float) -> float:
    """
    Linearly interpolate between two angles in degrees,
    following the shortest path.

    :param start_angle: The starting angle
    :param end_angle: The ending angle
    :param u: The interpolation value
    :return: The interpolated angle
    """
    start_angle %= 360
    end_angle %= 360

    while start_angle - end_angle > 180:
        end_angle += 360

    while start_angle - end_angle < -180:
        end_angle -= 360

    return lerp(start_angle, end_angle, u) % 360


def rand_in_rect(bottom_left: Point, width: float, height: float) -> Point:
    """
    Calculate a random point in a rectangle.

    :param bottom_left: The bottom left corner of the rectangle
    :param width: The width of the rectangle
    :param height: The height of the rectangle
    :return: A random point in the rectangle
    """
    return (
        random.uniform(bottom_left[0], bottom_left[0] + width),
        random.uniform(bottom_left[1], bottom_left[1] + height)
    )


def rand_in_circle(center: Point, radius: float) -> Point:
    """
    Generate a point in a circle, or can think of it as a vector pointing
    a random direction with a random magnitude <= radius.

    Reference: https://stackoverflow.com/a/30564123

    .. note:: This algorithm returns a higher concentration of points
              around the center of the circle

    :param center: The center of the circle
    :param radius: The radius of the circle
    :return: A random point in the circle
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
    """
    Generate a point on a circle.

    .. note: by passing a random value in for float,
             you can achieve what rand_in_circle() does

    :param center: The center of the circle
    :param radius: The radius of the circle
    :return: A random point on the circle
    """
    angle = 2 * math.pi * random.random()
    return (
        radius * math.cos(angle) + center[0],
        radius * math.sin(angle) + center[1]
    )


def rand_on_line(pos1: Point, pos2: Point) -> Point:
    """
    Given two points defining a line, return a random point on that line.

    :param pos1: The first point
    :param pos2: The second point
    :return: A random point on the line
    """
    u = random.uniform(0.0, 1.0)
    return lerp_2d(pos1, pos2, u)


def rand_angle_360_deg() -> float:
    """
    Returns a random angle in degrees.
    """
    return random.uniform(0.0, 360.0)


def rand_angle_spread_deg(angle: float, half_angle_spread: float) -> float:
    """
    Returns a random angle in degrees, within a spread of the given angle.

    :param angle: The angle to spread from
    :param half_angle_spread: The half angle spread
    :return: A random angle in degrees
    """
    s = random.uniform(-half_angle_spread, half_angle_spread)
    return angle + s


def rand_vec_spread_deg(
    angle: float,
    half_angle_spread: float,
    length: float
) -> tuple[float, float]:
    """
    Returns a random vector, within a spread of the given angle.

    :param angle: The angle to spread from
    :param half_angle_spread: The half angle spread
    :param length: The length of the vector
    :return: A random vector
    """
    a = rand_angle_spread_deg(angle, half_angle_spread)
    vel = _Vec2.from_polar(a, length)
    return vel.as_tuple()


def rand_vec_magnitude(
    angle: float,
    lo_magnitude: float,
    hi_magnitude: float,
) -> tuple[float, float]:
    """
    Returns a random vector, within a spread of the given angle.

    :param angle: The angle to spread from
    :param lo_magnitude: The lower magnitude
    :param hi_magnitude: The higher magnitude
    :return: A random vector
    """
    mag = random.uniform(lo_magnitude, hi_magnitude)
    vel = _Vec2.from_polar(angle, mag)
    return vel.as_tuple()


class _Vec2:
    """
    2D vector used to do operate points and vectors

    Note: intended to be used for internal implementations only.
    Should not be part of public interfaces
    (ex: function parameters or return values).
    """
    __slots__ = ['x', 'y']

    def __init__(self, x: float, y: float):
        # see if first argument is an iterable with two items
        self.x: float = x
        self.y: float = y

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

    def rotated(self, angle: float):
        """
        Returns the new vector resulting when this vector is
        rotated by the given angle in degrees
        """
        rads = math.radians(angle)
        cosine = math.cos(rads)
        sine = math.sin(rads)
        return _Vec2(
            (self.x * cosine) - (self.y * sine),
            (self.y * cosine) + (self.x * sine)
        )

    def as_tuple(self) -> Point:
        return self.x, self.y


def get_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Get the distance between two points.

    :param x1: x coordinate of the first point
    :param y1: y coordinate of the first point
    :param x2: x coordinate of the second point
    :param y2: y coordinate of the second point
    :return: Distance between the two points
    """
    return math.hypot(x1 - x2, y1 - y2)


def rotate_point(
    x: float,
    y: float,
    cx: float,
    cy: float,
    angle_degrees: float,
) -> Point:
    """
    Rotate a point around a center.

    :param x: x value of the point you want to rotate
    :param y: y value of the point you want to rotate
    :param cx: x value of the center point you want to rotate around
    :param cy: y value of the center point you want to rotate around
    :param angle_degrees: Angle, in degrees, to rotate
    :return: Return rotated (x, y) pair
    """
    temp_x = x - cx
    temp_y = y - cy

    # now apply rotation
    angle_radians = math.radians(angle_degrees)
    cos_angle = math.cos(angle_radians)
    sin_angle = math.sin(angle_radians)
    rotated_x = temp_x * cos_angle + temp_y * sin_angle
    rotated_y = -temp_x * sin_angle + temp_y * cos_angle

    # translate back
    x = round(rotated_x + cx, _PRECISION)
    y = round(rotated_y + cy, _PRECISION)

    return x, y


def get_angle_degrees(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Get the angle in degrees between two points.

    :param x1: x coordinate of the first point
    :param y1: y coordinate of the first point
    :param x2: x coordinate of the second point
    :param y2: y coordinate of the second point
    """
    x_diff = x2 - x1
    y_diff = y2 - y1
    return math.degrees(math.atan2(x_diff, y_diff))


def get_angle_radians(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Get the angle in radians between two points.

    :param x1: x coordinate of the first point
    :param y1: y coordinate of the first point
    :param x2: x coordinate of the second point
    :param y2: y coordinate of the second point
    """
    x_diff = x2 - x1
    y_diff = y2 - y1
    return math.atan2(x_diff, y_diff)


def quaternion_rotation(axis: Tuple[float, float, float],
                        vector: Tuple[float, float, float],
                        angle: float) -> Tuple[float, float, float]:
    """
    Rotate a 3-dimensional vector of any length clockwise around a 3-dimensional unit length vector.

    This method of vector rotation is immune to rotation-lock, however it takes a little more effort
    to find the axis of rotation rather than 3 angles of rotation.
    Ref: https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html.

    :param axis: The unit length vector that will be rotated around
    :param vector: The 3-dimensional vector to be rotated
    :param angle: The angle in degrees to rotate the vector clock-wise by
    :return: A rotated 3-dimension vector with the same length as the argument vector.
    """
    _rotation_rads = -math.radians(angle)
    p1, p2, p3 = vector
    _c2, _s2 = math.cos(_rotation_rads / 2.0), math.sin(_rotation_rads / 2.0)

    q0, q1, q2, q3 = _c2, _s2 * axis[0], _s2 * axis[1], _s2 * axis[2]
    q0_2, q1_2, q2_2, q3_2 = q0 ** 2, q1 ** 2, q2 ** 2, q3 ** 2
    q01, q02, q03, q12, q13, q23 = q0 * q1, q0 * q2, q0 * q3, q1 * q2, q1 * q3, q2 * q3

    _x = p1 * (q0_2 + q1_2 - q2_2 - q3_2) + 2.0 * (p2 * (q12 - q03) + p3 * (q02 + q13))
    _y = p2 * (q0_2 - q1_2 + q2_2 - q3_2) + 2.0 * (p1 * (q03 + q12) + p3 * (q23 - q01))
    _z = p3 * (q0_2 - q1_2 - q2_2 + q3_2) + 2.0 * (p1 * (q13 - q02) + p2 * (q01 + q23))

    return _x, _y, _z
