"""
Functions for checking collisions with geometry.

These are the shapely versions of the functions.
"""
from shapely.geometry import Polygon, Point  # type: ignore
# The speedups module was deprecated in Shapely 2.0 and will be removed in the future
try:
    from shapely import speedups  # type: ignore
    speedups.enable()
except ImportError:
    pass

from arcade.types import PointList


def are_polygons_intersecting(poly_a: PointList, poly_b: PointList) -> bool:
    """
    Return True if two polygons intersect.

    The polygons can have 3 or more points and can be concave or convex.

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


def is_point_in_polygon(x: float, y: float, polygon: PointList) -> bool:
    """
    Use ray-tracing to see if point is inside a polygon

    :param float x: X coordinate of point
    :param float y: Y coordinate of point
    :param PointList polygon_point_list: List of points that define the polygon.
    :Returns: True or false depending if point is in polygon
    """
    shapely_point = Point(x, y)
    shapely_polygon = Polygon(polygon)

    return shapely_polygon.contains(shapely_point)
