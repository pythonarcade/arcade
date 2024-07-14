from arcade.geometry import is_point_in_polygon


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


def test_point_in_extreme_polygon():
    # Cf : https://github.com/pythonarcade/arcade/issues/1906
    polygon = [(9984.0, 2112.0), (10048.0, 2112.0), (10048.0, 2048.0), (9984.0, 2048.0)]

    assert is_point_in_polygon(10016.0, 2080.0, polygon)

