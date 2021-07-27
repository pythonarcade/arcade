from arcade.experimental.gui_v2.widgets import AnchorWidget, Widget, ListGroup, Dummy


def test_place_widget():
    widget = Dummy(width=100, height=200)

    placed_widget = AnchorWidget(
        anchor_x="center_x",
        align_y=-20,
        anchor_y="top",
        child=widget
    )
    placed_widget.parent = Dummy(width=500, height=500)

    placed_widget.do_layout()

    assert placed_widget.rect == (200, 280, 100, 200)


def test_place_box_widget():
    widget = ListGroup()
    widget.add(Dummy(width=100, height=100))
    widget.add(Dummy(width=100, height=100))

    placed_widget = AnchorWidget(
        anchor_x="center_x",
        align_y=-20,
        anchor_y="top",
        child=widget
    )
    placed_widget.parent = Dummy(width=500, height=500)

    placed_widget.do_layout()

    assert placed_widget.rect == (200, 280, 100, 200)
