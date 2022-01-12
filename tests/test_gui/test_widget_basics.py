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
