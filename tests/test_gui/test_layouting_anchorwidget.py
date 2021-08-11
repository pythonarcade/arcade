from arcade.gui.widgets import UIAnchorWidget, UIWidget, UIBoxGroup, UIDummy


def test_place_widget():
    widget = UIDummy(width=100, height=200)

    placed_widget = UIAnchorWidget(
        anchor_x="center_x",
        align_y=-20,
        anchor_y="top",
        child=widget
    )
    placed_widget.parent = UIDummy(width=500, height=500)

    placed_widget.do_layout()

    assert placed_widget.rect == (200, 280, 100, 200)


def test_place_box_widget():
    widget = UIBoxGroup()
    widget.add(UIDummy(width=100, height=100))
    widget.add(UIDummy(width=100, height=100))

    placed_widget = UIAnchorWidget(
        anchor_x="center_x",
        align_y=-20,
        anchor_y="top",
        child=widget
    )
    placed_widget.parent = UIDummy(width=500, height=500)

    placed_widget.do_layout()

    assert placed_widget.rect == (200, 280, 100, 200)
