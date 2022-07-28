import arcade
import pytest


def test_rotate_point():
    x = 0
    y = 0
    cx = 0
    cy = 0
    angle = 0
    rx, ry = arcade.rotate_point(x, y, cx, cy, angle)
    assert rx == 0
    assert ry == 0

    x = 0
    y = 0
    cx = 0
    cy = 0
    angle = 90
    rx, ry = arcade.rotate_point(x, y, cx, cy, angle)
    assert rx == 0
    assert ry == 0

    x = 50
    y = 50
    cx = 0
    cy = 0
    angle = 0
    rx, ry = arcade.rotate_point(x, y, cx, cy, angle)
    assert rx == 50
    assert ry == 50

    x = 50
    y = 0
    cx = 0
    cy = 0
    angle = 90
    rx, ry = arcade.rotate_point(x, y, cx, cy, angle)
    assert rx == 0
    assert ry == 50

    x = 20
    y = 10
    cx = 10
    cy = 10
    angle = 180
    rx, ry = arcade.rotate_point(x, y, cx, cy, angle)
    assert rx == 0
    assert ry == 10


def test_parse_color():
    with pytest.raises(ValueError):
        arcade.color_from_hex_string("#ff0000ff0")

    # Hash symbol RGBA variants
    assert arcade.color_from_hex_string("#ffffffff") == (255, 255, 255, 255)
    assert arcade.color_from_hex_string("#ffffff00") == (255, 255, 255, 0)
    assert arcade.color_from_hex_string("#ffff00ff") == (255, 255, 0, 255)
    assert arcade.color_from_hex_string("#ff00ffff") == (255, 0, 255, 255)
    assert arcade.color_from_hex_string("#00ffffff") == (0, 255, 255, 255)

    # RGB
    assert arcade.color_from_hex_string("#ffffff") == (255, 255, 255, 255)
    assert arcade.color_from_hex_string("#ffff00") == (255, 255, 0, 255)
    assert arcade.color_from_hex_string("#ff0000") == (255, 0, 0, 255)

    # Without hash
    assert arcade.color_from_hex_string("ffffff") == (255, 255, 255, 255)
    assert arcade.color_from_hex_string("ffff00") == (255, 255, 0, 255)
    assert arcade.color_from_hex_string("ff0000") == (255, 0, 0, 255)

    # Short form
    assert arcade.color_from_hex_string("#fff") == (255, 255, 255, 255)
    assert arcade.color_from_hex_string("FFF") == (255, 255, 255, 255)

    with pytest.raises(ValueError):
        arcade.color_from_hex_string("ppp")

    with pytest.raises(ValueError):
        arcade.color_from_hex_string("ff")


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


def test_get_four_float_color():
    assert arcade.get_four_float_color((1, 2, 3)) == (1/255, 2/255, 3/255, 1.0)
    assert arcade.get_four_float_color((1, 2, 3, 4)) == (1/255, 2/255, 3/255, 4/255)

    with pytest.raises(ValueError):
        arcade.get_four_float_color((0, 0))
    with pytest.raises(TypeError):
        arcade.get_four_float_color(1000)


def test_get_three_float_color():
    assert arcade.get_three_float_color((1, 2, 3)) == (1/255, 2/255, 3/255)
    assert arcade.get_three_float_color((1, 2, 3, 4)) == (1/255, 2/255, 3/255)

    with pytest.raises(ValueError):
        arcade.get_three_float_color((1, 2))

    with pytest.raises(TypeError):
        arcade.get_three_float_color(1000)


def test_make_transparent_color():
    assert arcade.make_transparent_color((1, 2, 3), 4) == (1, 2, 3, 4)


def test_uint24_to_three_byte_color():
    assert arcade.uint24_to_three_byte_color(16777215) == (255, 255, 255)
    assert arcade.uint24_to_three_byte_color((1 << 16) + (2 << 8) + 3) == (1, 2, 3)

    with pytest.raises(TypeError):
        arcade.uint24_to_three_byte_color("moo")


def test_uint32_to_four_byte_color():
    assert arcade.uint32_to_four_byte_color(4294967295) == (255, 255, 255, 255)
    assert arcade.uint32_to_four_byte_color((1 << 24) + (2 << 16) + (3 << 8) + 4) == (1, 2, 3, 4)

    with pytest.raises(TypeError):
        arcade.uint32_to_four_byte_color("moo")


def test_float_to_byte_color():
    assert arcade.float_to_byte_color((1/255, 2/255, 3/255)) == (1, 2, 3)
    assert arcade.float_to_byte_color((1/255, 2/255, 3/255, 4/255)) == (1, 2, 3, 4)

    with pytest.raises(ValueError):
        arcade.float_to_byte_color((0, 0))

    with pytest.raises(ValueError):
        arcade.float_to_byte_color("moo")
