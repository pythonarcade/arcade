"""
Functions for calculating geometry.
"""

from typing import cast
from arcade import PointList,Point
import math

_PRECISION = 2

def point_list_to_segments_list(polygon: PointList):
    return [(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))]

def get_triangle_orientation(p1:Point,p2:Point,p3:Point):
    """
    :returns whether the given triangle is right oriented +1 or left oriented -1.
    if the triangle is flat (area is 0) than returns a tuple (0,True/False), where the second part of the tuple it True if p3 is between p1 and p2.
    """
    area = (p2[1]-p1[1])*(p3[0]-p2[0]) - (p2[0]-p1[0])*(p3[1]-p2[1])
    if area > 0:
        return 1
    if area < 0:
        return -1
    if area == 0:
        # if the triangle is flat, we distinguish between a triangle that self intersects and a triangle that doesn't self intersect.
        if max(p1[0], p2[0]) >= p3[0] >= min(p1[0], p2[0]) \
                and max(p1[1], p2[1]) >= p3[1] >= min(p1[1], p2[1]):
            # flat and self intersects
            return (0,True)
        else:
            # flat and not self intersects
            return (0,False)

def are_polygons_intersecting(poly_a: PointList,
                              poly_b: PointList) -> bool:
    """
    Return True if two polygons intersect.

    :param PointList poly_a: List of points that define the first polygon.
    :param PointList poly_b: List of points that define the second polygon.
    :Returns: True or false depending if polygons intersect

    :rtype bool:
    """
    # check if the line segments that compose the polygons exterior intersect
    segments_a = point_list_to_segments_list(poly_a)
    segments_b = point_list_to_segments_list(poly_b)

    for line_a in segments_a:
        for line_b in segments_b:
            # line segments a and b intersect iff the orientations of the following partial triangles are opposite in the following way: o1 != o2 and o3 != o4
            # or in the degenerate case where the triangles are flat (area equals 0), the lines intersect if the third point lies inside the segment.
            o1 = get_triangle_orientation(line_a[0], line_a[1], line_b[0])
            o2 = get_triangle_orientation(line_a[0], line_a[1], line_b[1])
            o3 = get_triangle_orientation(line_b[0], line_b[1], line_a[0])
            o4 = get_triangle_orientation(line_b[0], line_b[1], line_a[1])
            if o1 == (0,True) or o2 == (0,True) or o3 == (0,True) or o4 == (0,True):
                return True
            if o1 == (0,False) or o2 == (0,False) or o3 == (0,False) or o4 == (0,False):
                continue
            if o1 != o2 and o3 != o4:
                return True

    # if got here than no segment intersection was found.
    # the only option left for the polygons to be colliding is if one is inside the other.
    # we check this by tacking some point in one polygon and checking if it is inside the other.
    if is_point_in_polygon(*poly_a[0],poly_b) or is_point_in_polygon(*poly_b[0], poly_a):
        return True
    else:
        return False

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
    for i in range(n+1):
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


def get_distance(x1: float, y1: float, x2: float, y2: float):
    """ Get the distance between two points. """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
