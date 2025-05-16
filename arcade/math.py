import math
import random
from typing import TypeVar

from pyglet.math import Vec2, Vec3

from arcade.types import AsFloat, HasAddSubMul, Point, Point2, SupportsRichComparison
from arcade.types.rect import Rect
from arcade.types.vector_like import Point3

_PRECISION = 2


__all__ = [
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
    "quaternion_rotation",
]

SupportsRichComparisonT = TypeVar("SupportsRichComparisonT", bound=SupportsRichComparison)


def clamp(
    a: SupportsRichComparisonT, low: SupportsRichComparisonT, high: SupportsRichComparisonT
) -> SupportsRichComparisonT:
    """Clamp a number between a range.

    Args:
        a (float): The number to clamp
        low (float): The lower bound
        high (float): The upper bound
    """
    # Python will deal with > unsupported by falling back on <.
    return high if a > high else max(a, low)  # type: ignore


# This TypeVar helps match v1 and v2 as the same type below in lerp's
# signature. If we used HasAddSubMul, they could be different.
L = TypeVar("L", bound=HasAddSubMul)


def lerp(v1: L, v2: L, u: float) -> L:
    """Linearly interpolate two values which support arithmetic operators.

    Both ``v1`` and ``v2`` must be of compatible types and support
    the following operators:

    * ``+`` (:py:meth:`~object.__add__`)
    * ``-`` (:py:meth:`~object.__sub__`)
    * ``*`` (:py:meth:`~object.__mul__`)

    This means that in certain cases, you may want to use another
    function:

    * For angles, use :py:func:`lerp_angle`.
    * To convert points as arbitary sequences, use:

      * :py:func:`lerp_2d`
      * :py:func:`lerp_3d`

    Args:
        v1 (HasAddSubMul): The first value
        v2 (HasAddSubMul): The second value
        u: The interpolation value `(0.0 to 1.0)`
    """
    return v1 + ((v2 - v1) * u)


def lerp_2d(v1: Point2, v2: Point2, u: float) -> Vec2:
    """Linearly interpolate between two 2D points passed as sequences.

    .. tip:: This function returns a :py:class:`Vec2` you can use
             with :py:func`lerp` .

    Args:
        v1: The first point as a sequence of 2 values.
        v2: The second point as a sequence of 2 values.
        u (float): The interpolation value `(0.0 to 1.0)`
    """
    return Vec2(lerp(v1[0], v2[0], u), lerp(v1[1], v2[1], u))


def lerp_3d(v1: Point3, v2: Point3, u: float) -> Vec3:
    """Linearly interpolate between two 3D points passed as sequences.

    .. tip:: This function returns a :py:class:`Vec3` you can use
             with :py:func`lerp`.

    Args:
        v1: The first point as a sequence of 3 values.
        v2: The second point as a sequence of 3 values.
        u (float): The interpolation value `(0.0 to 1.0)`
    """
    return Vec3(lerp(v1[0], v2[0], u), lerp(v1[1], v2[1], u), lerp(v1[2], v2[2], u))


def smerp(v1: L, v2: L, dt: float, h: float) -> L:
    """
    Smoothly interpolate between two values indepentdant of time.
    use as `a = smerp(a, b, delta_time, 16)`.

    .. tip:: To find the ideal decay constant (half-life) you can use:
             `h = -t / math.log2(p)` where p is how close (percentage) you'd like to be
             to the target value in t seconds.
             i.e if in 1 second you'd like to be within 1% then h ~= 0.15051

    Args:
        v1: The first value to interpolate from.
        v2: The second value to interpolate to.
        dt: The time in seconds that has passed since v1 was interpolated last
        h: The decay constant. The higher the faster v1 reaches v2.
           0.1-25.0 is a good range.
    """

    return v2 + (v1 - v2) * math.pow(2.0, -dt / h)


def smerp_2d(v1: Point2, v2: Point2, dt: float, h: float) -> Vec2:
    """
    Smoothly interpolate between two sequences of length 2 indepentdant of time.
    use as `a = smerp_2d(a, b, delta_time, 16)`.

    .. tip:: To find the ideal decay constant (half-life) you can use:
             `h = -t / math.log2(p)` where p is how close (percentage) you'd like to be
             to the target value in t seconds.
             i.e if in 1 second you'd like to be within 1% then h ~= 0.15051

    .. tip::  This function returns a :py:class:`Vec2` you can use
             with :py:func`smerp`.

    Args:
        v1: The first value to interpolate from.
        v2: The second value to interpolate to.
        dt: The time in seconds that has passed since v1 was interpolated last
        h: The decay constant. The lower the faster v1 reaches v2.
           0.1-25.0 is a good range.
    """
    x1, y1 = v1
    x2, y2 = v2
    d = math.pow(2.0, -dt / h)
    return Vec2(x2 + (x1 - x2) * d, y2 + (y1 - y2) * d)


