from arcade.experimental.gui_v2.widgets import PlacedWidget, Widget, BoxWidget


def test_place_widget():
    widget = Widget(width=100, height=200)

    placed_widget = PlacedWidget(
        x_anchor="center_x",
        y_align=-20,
        y_anchor="top",
        child=widget
    )
    placed_widget.parent = Widget(width=500, height=500)

    placed_widget.on_update(0)

    assert placed_widget.rect == (200, 280, 100, 200)


def test_place_box_widget():
    widget = BoxWidget()
    widget.add(Widget(width=100, height=100))
    widget.add(Widget(width=100, height=100))

    placed_widget = PlacedWidget(
        x_anchor="center_x",
        y_align=-20,
        y_anchor="top",
        child=widget
    )
    placed_widget.parent = Widget(width=500, height=500)

    placed_widget.on_update(0)

    assert placed_widget.rect == (200, 280, 100, 200)
