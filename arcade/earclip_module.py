"""

from: https://github.com/linuxlewis/tripy/blob/master/tripy.py
"""

from arcade import Point, PointList
from typing import List, Tuple


def earclip(polygon: PointList) -> List[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]]:
    """
    Simple earclipping algorithm for a given polygon p.
    polygon is expected to be an array of 2-tuples of the cartesian points of the polygon
    For a polygon with n points it will return n-2 triangles.
    The triangles are returned as an array of 3-tuples where each item in the tuple is a 2-tuple of the cartesian point.

    Implementation Reference:
        - https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf
    """
    ear_vertex = []
    triangles = []

    polygon = [point for point in polygon]

    if _is_clockwise(polygon):
        polygon.reverse()

    point_count = len(polygon)
    for i in range(point_count):
        prev_index = i - 1
        prev_point = polygon[prev_index]
        point = polygon[i]
        next_index = (i + 1) % point_count
        next_point = polygon[next_index]

        if _is_ear(prev_point, point, next_point, polygon):
            ear_vertex.append(point)

    while ear_vertex and point_count >= 3:
        ear = ear_vertex.pop(0)
        i = polygon.index(ear)
        prev_index = i - 1
        prev_point = polygon[prev_index]
        next_index = (i + 1) % point_count
        next_point = polygon[next_index]

        polygon.remove(ear)
        point_count -= 1
        triangles.append(((prev_point[0], prev_point[1]), (ear[0], ear[1]), (next_point[0], next_point[1])))
        if point_count > 3:
            prev_prev_point = polygon[prev_index - 1]
            next_next_index = (i + 1) % point_count
            next_next_point = polygon[next_next_index]

            groups = [
                (prev_prev_point, prev_point, next_point, polygon),
                (prev_point, next_point, next_next_point, polygon)
            ]
            for group in groups:
                p = group[1]
                if _is_ear(*group):
                    if p not in ear_vertex:
                        ear_vertex.append(p)
                elif p in ear_vertex:
                    ear_vertex.remove(p)
    return triangles


def _is_clockwise(polygon: List[Point]):
    s = 0.0
    polygon_count = len(polygon)
    for i in range(polygon_count):
        point = polygon[i]
        point2 = polygon[(i + 1) % polygon_count]
        s += (point2[0] - point[0]) * (point2[1] + point[1])
    return s > 0


def _is_convex(prev: Point, point: Point, next_point: Point):
    return _triangle_sum(prev[0], prev[1], point[0], point[1], next_point[0], next_point[1]) < 0


def _is_ear(p1: Point, p2: Point, p3: Point, polygon: List[Point]):
    return _contains_no_points(p1, p2, p3, polygon) and \
        _is_convex(p1, p2, p3) and \
        _triangle_area(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]) > 0


def _contains_no_points(p1: Point, p2: Point, p3: Point, polygon: List[Point]):
    for pn in polygon:
        if pn in (p1, p2, p3):
            continue
        elif _is_point_inside(pn, p1, p2, p3):
            return False
    return True


def _is_point_inside(p: Point, a: Point, b: Point, c: Point):
    area = _triangle_area(a[0], a[1], b[0], b[1], c[0], c[1])
    area1 = _triangle_area(p[0], p[1], b[0], b[1], c[0], c[1])
    area2 = _triangle_area(p[0], p[1], a[0], a[1], c[0], c[1])
    area3 = _triangle_area(p[0], p[1], a[0], a[1], b[0], b[1])
    return area == sum([area1, area2, area3])


def _triangle_area(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> float:
    return abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)


def _triangle_sum(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> float:
    return x1 * (y3 - y2) + x2 * (y1 - y3) + x3 * (y2 - y1)
