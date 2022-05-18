from arcade.gui import UIWidget


def test_widget_scale_down():
    # GIVEN
    widget = UIWidget(width=100, height=100)

    # WHEN
    widget.scale(0.5)

    # THEN
    assert widget.width == 50
    assert widget.height == 50
    assert widget.x == 0
    assert widget.y == 0


def test_widget_scale_up():
    # GIVEN
    widget = UIWidget(width=100, height=100)

    # WHEN
    widget.scale(2)

    # THEN
    assert widget.width == 200
    assert widget.height == 200
    assert widget.x == 0
    assert widget.y == 0


def test_widget_move():
    # GIVEN
    widget = UIWidget(x=100, y=200)

    # WHEN
    widget.move(10, 20)

    # THEN
    assert widget.x == 110
    assert widget.y == 220


def test_widget_set_padding_with_1_parameters():
    # GIVEN
    widget = UIWidget(x=0, y=0, width=100, height=100)

    # WHEN
    widget.padding = 20

    # THEN
    assert widget.padding_top == 20
    assert widget.padding_right == 20
    assert widget.padding_bottom == 20
    assert widget.padding_left == 20
    assert widget.padding == (20, 20, 20, 20)


def test_widget_set_padding_with_2_parameters():
    # GIVEN
    widget = UIWidget(x=0, y=0, width=100, height=100)

    # WHEN
    widget.padding = 20, 40

    # THEN
    assert widget.padding_top == 20
    assert widget.padding_right == 40
    assert widget.padding_bottom == 20
    assert widget.padding_left == 40
    assert widget.padding == (20, 40, 20, 40)


def test_widget_set_padding_with_4_parameters():
    # GIVEN
    widget = UIWidget(x=0, y=0, width=100, height=100)

    # WHEN
    widget.padding = (10, 20, 30, 40)

    # THEN
    assert widget.padding_top == 10
    assert widget.padding_right == 20
    assert widget.padding_bottom == 30
    assert widget.padding_left == 40
    assert widget.padding == (10, 20, 30, 40)


def test_widget_content_rect_affected_by_padding():
    # GIVEN
    widget = UIWidget(x=0, y=0, width=100, height=100)

    # WHEN
    widget.padding = 20

    # THEN
    assert widget.rect == (0, 0, 100, 100)
    assert widget.content_rect == (20, 20, 60, 60)


def test_widget_content_rect_affected_by_border_width():
    # GIVEN
    widget = UIWidget(x=0, y=0, width=100, height=100)

    # WHEN
    widget.border_width = 10

    # THEN
    assert widget.rect == (0, 0, 100, 100)
    assert widget.content_rect == (10, 10, 80, 80)
