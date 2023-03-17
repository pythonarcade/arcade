import pytest
import arcade
from arcade.math import rotate_point


def test_rotate_point():
    x = 0
    y = 0
    cx = 0
    cy = 0
    angle = 0
    rx, ry = rotate_point(x, y, cx, cy, angle)
    assert round(rx, 2) == 0
    assert round(ry, 2) == 0

    x = 0
    y = 0
    cx = 0
    cy = 0
    angle = 90
    rx, ry = rotate_point(x, y, cx, cy, angle)
    assert round(rx, 2) == 0
    assert round(ry, 2) == 0

    x = 50
    y = 50
    cx = 0
    cy = 0
    angle = 0
    rx, ry = rotate_point(x, y, cx, cy, angle)
    assert round(rx, 2) == 50
    assert round(ry, 2) == 50

    x = 50
    y = 0
    cx = 0
    cy = 0
    angle = 90
    rx, ry = rotate_point(x, y, cx, cy, angle)
    assert round(rx, 2) == 0
    assert round(ry, 2) == -50

    x = 20
    y = 10
    cx = 10
    cy = 10
    angle = 180
    rx, ry = rotate_point(x, y, cx, cy, angle)
    assert round(rx, 2) == 0
    assert round(ry, 2) == 10


def test_get_four_byte_color():
    assert arcade.get_four_byte_color((1, 2, 3)) == (1, 2, 3, 255)
    assert arcade.get_four_byte_color((255, 255, 255)) == (255, 255, 255, 255)

    assert arcade.get_four_byte_color((1, 2, 3, 4)) == (1, 2, 3, 4)
    assert arcade.get_four_byte_color((255, 255, 255)) == (255, 255, 255, 255)

    with pytest.raises(ValueError):
        arcade.get_four_byte_color((255, 255))

    with pytest.raises(ValueError):
        arcade.get_four_byte_color((255, 255, 255, 255, 255))

    with pytest.raises(TypeError):
        arcade.get_four_byte_color(1000)
