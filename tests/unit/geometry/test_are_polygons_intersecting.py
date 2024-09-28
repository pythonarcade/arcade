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
