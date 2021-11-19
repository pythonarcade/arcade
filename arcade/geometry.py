"""
Functions for calculating geometry.
"""

import math

from shapely import speedups  # type: ignore
from shapely.geometry import Polygon, Point  # type: ignore
from typing import List

from arcade import PointList

_PRECISION = 2

speedups.enable()


def are_polygons_intersecting(poly_a: PointList,
                              poly_b: PointList) -> bool:
    """
    Return True if two polygons intersect.

    :param PointList poly_a: List of points that define the first polygon.
    :param PointList poly_b: List of points that define the second polygon.
    :Returns: True or false depending if polygons intersect

    :rtype bool:
    """

    shapely_polygon_a = Polygon(poly_a)
    shapely_polygon_b = Polygon(poly_b)

    r2 = False
    r1 = shapely_polygon_a.intersects(shapely_polygon_b)
    if r1:
        r2 = shapely_polygon_a.touches(shapely_polygon_b)
    return r1 and not r2


def is_point_in_polygon(x: float, y: float, polygon_point_list) -> bool:
    """
    Use ray-tracing to see if point is inside a polygon

    Args:
        x:
        y:
        polygon_point_list:

    Returns: bool

    """
    shapely_point = Point(x, y)
    shapely_polygon = Polygon(polygon_point_list)

    return shapely_polygon.contains(shapely_point)


def get_distance(x1: float, y1: float, x2: float, y2: float):
    """ Get the distance between two points. """
    return math.hypot(x1 - x2, y1 - y2)


def clamp(a, low, high):
    """ Clamp a number between a range. """
    if a > high:
        return high
    elif a < low:
        return low
    else:
        return a


def rotate_point(x: float, y: float, cx: float, cy: float,
                 angle_degrees: float) -> List[float]:
    """
    Rotate a point around a center.

    :param x: x value of the point you want to rotate
    :param y: y value of the point you want to rotate
    :param cx: x value of the center point you want to rotate around
    :param cy: y value of the center point you want to rotate around
    :param angle_degrees: Angle, in degrees, to rotate
    :return: Return rotated (x, y) pair
    :rtype: (float, float)
    """
    temp_x = x - cx
    temp_y = y - cy

    # now apply rotation
    angle_radians = math.radians(angle_degrees)
    cos_angle = math.cos(angle_radians)
    sin_angle = math.sin(angle_radians)
    rotated_x = temp_x * cos_angle - temp_y * sin_angle
    rotated_y = temp_x * sin_angle + temp_y * cos_angle

    # translate back
    rounding_precision = 2
    x = round(rotated_x + cx, rounding_precision)
    y = round(rotated_y + cy, rounding_precision)

    return [x, y]
