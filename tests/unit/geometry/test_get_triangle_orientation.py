from arcade.geometry import get_triangle_orientation


def test_get_triangle_orientation():
    triangle_colinear = [(0, 0), (0, 50), (0, 100)]
    assert get_triangle_orientation(*triangle_colinear) == 0

    triangle_cw = [(0, 0), (0, 50), (50, 50)]
    assert get_triangle_orientation(*triangle_cw) == 1

    triangle_ccw = list(reversed(triangle_cw))
    assert get_triangle_orientation(*triangle_ccw) == 2
