from arcade.gui.widgets import UIDummy
from arcade.gui import UIAnchorWidget, UIBoxLayout


def test_place_widget(window):
    root = UIDummy(width=500, height=500)
    widget = UIDummy(width=100, height=200)

    placed_widget = UIAnchorWidget(
        anchor_x="center_x", align_y=-20, anchor_y="top", child=widget
    )
    root.add(placed_widget)

    placed_widget._do_layout()

    assert placed_widget.rect == (200, 280, 100, 200)


def test_place_box_layout(window):
    root = UIDummy(width=500, height=500)

    box = UIBoxLayout()
    box.add(UIDummy(width=100, height=100))
    box.add(UIDummy(width=100, height=100))

    placed_widget = UIAnchorWidget(
        anchor_x="center_x", align_y=-20, anchor_y="top", child=box
    )
    root.add(placed_widget)

    placed_widget._do_layout()

    assert placed_widget.rect == (200, 280, 100, 200)
    assert box.rect == (200, 280, 100, 200)