def smerp_3d(v1: Point3, v2: Point3, dt: float, h: float) -> Vec3:
    """
    Smoothly interpolate between two sequences of length 3 indepentdant of time.
    use as `a = smerp_3d(a, b, delta_time, 16)`.

    .. tip:: To find the ideal decay constant (half-life) you can use:
             `h = -t / math.log2(p)` where p is how close (percentage) you'd like to be
             to the target value in t seconds.
             i.e if in 1 second you'd like to be within 1% then h ~= 0.15051

    .. tip::  This function returns a :py:class:`Vec3` you can use
             with :py:func`smerp`.

    Args:
        v1: The first value to interpolate from.
        v2: The second value to interpolate to.
        dt: The time in seconds that has passed since v1 was interpolated last
        h: The decay constant. The higher the faster v1 reaches v2.
           0.1-25.0 is a good range.
    """
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    d = math.pow(2.0, -dt / h)
    return Vec3(x2 + (x1 - x2) * d, y2 + (y1 - y2) * d, z2 + (z1 - z2) * d)


def lerp_angle(start_angle: float, end_angle: float, u: float) -> float:
    """
    Linearly interpolate between two angles in degrees,
    following the shortest path.

    Args:
        start_angle (float): The starting angle
        end_angle (float): The ending angle
        u (float): The interpolation value (0.0 to 1.0)
    """
    start_angle %= 360
    end_angle %= 360

    while start_angle - end_angle > 180:
        end_angle += 360

    while start_angle - end_angle < -180:
        end_angle -= 360

    return lerp(start_angle, end_angle, u) % 360


def rand_in_rect(rect: Rect) -> Point2:
    """
    Calculate a random point in a rectangle.

    Args:
        rect (Rect): The rectangle to calculate the point in.
    """
    return (
        random.uniform(rect.left, rect.right),
        random.uniform(rect.bottom, rect.top),
    )


def rand_in_circle(center: Point2, radius: float) -> Point2:
    """
    Generate a point in a circle, or can think of it as a vector pointing
    a random direction with a random magnitude <= radius.

    Reference: https://stackoverflow.com/a/50746409

    Args:
        center (Point2): The center of the circle
        radius (float): The radius of the circle
    """
    # random angle
    angle = 2 * math.pi * random.random()
    # random radius
    r = radius * math.sqrt(random.random())
    # calculating coordinates
    return r * math.cos(angle) + center[0], r * math.sin(angle) + center[1]


def rand_on_circle(center: Point2, radius: float) -> Point2:
    """
    Generate a point on a circle.

    Args:
        center (Point2): The center of the circle
        radius (float): The radius of the circle
    """
    angle = 2 * math.pi * random.random()
    return radius * math.cos(angle) + center[0], radius * math.sin(angle) + center[1]


def rand_on_line(pos1: Point2, pos2: Point2) -> Point:
    """
    Given two points defining a line, return a random point on that line.

    Args:
        pos1 (Point2): The first point
        pos2 (Point2): The second point
    """
    u = random.uniform(0.0, 1.0)
    return lerp_2d(pos1, pos2, u)


def rand_angle_360_deg() -> float:
    """
    Returns a random angle in degrees between 0.0 and 360.0.
    """
    return random.uniform(0.0, 360.0)


def rand_angle_spread_deg(angle: float, half_angle_spread: float) -> float:
    """
    Returns a random angle in degrees, within a spread of the given angle.

    Args:
        angle (float): The angle to spread from
        half_angle_spread (float): The half angle spread
    """
    s = random.uniform(-half_angle_spread, half_angle_spread)
    return angle + s


def rand_vec_spread_deg(angle: float, half_angle_spread: float, length: float) -> Point2:
    """
    Returns a random vector, within a spread of the given angle.

    Args:
        angle (float): The angle to spread from
        half_angle_spread (float): The half angle spread
        length (float): The length of the vector
    """
    a = rand_angle_spread_deg(angle, half_angle_spread)
    vel = Vec2.from_polar(a, length)
    return vel.x, vel.y


def rand_vec_magnitude(
    angle: float,
    lo_magnitude: float,
    hi_magnitude: float,
) -> Point2:
    """
    Return a vector of randomized magnitude pointing in the given direction.

    Args:
        angle (float): The vector angle in radians
        lo_magnitude (float): The lower magnitude
        hi_magnitude (float): The higher magnitude
    """
    mag = random.uniform(lo_magnitude, hi_magnitude)
    vel = Vec2.from_polar(angle, mag)
    return vel.x, vel.y


