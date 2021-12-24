"""
Functions for calculating geometry.
"""

from typing import cast

from arcade import PointList


_PRECISION = 2


def are_polygons_intersecting(poly_a: PointList,
                              poly_b: PointList) -> bool:
    """
    Return True if two polygons intersect.

    :param PointList poly_a: List of points that define the first polygon.
    :param PointList poly_b: List of points that define the second polygon.
    :Returns: True or false depending if polygons intersect

    :rtype bool:
    """

    for polygon in (poly_a, poly_b):

        for i1 in range(len(polygon)):
            i2 = (i1 + 1) % len(polygon)
            projection_1 = polygon[i1]
            projection_2 = polygon[i2]

            normal = (projection_2[1] - projection_1[1],
                      projection_1[0] - projection_2[0])

            min_a, max_a, min_b, max_b = (None,) * 4

            for poly in poly_a:
                projected = normal[0] * poly[0] + normal[1] * poly[1]

                if min_a is None or projected < min_a:
                    min_a = projected
                if max_a is None or projected > max_a:
                    max_a = projected

            for poly in poly_b:
                projected = normal[0] * poly[0] + normal[1] * poly[1]

                if min_b is None or projected < min_b:
                    min_b = projected
                if max_b is None or projected > max_b:
                    max_b = projected

            if cast(float, max_a) <= cast(float, min_b) or cast(float, max_b) <= cast(float, min_a):
                return False

    return True


def is_point_in_polygon(x, y, polygon_point_list):
    """
    Use ray-tracing to see if point is inside a polygon

    Args:
        x:
        y:
        polygon_point_list:

    Returns: bool

    """
    n = len(polygon_point_list)
    inside = False
    if n == 0:
        return False

    p1x, p1y = polygon_point_list[0]
    for i in range(n + 1):
        p2x, p2y = polygon_point_list[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    # noinspection PyUnboundLocalVariable
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside
