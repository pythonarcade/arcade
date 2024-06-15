from math import ceil

from arcade.gui.widgets import GUIRect


def test_rect_properties():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # THEN
    assert rect.x == 10
    assert rect.y == 20
    assert rect.width == 100
    assert rect.height == 200
    assert rect.left == 10
    assert rect.bottom == 20
    assert rect.top == 220
    assert rect.right == 110


def test_rect_move():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.move(30, 50)

    # THEN
    assert new_rect == (40, 70, 100, 200)


def test_rect_resize():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.resize(200, 300)

    # THEN
    assert new_rect == (10, 20, 200, 300)


def test_rect_align_center_x():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_center_x(50)

    # THEN
    assert new_rect == (0, 20, 100, 200)


def test_rect_align_center_y():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_center_y(50)

    # THEN
    assert new_rect == (10, -50, 100, 200)


def test_rect_center():
    # WHEN
    rect = GUIRect(0, 0, 100, 200)

    # THEN
    assert rect.center == (50, 100)


def test_rect_align_top():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_top(50)

    # THEN
    assert new_rect == (10, -150, 100, 200)


def test_rect_align_bottom():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_bottom(50)

    # THEN
    assert new_rect == (10, 50, 100, 200)


def test_rect_align_right():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_right(50)

    # THEN
    assert new_rect == (-50, 20, 100, 200)


def test_rect_align_left():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_left(50)

    # THEN
    assert new_rect == (50, 20, 100, 200)


def test_rect_min_size():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.min_size(120, 180)

    # THEN
    assert new_rect == (10, 20, 120, 200)


def test_rect_max_size():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.max_size(120, 180)

    # THEN
    assert new_rect == (10, 20, 100, 180)


def test_rect_max_size_only_width():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.max_size(width=80)

    # THEN
    assert new_rect == (10, 20, 80, 200)


def test_rect_max_size_only_height():
    # GIVEN
    rect = GUIRect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.max_size(height=80)

    # THEN
    assert new_rect == (10, 20, 100, 80)


def test_rect_union():
    # GIVEN
    rect_a = GUIRect(0, 5, 10, 5)
    rect_b = GUIRect(5, 0, 15, 8)

    # WHEN
    new_rect = rect_a.union(rect_b)

    # THEN
    assert new_rect == (0, 0, 20, 10)


def test_collide_with_point():
    rect = GUIRect(0, 0, 100, 100)

    assert rect.collide_with_point(0, 0)
    assert rect.collide_with_point(50, 50)
    assert rect.collide_with_point(100, 100)
    assert not rect.collide_with_point(150, 150)


def test_rect_scale():
    rect = GUIRect(0, 0, 95, 99)

    # Default rounding rounds down
    assert rect.scale(0.9) == (0, 0, 85, 89)

    # Passing in a rounding technique works too
    assert rect.scale(0.9, rounding=ceil) == (0, 0, 86, 90)

    # Passing in None applies no rounding
    rect_100 = GUIRect(100, 100, 100, 100)
    rect_100_scaled = rect_100.scale(0.1234, None)
    assert rect_100_scaled == (12.34, 12.34, 12.34, 12.34)
    assert rect_100_scaled.x == 12.34
    assert rect_100_scaled.y == 12.34
    assert rect_100_scaled.width == 12.34
    assert rect_100_scaled.height == 12.34

    # Passing in None via rounding keyword applies no rounding
    rect_100_scaled = rect_100.scale(0.1234, rounding=None)
    assert rect_100_scaled == (12.34, 12.34, 12.34, 12.34)
    assert rect_100_scaled.x == 12.34
    assert rect_100_scaled.y == 12.34
    assert rect_100_scaled.width == 12.34
    assert rect_100_scaled.height == 12.34
