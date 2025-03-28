"""
Functions for handling collisions with geometry.

These are the pure python versions of the functions.

Point in polygon function from https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/
"""

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
    for polygon in (poly_a, poly_b):
        for i1 in range(len(polygon)):
            i2 = (i1 + 1) % len(polygon)
            projection_1 = polygon[i1]
            projection_2 = polygon[i2]

            normal = (
                projection_2[1] - projection_1[1],
                projection_1[0] - projection_2[0],
            )

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
            if max_a <= min_b or max_b <= min_a:
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
