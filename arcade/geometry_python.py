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


# Point in polygon function from https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/

# Given three collinear points p, q, r,
# the function checks if point q lies
# on line segment 'pr'
def _on_segment(p: tuple, q: tuple, r: tuple) -> bool:
    if ((q[0] <= max(p[0], r[0])) & (q[0] >= min(p[0], r[0])) & (q[1] <= max(p[1], r[1])) & (q[1] >= min(p[1], r[1]))):
        return True

    return False


# To find orientation of ordered triplet (p, q, r).
# The function returns following values
# 0 --> p, q and r are collinear
# 1 --> Clockwise
# 2 --> Counterclockwise
def _orientation(p: tuple, q: tuple, r: tuple) -> int:
    val = (((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1])))

    if val == 0:
        return 0
    if val > 0:
        return 1  # Collinear
    else:
        return 2  # Clock or counterclock


def _do_intersect(p1, q1, p2, q2):
    # Find the four orientations needed for
    # general and special cases
    o1 = _orientation(p1, q1, p2)
    o2 = _orientation(p1, q1, q2)
    o3 = _orientation(p2, q2, p1)
    o4 = _orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases
    # p1, q1 and p2 are collinear and
    # p2 lies on segment p1q1
    if (o1 == 0) and (_on_segment(p1, p2, q1)):
        return True

    # p1, q1 and p2 are collinear and
    # q2 lies on segment p1q1
    if (o2 == 0) and (_on_segment(p1, q2, q1)):
        return True

    # p2, q2 and p1 are collinear and
    # p1 lies on segment p2q2
    if (o3 == 0) and (_on_segment(p2, p1, q2)):
        return True

    # p2, q2 and q1 are collinear and
    # q1 lies on segment p2q2
    if (o4 == 0) and (_on_segment(p2, q1, q2)):
        return True

    return False


# Returns true if the point p lies
# inside the polygon[] with n vertices
def is_point_in_polygon(x: float, y: float, polygon_point_list) -> bool:
    p = x, y
    n = len(polygon_point_list)

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

        if polygon_point_list[i][1] == p[1]:
            decrease += 1

        # Check if the line segment from 'p' to
        # 'extreme' intersects with the line
        # segment from 'polygon[i]' to 'polygon[next]'
        if (_do_intersect(polygon_point_list[i],
                          polygon_point_list[next_item],
                          p, extreme)):

            # If the point 'p' is collinear with line
            # segment 'i-next', then check if it lies
            # on segment. If it lies, return true, otherwise false
            if _orientation(polygon_point_list[i], p,
                            polygon_point_list[next_item]) == 0:
                return not _on_segment(polygon_point_list[i], p,
                                       polygon_point_list[next_item])

            count += 1

        i = next_item

        if i == 0:
            break

    # Reduce the count by decrease amount
    # as these points would have been added twice
    count -= decrease

    # Return true if count is odd, false otherwise
    return count % 2 == 1
