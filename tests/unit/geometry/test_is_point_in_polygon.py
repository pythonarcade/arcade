from arcade.geometry import is_point_in_polygon


def test_point_in_rectangle_cw():
    """Clockwise rectangle"""
    polygon = [(0, 0), (0, 50), (50, 50), (50, 0)]
    # Center
    assert is_point_in_polygon(25, 25, polygon) is True
    # One pixel from edge
    assert is_point_in_polygon(1, 1, polygon) is True
    assert is_point_in_polygon(49, 49, polygon) is True
    assert is_point_in_polygon(1, 49, polygon) is True
    assert is_point_in_polygon(49, 1, polygon) is True

    # Intersect edges
    assert is_point_in_polygon(0, 0, polygon) is True
    assert is_point_in_polygon(50, 50, polygon) is True
    assert is_point_in_polygon(0, 50, polygon) is True
    assert is_point_in_polygon(50, 0, polygon) is True


def test_point_in_rectangle_cc():
    """Counter-clockwise rectangle"""
    polygon = [(0, 0), (50, 0), (50, 50), (0, 50)]
    # Center
    assert is_point_in_polygon(25, 25, polygon) is True
    # One pixel from edge
    assert is_point_in_polygon(1, 1, polygon) is True
    assert is_point_in_polygon(49, 49, polygon) is True
    assert is_point_in_polygon(1, 49, polygon) is True
    assert is_point_in_polygon(49, 1, polygon) is True

    # Intersect edges
    assert is_point_in_polygon(0, 0, polygon) is True
    assert is_point_in_polygon(50, 50, polygon) is True
    assert is_point_in_polygon(0, 50, polygon) is True
    assert is_point_in_polygon(50, 0, polygon) is True


def test_point_not_in_rectangle():
    polygon = [(0, 0), (0, 50), (50, 50), (50, 0)]
    result = is_point_in_polygon(100, 100, polygon)
    assert result is False


def test_point_not_in_empty_polygon():
    polygon = []
    result = is_point_in_polygon(25, 25, polygon)
    assert result is False


def test_point_in_extreme_polygon():
    # Cf : https://github.com/pythonarcade/arcade/issues/1906
    polygon = [(9984.0, 2112.0), (10048.0, 2112.0), (10048.0, 2048.0), (9984.0, 2048.0)]
    assert is_point_in_polygon(10016.0, 2080.0, polygon)