def get_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Get the distance between two points.

    Args:
        x1 (float): x coordinate of the first point
        y1 (float): y coordinate of the first point
        x2 (float): x coordinate of the second point
        y2 (float): y coordinate of the second point
    """
    return math.hypot(x1 - x2, y1 - y2)


def rotate_point(
    x: float,
    y: float,
    cx: float,
    cy: float,
    angle_degrees: float,
) -> Point2:
    """
    Rotate a point around a center.

    Args:
        x (float): x value of the point you want to rotate
        y (float): y value of the point you want to rotate
        cx (float): x value of the center point you want to rotate around
        cy (float): y value of the center point you want to rotate around
        angle_degrees (float): Angle, in degrees, to rotate
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


# scale around point


def rescale_relative_to_point(source: Point2, target: Point2, factor: AsFloat | Point2) -> Point2:
    """
    Calculate where a point should be when scaled by the factor realtive to the source point.

    Args:
        source: Where to scaled from.
        target: The point being scaled.
        factor: How much to scale by. If factor is less than one, target approaches source.
                Otherwise it moves away. A factor of zero returns source.

    Returns:
        The rescaled point.
    """

    if isinstance(factor, float | int):
        if factor == 1.0:
            return target
        scale_x = scale_y = factor
    else:
        try:
            scale_x, scale_y = factor
            if scale_x == 1.0 and scale_y == 1.0:
                return target
        except ValueError:
            raise ValueError(
                "factor must be a float, int, or tuple-like which unpacks as two float-like values"
            )
        except TypeError:
            raise TypeError(
                "factor must be a float, int, or tuple-like unpacks as two float-like values"
            )

    dx = target[0] - source[0]
    dy = target[1] - source[1]

    return source[0] + dx * scale_x, source[1] + dy * scale_y


def rotate_around_point(source: Point2, target: Point2, angle: float):
    """
    Rotate a point around another point clockwise.

    Args:
        source: The point to rotate around
        target: The point to rotate
        angle: The degrees to rotate the target by.
    """

    if source == target or angle % 360.0 == 0.0:
        return target

    diff_x = target[0] - source[0]
    diff_y = target[1] - source[1]
    r = math.radians(angle)

    c, s = math.cos(r), math.sin(r)

    dx = diff_x * c - diff_y * s
    dy = diff_x * s + diff_y * c

    return target[0] + dx, target[1] + dy


def get_angle_degrees(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Get the angle in degrees between two points.

    Args:
        x1 (float): x coordinate of the first point
        y1 (float): y coordinate of the first point
        x2 (float): x coordinate of the second point
        y2 (float): y coordinate of the second point
    """
    x_diff = x2 - x1
    y_diff = y2 - y1
    return -math.degrees(math.atan2(y_diff, x_diff))


def get_angle_radians(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Get the angle in radians between two points.

    Args:
        x1 (float): x coordinate of the first point
        y1 (float): y coordinate of the first point
        x2 (float): x coordinate of the second point
        y2 (float): y coordinate of the second point
    """
    x_diff = x2 - x1
    y_diff = y2 - y1
    return math.atan2(x_diff, y_diff)


def quaternion_rotation(axis: Point3, vector: Point3, angle: float) -> tuple[float, float, float]:
    """
    Rotate a 3-dimensional vector of any length clockwise around a 3-dimensional unit
    length vector.

    This method of vector rotation is immune to rotation-lock, however it takes a little
    more effort to find the axis of rotation rather than 3 angles of rotation.
    Ref: https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html.

    Args:
        axis (tuple[float, float, float]): The unit length vector that will be rotated around
        vector (tuple[float, float, float]): The 3-dimensional vector to be rotated
        angle (float): The angle in degrees to rotate the vector clock-wise by
    """
    _rotation_rads = -math.radians(angle)
    p1, p2, p3 = vector
    a1, a2, a3 = axis
    _c2, _s2 = math.cos(_rotation_rads / 2.0), math.sin(_rotation_rads / 2.0)

    q0, q1, q2, q3 = _c2, _s2 * a1, _s2 * a2, _s2 * a3
    q0_2, q1_2, q2_2, q3_2 = q0**2, q1**2, q2**2, q3**2
    q01, q02, q03, q12, q13, q23 = q0 * q1, q0 * q2, q0 * q3, q1 * q2, q1 * q3, q2 * q3

    _x = p1 * (q0_2 + q1_2 - q2_2 - q3_2) + 2.0 * (p2 * (q12 - q03) + p3 * (q02 + q13))
    _y = p2 * (q0_2 - q1_2 + q2_2 - q3_2) + 2.0 * (p1 * (q03 + q12) + p3 * (q23 - q01))
    _z = p3 * (q0_2 - q1_2 - q2_2 + q3_2) + 2.0 * (p1 * (q13 - q02) + p2 * (q01 + q23))

    return _x, _y, _z
