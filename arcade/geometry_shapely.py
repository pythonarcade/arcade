"""
Functions for calculating geometry.
"""

from shapely import speedups  # type: ignore
from shapely.geometry import Polygon, Point  # type: ignore

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
