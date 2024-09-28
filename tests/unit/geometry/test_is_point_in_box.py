from arcade.geometry import is_point_in_box


def test_point_inside_center():
    """Points clearly inside the box"""
    assert is_point_in_box((0, 0), (50, 50), (100, 100)) is True
    assert is_point_in_box((0, 0), (-50, -50), (-100, -100)) is True
    assert is_point_in_box((0, 0), (50, -50), (100, -100)) is True
    assert is_point_in_box((0, 0), (-50, 50), (-100, 100)) is True


def test_point_intersecting():
    """Points intersecting the box edges"""
    # Test each corner
    assert is_point_in_box((0, 0), (0, 0), (100, 100)) is True
    assert is_point_in_box((0, 0), (100, 100), (100, 100)) is True
    assert is_point_in_box((0, 0), (100, 0), (100, 100)) is True
    assert is_point_in_box((0, 0), (0, 100), (100, 100)) is True


def test_point_outside_1px():
    """Points outside the box by one pixel"""
    assert is_point_in_box((0, 0), (-1, -1), (100, 100)) is False
    assert is_point_in_box((0, 0), (101, 101), (100, 100)) is False
    assert is_point_in_box((0, 0), (101, -1), (100, 100)) is False
    assert is_point_in_box((0, 0), (-1, 101), (100, 100)) is False
