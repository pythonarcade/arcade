"""
Functions for handling collisions with geometry.

These are the pure python versions of the functions.

Point in polygon function from https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/
"""

from collections.abc import Iterable
from sys import maxsize as sys_int_maxsize

from arcade.types import Point2, Point2List


def are_polygons_intersecting(poly_a: Point2List, poly_b: Point2List) -> bool:
    """
    Check if two polygons intersect.

    Args:
        poly_a: List of points that define the first polygon.
        poly_b: List of points that define the second polygon.

    Returns:
        ``True`` if polygons intersect, ``False`` otherwise
    """
    # if either are [], they don't intersect
    if not poly_a or not poly_b:
        return False

    # Bounding box check. This also covers the x and y axes of the
    # separating axis test below.
    x_a, y_a = zip(*poly_a)
    x_b, y_b = zip(*poly_b)
    if max(x_a) <= min(x_b) or max(x_b) <= min(x_a) or max(y_a) <= min(y_b) or max(y_b) <= min(y_a):
        return False

    return _are_polygons_intersecting_sat(poly_a, poly_b)


def _are_polygons_intersecting_sat(poly_a: Point2List, poly_b: Point2List) -> bool:
    """
    Separating axis test for two polygons whose bounding boxes overlap.

    The caller must already have checked that the bounding boxes overlap.
    Horizontal and vertical edges are skipped because their axes are the
    x and y axes, which the bounding box check has already covered. This
    means two axis-aligned rectangles need no further work at all.

    Args:
        poly_a: List of points that define the first polygon.
        poly_b: List of points that define the second polygon.

    Returns:
        ``True`` if polygons intersect, ``False`` otherwise
    """
    for polygon in (poly_a, poly_b):
        prev_x, prev_y = polygon[-1]
        for x, y in polygon:
            normal_x = y - prev_y
            normal_y = prev_x - x
            prev_x = x
            prev_y = y

            # Axis-aligned or zero-length edge
            if normal_x == 0 or normal_y == 0:
                continue

            projected_a = [normal_x * px + normal_y * py for px, py in poly_a]
            projected_b = [normal_x * px + normal_y * py for px, py in poly_b]

            if max(projected_a) <= min(projected_b) or max(projected_b) <= min(projected_a):
                return False

    return True


def _are_polygons_overlapping_on_axes(
    poly_a: Point2List, poly_b: Point2List, axes: Iterable[Point2]
) -> bool:
    """
    Separating axis test for two polygons using a given set of axes.

    Like :py:func:`_are_polygons_intersecting_sat`, but the caller provides
    the axes to test, so they can be cached and duplicates removed.

    Args:
        poly_a: List of points that define the first polygon.
        poly_b: List of points that define the second polygon.
        axes: The axes to project onto. They don't need to be unit vectors.

    Returns:
        ``True`` if the polygons overlap on every axis, ``False`` otherwise
    """
    for normal_x, normal_y in axes:
        projected_a = [normal_x * px + normal_y * py for px, py in poly_a]
        projected_b = [normal_x * px + normal_y * py for px, py in poly_b]

        if max(projected_a) <= min(projected_b) or max(projected_b) <= min(projected_a):
            return False

    return True


def is_point_in_box(p: Point2, q: Point2, r: Point2) -> bool:
    """
    Checks if point ``q`` is inside the box defined by ``p`` and ``r``.

    Args:
        p (Point2): Start of box
        q (Point2): Point to check
        r (Point2): End of box

    Returns:
        ``True`` or ``False`` depending if point is in the box.
    """
    return (
        (q[0] <= max(p[0], r[0]))
        and (q[0] >= min(p[0], r[0]))
        and (q[1] <= max(p[1], r[1]))
        and (q[1] >= min(p[1], r[1]))
    )


def get_triangle_orientation(p: Point2, q: Point2, r: Point2) -> int:
    """
    Find the orientation of a triangle defined by (p, q, r)

    The function returns the following integer values:

      * 0 --> p, q, and r are collinear
      * 1 --> Clockwise
      * 2 --> Counterclockwise

    Args:
        p: Point 1
        q: Point 2
        r: Point 3

    Returns:
        int: 0, 1, or 2 depending on the orientation
    """
    val = ((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1]))

    if val == 0:
        return 0  # collinear
    if val > 0:
        return 1  # clockwise
    else:
        return 2  # counter-clockwise


def are_lines_intersecting(p1: Point2, q1: Point2, p2: Point2, q2: Point2) -> bool:
    """
    Given two lines defined by points p1, q1 and p2, q2, the function
    returns true if the two lines intersect.

    Args:
        p1: Point 1
        q1: Point 2
        p2: Point 3
        q2: Point 4

    Returns:
        bool: ``True`` or ``False`` depending if lines intersect
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


def is_point_in_polygon(x: float, y: float, polygon: Point2List) -> bool:
    """
    Checks if a point is inside a polygon of three or more points.

    Args:
        x: X coordinate of point
        y: Y coordinate of point
        polygon: List of points that define the polygon.

    Returns:
        bool: ``True`` or ``False`` depending if point is inside polygon
    """
    p = x, y
    n = len(polygon)

    # There must be at least 3 vertices
    # in polygon
    if n < 3:
        return False

    # Create a point for line segment
    # from p to infinite
    extreme = (sys_int_maxsize, p[1])

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
                return is_point_in_box(
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
