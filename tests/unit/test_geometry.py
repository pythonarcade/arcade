from arcade.geometry import (
    is_point_in_polygon,
    are_polygons_intersecting,
    get_triangle_orientation,
    are_lines_intersecting,
    is_point_in_box,
)


def test_point_in_rectangle():
    polygon = [
        (0, 0),
        (0, 50),
        (50, 50),
        (50, 0),
    ]
    result = is_point_in_polygon(25, 25, polygon)
    assert result is True


def test_point_not_in_rectangle():
    polygon = [
        (0, 0),
        (0, 50),
        (50, 50),
        (50, 0),
    ]
    result = is_point_in_polygon(100, 100, polygon)
    assert result is False


def test_point_not_in_empty_polygon():
    polygon = []
    result = is_point_in_polygon(25, 25, polygon)
    assert result is False


def test_are_polygons_intersecting():
    poly_a = [(0, 0), (0, 50), (50, 50), (50, 0)]
    poly_b = [(25, 25), (25, 75), (75, 75), (75, 25)]
    assert are_polygons_intersecting(poly_a, poly_b) is True


def test_are_polygons_not_intersecting():
    poly_a = [(0, 0), (0, 50), (50, 50), (50, 0)]
    poly_b = [(100, 100), (100, 150), (150, 150), (150, 100)]
    assert are_polygons_intersecting(poly_a, poly_b) is False

def test_are_empty_polygons_breaking():
    poly_a = [] 
    poly_b = []
    assert are_polygons_intersecting(poly_a, poly_b) is False

def test_are_mismatched_polygons_breaking():
    poly_a = [(0, 0), (0, 50), (50, 50), (50, 0)] 
    poly_b = []
    assert are_polygons_intersecting(poly_a, poly_b) is False


def test_get_triangle_orientation():
    triangle_colinear = [(0, 0), (0, 50), (0, 100)]
    assert get_triangle_orientation(*triangle_colinear) == 0

    triangle_cw = [(0, 0), (0, 50), (50, 50)]
    assert get_triangle_orientation(*triangle_cw) == 1

    triangle_ccw = list(reversed(triangle_cw))
    assert get_triangle_orientation(*triangle_ccw) == 2


def test_are_lines_intersecting():
    line_a = [(0, 0), (50, 50)]
    line_b = [(0, 0), (50, 50)]
    assert are_lines_intersecting(*line_a, *line_b) is True

    #---------
    # Two lines clearly intersecting
    line_a = [(0, 0), (50, 50)]
    line_b = [(0, 50), (50, 0)]
    assert are_lines_intersecting(*line_a, *line_b) is True

    # Two parallel lines clearly not intersecting
    line_a = [(0, 0), (50, 0)]
    line_b = [(0, 50), (0, 50)]
    assert are_lines_intersecting(*line_a, *line_b) is False

    # Two lines intersecting at the edge points
    line_a = [(0, 0), (50, 0)]
    line_b = [(0, -50), (0, 50)]
    assert are_lines_intersecting(*line_a, *line_b) is True

    # Twp perpendicular lines almost intersecting
    line_a = [(0, 0), (50, 0)]
    line_b = [(-1, -50), (-1, 50)]
    assert are_lines_intersecting(*line_a, *line_b) is False

    # Twp perpendicular lines almost intersecting
    line_a = [(0, 0), (50, 0)]
    line_b = [(51, -50), (51, 50)]
    assert are_lines_intersecting(*line_a, *line_b) is False


def test_is_point_in_box():
    # Point inside box
    assert is_point_in_box((0, 0), (50, 50), (100, 100)) is True
    assert is_point_in_box((0, 0), (-50, -50), (-100, -100)) is True
    assert is_point_in_box((0, 0), (0, 0), (100, 100)) is True

    # Point outside box
    assert is_point_in_box((0, 0), (-1, -1), (100, 100)) is False
    assert is_point_in_box((0, 0), (101, 101), (100, 100)) is False


if __name__ == "__main__":
    test_are_lines_intersecting()
