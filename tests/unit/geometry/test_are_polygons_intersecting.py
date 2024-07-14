from arcade.geometry import are_polygons_intersecting


def test_are_polygons_intersecting():
    poly_a = [(0, 0), (0, 50), (50, 50), (50, 0)]
    poly_b = [(25, 25), (25, 75), (75, 75), (75, 25)]
    assert are_polygons_intersecting(poly_a, poly_b) is True


def test_are_empty_polygons_breaking():
    poly_a = []
    poly_b = []
    assert are_polygons_intersecting(poly_a, poly_b) is False


def test_are_mismatched_polygons_breaking():
    poly_a = [(0, 0), (0, 50), (50, 50), (50, 0)]
    poly_b = []
    assert are_polygons_intersecting(poly_a, poly_b) is False
