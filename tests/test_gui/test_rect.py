from arcade.gui.widgets import Rect


def test_rect_properties():
    # GIVEN
    rect = Rect(10, 20, 100, 200)

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
    rect = Rect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.move(30, 50)

    # THEN
    assert new_rect == (40, 70, 100, 200)


def test_rect_resize():
    # GIVEN
    rect = Rect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.resize(200, 300)

    # THEN
    assert new_rect == (10, 20, 200, 300)


def test_rect_align_center_x():
    # GIVEN
    rect = Rect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_center_x(50)

    # THEN
    assert new_rect == (0, 20, 100, 200)


def test_rect_align_center_y():
    # GIVEN
    rect = Rect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_center_y(50)

    # THEN
    assert new_rect == (10, -50, 100, 200)


def test_rect_align_top():
    # GIVEN
    rect = Rect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_top(50)

    # THEN
    assert new_rect == (10, -150, 100, 200)


def test_rect_align_bottom():
    # GIVEN
    rect = Rect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_bottom(50)

    # THEN
    assert new_rect == (10, 50, 100, 200)


def test_rect_align_right():
    # GIVEN
    rect = Rect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_right(50)

    # THEN
    assert new_rect == (-50, 20, 100, 200)


def test_rect_align_left():
    # GIVEN
    rect = Rect(10, 20, 100, 200)

    # WHEN
    new_rect = rect.align_left(50)

    # THEN
    assert new_rect == (50, 20, 100, 200)
