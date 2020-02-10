import arcade

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

