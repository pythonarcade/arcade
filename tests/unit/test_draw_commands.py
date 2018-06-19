def test_rotate_point(mock_window):
    from arcade import rotate_point
    x, y = rotate_point(1, 1, 0, 0, 90)
    assert (-1.0, 1.0) == (x, y)
