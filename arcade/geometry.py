"""
Functions for handling collisions with geometry.

These are the pure python versions of the functions.

Point in polygon function from https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/
"""
from __future__ import annotations

from arcade.types import Point, PointList


def are_polygons_intersecting(poly_a: PointList, poly_b: PointList) -> bool:
    """
    Return True if two polygons intersect.

    :param poly_a: List of points that define the first polygon.
    :param poly_b: List of points that define the second polygon.
    :Returns: True or false depending if polygons intersect
    """
    #if either are [], they don't intersect
    if not poly_a or not poly_b:
        return False
    for polygon in (poly_a, poly_b):

        for i1 in range(len(polygon)):
            i2 = (i1 + 1) % len(polygon)
            projection_1 = polygon[i1]
            projection_2 = polygon[i2]

            normal = (projection_2[1] - projection_1[1],
                      projection_1[0] - projection_2[0])

            min_a, min_b = (float("inf"),) * 2
            max_a, max_b = (-float("inf"),) * 2

            for poly in poly_a:
                projected = normal[0] * poly[0] + normal[1] * poly[1]

                if projected < min_a:
                    min_a = projected
                if projected > max_a:
                    max_a = projected

            for poly in poly_b:
                projected = normal[0] * poly[0] + normal[1] * poly[1]

                if projected < min_b:
                    min_b = projected
                if projected > max_b:
                    max_b = projected

            # Avoid typing.cast() because this is a very hot path
            if max_a <= min_b or max_b <= min_a:  # type: ignore
                return False

    return True

def is_point_in_box(p: Point, q: Point, r: Point) -> bool:
    """
    Return True if point q is inside the box defined by p and r.

    :param p: Point 1
    :param q: Point 2
    :param r: Point 3
    :Returns: True or false depending if points are collinear
    """
    return (
        (q[0] <= max(p[0], r[0]))
        and (q[0] >= min(p[0], r[0]))
        and (q[1] <= max(p[1], r[1]))
        and (q[1] >= min(p[1], r[1]))
    )


# NOTE: Should be named are_point_in_box
def get_triangle_orientation(p: Point, q: Point, r: Point) -> int:
    """
    Find the orientation of a triangle defined by (p, q, r)

    The function returns following integer values
      * 0 --> p, q and r are collinear
      * 1 --> Clockwise
      * 2 --> Counterclockwise

    :param p: Point 1
    :param q: Point 2
    :param r: Point 3
    :Returns: 0, 1, or 2 depending on orientation
    """
    val = ((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1]))

    if val == 0:
        return 0  # collinear
    if val > 0:
        return 1  # clockwise
    else:
        return 2  # counter-clockwise


def are_lines_intersecting(p1: Point, q1: Point, p2: Point, q2: Point) -> bool:
    """
    Given two lines defined by points p1, q1 and p2, q2, the function
    returns true if the two lines intersect.

    :param p1: Point 1
    :param q1: Point 2
    :param p2: Point 3
    :param q2: Point 4
    :Returns: True or false depending if lines intersect
    """
    o1 = get_triangle_orientation(p1, q1, p2)
    o2 = get_triangle_orientation(p1, q1, q2)
    o3 = get_triangle_orientation(p2, q2, p1)
    o4 = get_triangle_orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases
    # p1, q1 and p2 are collinear and p2 lies on segment p1q1
    if (o1 == 0) and is_point_in_box(p1, p2, q1):
        return True

    # p1, q1 and p2 are collinear and q2 lies on segment p1q1
    if (o2 == 0) and is_point_in_box(p1, q2, q1):
        return True

    # p2, q2 and p1 are collinear and p1 lies on segment p2q2
    if (o3 == 0) and is_point_in_box(p2, p1, q2):
        return True

    # p2, q2 and q1 are collinear and q1 lies on segment p2q2
    if (o4 == 0) and is_point_in_box(p2, q1, q2):
        return True

    return False


def is_point_in_polygon(x: float, y: float, polygon: PointList) -> bool:
    """
    Checks if a point is inside a polygon of three or more points.

    :param x: X coordinate of point
    :param y: Y coordinate of point
    :param polygon_point_list: List of points that define the polygon.
    :Returns: True or false depending if point is inside polygon
    """
    p = x, y
    n = len(polygon)

    # There must be at least 3 vertices
    # in polygon
    if n < 3:
        return False

    # Create a point for line segment
    # from p to infinite
    extreme = (10000, p[1])

    # To count number of points in polygon
    # whose y-coordinate is equal to
    # y-coordinate of the point
    decrease = 0
    count = i = 0

    while True:
        next_item = (i + 1) % n

        if polygon[i][1] == p[1]:
            decrease += 1

        # Check if the line segment from 'p' to
        # 'extreme' intersects with the line
        # segment from 'polygon[i]' to 'polygon[next]'
        if are_lines_intersecting(polygon[i], polygon[next_item], p, extreme):
            # If the point 'p' is collinear with line
            # segment 'i-next', then check if it lies
            # on segment. If it lies, return true, otherwise false
            if get_triangle_orientation(polygon[i], p, polygon[next_item]) == 0:
                return not is_point_in_box(
                    polygon[i],
                    p,
                    polygon[next_item],
                )

            count += 1

        i = next_item

        if i == 0:
            break

    # Reduce the count by decrease amount
    # as these points would have been added twice
    count -= decrease

    # Return true if count is odd, false otherwise
    return count % 2 == 1

