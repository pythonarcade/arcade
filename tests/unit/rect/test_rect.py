from pyglet.math import Vec2
from pytest import approx

from arcade import LBWH
from arcade.types import AnchorPoint


def test_rect_properties():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # THEN
    assert rect.left == 10
    assert rect.bottom == 20
    assert rect.width == 100
    assert rect.height == 200
    assert rect.left == 10
    assert rect.bottom == 20
    assert rect.top == 220
    assert rect.right == 110


def test_rect_move():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.move(30, 50)

    # THEN
    assert new_rect == LBWH(40, 70, 100, 200)


def test_rect_resize():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.resize(200, 300, anchor=AnchorPoint.BOTTOM_LEFT)

    # THEN
    assert new_rect == LBWH(10, 20, 200, 300)


def test_rect_align_center_x():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_center_x(50)

    # THEN
    assert new_rect == LBWH(0, 20, 100, 200)


def test_rect_align_center_y():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_center_y(50)

    # THEN
    assert new_rect == LBWH(10, -50, 100, 200)


def test_rect_center():
    # WHEN
    rect = LBWH(0, 0, 100, 200)

    # THEN
    assert rect.center == Vec2(50.0, 100.0)


def test_rect_align_top():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_top(50)

    # THEN
    assert new_rect == LBWH(10, -150, 100, 200)


def test_rect_align_bottom():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_bottom(50)

    # THEN
    assert new_rect == LBWH(10, 50, 100, 200)


def test_rect_align_right():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_right(50)

    # THEN
    assert new_rect == LBWH(-50, 20, 100, 200)


def test_rect_align_left():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_left(50)

    # THEN
    assert new_rect == LBWH(50, 20, 100, 200)


def test_rect_min_size_anchor_bl():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.min_size(120, 180, anchor=AnchorPoint.BOTTOM_LEFT)

    # THEN
    assert new_rect == LBWH(10, 20, 120, 200)


def test_rect_max_size_anchor_bl():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.max_size(120, 180, anchor=AnchorPoint.BOTTOM_LEFT)

    # THEN
    assert new_rect == LBWH(10, 20, 100, 180)


def test_rect_max_size_only_width():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.max_size(width=80, anchor=AnchorPoint.BOTTOM_LEFT)

    # THEN
    assert new_rect == LBWH(10, 20, 80, 200)


def test_rect_max_size_only_height():
    # GIVEN
    rect = LBWH(10, 20, 100, 200)

    # WHEN
    new_rect = rect.max_size(height=80, anchor=AnchorPoint.BOTTOM_LEFT)

    # THEN
    assert new_rect == LBWH(10, 20, 100, 80)


def test_rect_union():
    # GIVEN
    rect_a = LBWH(0, 5, 10, 5)
    rect_b = LBWH(5, 0, 15, 8)

    # WHEN
    new_rect = rect_a.union(rect_b)

    # THEN
    assert new_rect == LBWH(0, 0, 20, 10)


def test_point_in_rect():
    rect = LBWH(0, 0, 100, 100)

    assert rect.point_in_rect((0, 0))
    assert rect.point_in_rect((50, 50))
    assert rect.point_in_rect((100, 100))
    assert not rect.point_in_rect((150, 150))


def test_point_in_bounds():
    rect = LBWH(0, 0, 100, 100)

    # on bounds
    assert not rect.point_in_bounds((0, 0))
    assert not rect.point_in_bounds((100, 100))

    # out of bounds
    assert not rect.point_in_bounds((150, 150))

    # in bounds
    assert rect.point_in_bounds((1, 1))
    assert rect.point_in_bounds((50, 50))
    assert rect.point_in_bounds((99, 99))


def test_rect_scale():
    rect = LBWH(0, 0, 95, 99)

    new_rect = rect.scale(0.9, anchor=AnchorPoint.BOTTOM_LEFT)

    assert new_rect.left == 0
    assert new_rect.bottom == 0
    assert new_rect.right == approx(85.5, abs=1)
    assert new_rect.top == approx(89.1, abs=1)
    assert new_rect.width == approx(85.5, abs=1)
    assert new_rect.height == approx(89.1, abs=1)


def test_min_width_issue():
    rect = LBWH(0, 0, 0, 50)

    new_rect = rect.min_size(width=50.0)

    assert new_rect.width == 50.0
    assert new_rect.left == -25.0
    assert new_rect.right == 25.0
