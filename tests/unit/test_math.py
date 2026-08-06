"""
Unit tests for utils.py

Can run these tests individually with:
python -m pytest tests/unit/test_utils.py
"""

import math

import arcade
from pytest import approx
from arcade.math import *
from arcade.types import LBWH


def test_lerp():
    assert lerp(2.0, 4.0, 0.75) == approx(3.5)


def test_lerp_2d():
    vec = lerp_2d((0.0, 2.0), (8.0, 4.0), 0.25)
    assert vec[0] == approx(2.0)
    assert vec[1] == approx(2.5)
    vec = lerp_2d((0.0, 2.0), (8.0, 4.0), -0.25)
    assert vec[0] == approx(-2.0)
    assert vec[1] == approx(1.5)


def test_lerp_angle_normal():
    assert lerp_angle(0, 90, 0.5) == 45


def test_lerp_angle_backwards():
    assert lerp_angle(90, 0, 0.5) == 45


def test_lerp_angle_loop_around():
    assert lerp_angle(355, 15, 0.5) == 5


def test_lerp_angle_loop_around_backwards():
    assert lerp_angle(10, 350, 0.5) == 0


def test_lerp_angle_equal():
    assert lerp_angle(50, 50, 0.5) == 50


def test_lerp_angle_effectively_equal():
    assert lerp_angle(50, 50 + 360, 0.5) == 50
    assert lerp_angle(50 - 360, 50, 0.5) == 50


def test_rand_in_rect():
    """Smoke test"""
    rand_in_rect(LBWH(10.0, 20.0, 30.5, 5.1))


def test_rand_in_circle():
    """Smoke test"""
    rand_in_circle((0, 0), 10.0)


def test_rand_on_circle():
    """Smoke test"""
    rand_on_circle((10.0, 20.0), 15.5)


def test_rand_on_line():
    """Smoke test"""
    rand_on_line((-5.5, -2.2), (5.2, 14.7))


def test_rand_angle_360_deg():
    """Smoke test"""
    rand_angle_360_deg()


def test_rand_angle_spread_deg():
    """Smoke test"""
    rand_angle_spread_deg(45.0, 5.0)


def test_rand_vec_spread_deg():
    """Smoke test"""
    rand_vec_spread_deg(-45.0, 5.0, 3.3)


def test_rand_vec_magnitude():
    """Smoke test"""
    rand_vec_magnitude(30.5, 3.3, 4.4)


def test_rotate_around_point_preserves_distance_from_source():
    """The rotated point must keep its distance from the center of rotation (source)."""
    source = (2.0, 3.0)
    target = (5.0, 7.0)  # distance 5 from source
    for angle in (30.0, 90.0, 170.0, 250.0):
        rx, ry = rotate_around_point(source, target, angle)
        dist = math.hypot(rx - source[0], ry - source[1])
        assert dist == approx(5.0)


def test_rotate_around_point_180_reflects_through_source():
    """A 180 degree rotation reflects the target through the source (direction-independent)."""
    source = (2.0, 3.0)
    target = (5.0, 3.0)
    rx, ry = rotate_around_point(source, target, 180.0)
    assert rx == approx(2.0 * source[0] - target[0])
    assert ry == approx(2.0 * source[1] - target[1])
