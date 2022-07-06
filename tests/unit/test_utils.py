"""
Unit tests for utils.py

Can run these tests individually with:
python -m pytest tests/unit/test_utils.py
"""

import arcade
from pytest import approx
# noinspection PyProtectedMember
from arcade.utils import _Vec2  # importing internal implementation class


def test_lerp():
    assert arcade.lerp(2.0, 4.0, 0.75) == approx(3.5)


def test_lerp_vec():
    vec = arcade.lerp_vec((0.0, 2.0), (8.0, 4.0), 0.25)
    assert vec[0] == approx(2.0)
    assert vec[1] == approx(2.5)
    vec = arcade.lerp_vec((0.0, 2.0), (8.0, 4.0), -0.25)
    assert vec[0] == approx(-2.0)
    assert vec[1] == approx(1.5)


def test_lerp_angle_normal():
    assert arcade.lerp_angle(0, 90, 0.5) == 45


def test_lerp_angle_backwards():
    assert arcade.lerp_angle(90, 0, 0.5) == 45


def test_lerp_angle_loop_around():
    assert arcade.lerp_angle(355, 15, 0.5) == 5


def test_lerp_angle_loop_around_backwards():
    assert arcade.lerp_angle(10, 350, 0.5) == 0


def test_lerp_angle_equal():
    assert arcade.lerp_angle(50, 50, 0.5) == 50


def test_lerp_angle_effectively_equal():
    assert arcade.lerp_angle(50, 50 + 360, 0.5) == 50


def test_rand_in_rect():
    """Smoke test"""
    arcade.rand_in_rect((10.0, 20.0), 30.5, 5.1)


def test_rand_in_circle():
    """Smoke test"""
    arcade.rand_in_circle((0, 0), 10.0)


def test_rand_on_circle():
    """Smoke test"""
    arcade.rand_on_circle((10.0, 20.0), 15.5)


def test_rand_on_line():
    """Smoke test"""
    arcade.rand_on_line((-5.5, -2.2), (5.2, 14.7))


def test_rand_angle_360_deg():
    """Smoke test"""
    arcade.rand_angle_360_deg()


def test_rand_angle_spread_deg():
    """Smoke test"""
    arcade.rand_angle_spread_deg(45.0, 5.0)


def test_rand_vec_spread_deg():
    """Smoke test"""
    arcade.rand_vec_spread_deg(-45.0, 5.0, 3.3)


def test_rand_vec_magnitude():
    """Smoke test"""
    arcade.rand_vec_magnitude(30.5, 3.3, 4.4)


def test_vec():
    # 2 floats
    v = _Vec2(3.3, 5.5)
    assert v.x == 3.3
    assert v.y == 5.5

    # one tuple
    v = _Vec2((1.1, 2.2))
    assert v.x == 1.1
    assert v.y == 2.2

    # iterator access
    items = [item for item in v]
    assert items == [1.1, 2.2]

    # tuple access
    assert v.as_tuple() == (1.1, 2.2)

    # string representation
    assert repr(v) == "Vec2(1.1,2.2)"
    assert str(v) == "Vec2(1.1,2.2)"


def test_vec_length():
    assert _Vec2(5.0, 0.0).length() == approx(5.0)
    assert _Vec2(0.0, -5.0).length() == approx(5.0)
    assert _Vec2(3.5355339, 3.5355339).length() == approx(5.0)
    assert _Vec2(-3.5355339, -3.5355339).length() == approx(5.0)


def test_vec_from_polar():
    v = _Vec2.from_polar(45, 4.0)
    assert v.x == approx(2.8284271)
    assert v.y == approx(2.8284271)


def test_vec_add_and_subtract():
    v1 = _Vec2(5.0, 4.0)
    v2 = _Vec2(-1.5, 3.0)

    v3 = v1 + v2
    assert v3.x == 3.5
    assert v3.y == 7.0

    v3 = v1 - v2
    assert v3.x == 6.5
    assert v3.y == 1.0


def test_vec_mult_and_divide():
    v1 = _Vec2(5.0, 4.0)
    v2 = _Vec2(0.5, -0.25)

    v3 = v1 * v2
    assert v3.x == 2.5
    assert v3.y == -1.0

    v4 = v3 / v2
    assert v4.x == v1.x
    assert v4.y == v1.y


def test_vec_dot():
    v1 = _Vec2(5.0, 4.0)
    v2 = _Vec2(0.5, -0.25)
    assert v1.dot(v2) == 1.5


def test_vec_rotated():
    v1 = _Vec2(3.0, 0.0)

    rotated = v1.rotated(0.0)
    assert rotated.x == approx(3.0)
    assert rotated.y == approx(0.0)

    rotated = v1.rotated(90.0)
    assert rotated.x == approx(0.0)
    assert rotated.y == approx(3.0)

    rotated = v1.rotated(-90.0)
    assert rotated.x == approx(0.0)
    assert rotated.y == approx(-3.0)

    rotated = v1.rotated(45.0)
    assert rotated.x == approx(2.12132)
    assert rotated.y == approx(2.12132)
