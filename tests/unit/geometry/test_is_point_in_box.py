from arcade.geometry import is_point_in_box

BOX_START = (0, 0)
BOX_END = (100, 100)


def test_point_inside():
    # Point inside box
    assert is_point_in_box((0, 0), (50, 50), (100, 100)) is True
    assert is_point_in_box((0, 0), (-50, -50), (-100, -100)) is True
    assert is_point_in_box((0, 0), (0, 0), (100, 100)) is True


def test_point_outside():
    # Point outside box
    assert is_point_in_box((0, 0), (-1, -1), (100, 100)) is False
    assert is_point_in_box((0, 0), (101, 101), (100, 100)) is False


def test_point_intersecting():
    pass
