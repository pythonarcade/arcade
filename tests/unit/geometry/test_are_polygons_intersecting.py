import math
import random

from arcade.geometry import are_polygons_intersecting


def test_intersecting_clear_case():
    """Two polygons clearly intersecting"""
    poly_a = [(0, 0), (0, 50), (50, 50), (50, 0)]
    poly_b = [(25, 25), (25, 75), (75, 75), (75, 25)]
    assert are_polygons_intersecting(poly_a, poly_b) is True
    assert are_polygons_intersecting(poly_b, poly_a) is True


def test_empty_polygons():
    """Two empty polys should never intersect"""
    poly_a = []
    poly_b = []
    assert are_polygons_intersecting(poly_a, poly_b) is False


def test_are_mismatched_polygons_breaking():
    """One empty poly should never intersect with a non-empty poly"""
    poly_a = [(0, 0), (0, 50), (50, 50), (50, 0)]
    poly_b = []
    assert are_polygons_intersecting(poly_a, poly_b) is False
    assert are_polygons_intersecting(poly_b, poly_a) is False


def test_touching_edges_do_not_intersect():
    """Polygons that only share an edge or corner don't intersect"""
    poly_a = [(0, 0), (0, 50), (50, 50), (50, 0)]
    assert are_polygons_intersecting(poly_a, [(50, 0), (50, 50), (100, 50), (100, 0)]) is False
    assert are_polygons_intersecting(poly_a, [(50, 50), (50, 100), (100, 100), (100, 50)]) is False
    # Triangle touching the square's corner
    assert are_polygons_intersecting(poly_a, [(50, 50), (60, 50), (50, 60)]) is False
    # Diamond touching the middle of the square's right edge with its corner
    assert are_polygons_intersecting(poly_a, [(50, 25), (60, 15), (70, 25), (60, 35)]) is False


def test_repeated_points():
    """A repeated point (e.g. a closed polygon) must not break the check"""
    poly_a = [(0, 0), (0, 50), (50, 50), (50, 0), (0, 0)]
    poly_b = [(25, 25), (25, 25), (25, 75), (75, 75), (75, 25)]
    assert are_polygons_intersecting(poly_a, poly_b) is True
    assert are_polygons_intersecting(poly_b, poly_a) is True
    assert are_polygons_intersecting(poly_a, [(10, 10), (20, 10), (20, 20), (10, 20), (10, 10)])


def test_diagonal_near_miss():
    """Bounding boxes overlap but a diagonal edge separates the polygons"""
    triangle_a = [(0, 0), (10, 0), (0, 10)]
    triangle_b = [(6, 6), (10, 6), (10, 10), (6, 10)]
    assert are_polygons_intersecting(triangle_a, triangle_b) is False
    assert are_polygons_intersecting(triangle_b, triangle_a) is False


def _reference_are_polygons_intersecting(poly_a, poly_b):
    """The original separating axis implementation, used as a reference."""
    if not poly_a or not poly_b:
        return False
    for polygon in (poly_a, poly_b):
        for i1 in range(len(polygon)):
            i2 = (i1 + 1) % len(polygon)
            p1 = polygon[i1]
            p2 = polygon[i2]
            normal = (p2[1] - p1[1], p1[0] - p2[0])
            projected_a = [normal[0] * p[0] + normal[1] * p[1] for p in poly_a]
            projected_b = [normal[0] * p[0] + normal[1] * p[1] for p in poly_b]
            if max(projected_a) <= min(projected_b) or max(projected_b) <= min(projected_a):
                return False
    return True


def _random_convex_polygon(rng):
    kind = rng.randrange(4)
    x, y = rng.randint(-20, 20), rng.randint(-20, 20)
    if kind == 0:
        # Axis-aligned rectangle on an integer grid, so exact touches are common
        w, h = rng.randint(1, 20), rng.randint(1, 20)
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    if kind == 1:
        # Octagon like the ones the default hit box algorithm makes
        w, h, c = rng.randint(4, 20), rng.randint(4, 20), rng.randint(1, 3)
        return [
            (x - w, y - h + c), (x - w + c, y - h), (x + w - c, y - h), (x + w, y - h + c),
            (x + w, y + h - c), (x + w - c, y + h), (x - w + c, y + h), (x - w, y + h - c),
        ]  # fmt: skip
    # Regular polygon with a random rotation
    sides = rng.randint(3, 8)
    radius = rng.uniform(1, 20)
    start = rng.uniform(0, math.tau)
    return [
        (x + radius * math.cos(start + math.tau * i / sides),
         y + radius * math.sin(start + math.tau * i / sides))
        for i in range(sides)
    ]  # fmt: skip


def test_matches_reference_implementation():
    """Compare against the original implementation on many random polygons"""
    rng = random.Random(1234)
    results = {True: 0, False: 0}
    for _ in range(20_000):
        poly_a = _random_convex_polygon(rng)
        poly_b = _random_convex_polygon(rng)
        expected = _reference_are_polygons_intersecting(poly_a, poly_b)
        assert are_polygons_intersecting(poly_a, poly_b) is expected, (poly_a, poly_b)
        results[expected] += 1
    # Make sure both outcomes were well covered
    assert min(results.values()) > 2000
