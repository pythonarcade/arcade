"""
Arrange elements in line with grid tiles with UIGridLayout

UIGridLayout allows you to place elements to cover one or more
cells of a grid. To assign an element more than one grid square,
use the col_span and row_span keyword arguments.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.grid_layout
"""

from __future__ import annotations

import arcade
from arcade.gui import UIManager
from arcade.gui.widgets import UIDummy
from arcade.gui.widgets.layout import UIGridLayout, UIAnchorLayout


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        dummy1 = UIDummy(width=100, height=100)
        dummy2 = UIDummy(width=50, height=50)
        dummy3 = UIDummy(width=50, height=50, size_hint=(0.5, 0.5))
        dummy4 = UIDummy(width=100, height=100)
        dummy5 = UIDummy(width=200, height=100)
        dummy6 = UIDummy(width=100, height=300)

        subject = (
            UIGridLayout(
                column_count=3,
                row_count=3,
                size_hint=(0.5, 0.5),
            )
            .with_border()
            .with_padding()
        )

        subject.add(child=dummy1, col_num=0, row_num=0)
        subject.add(child=dummy2, col_num=0, row_num=1)
        subject.add(child=dummy3, col_num=1, row_num=0)
        subject.add(child=dummy4, col_num=1, row_num=1)
        subject.add(child=dummy5, col_num=0, row_num=2, col_span=2)
        subject.add(child=dummy6, col_num=2, row_num=0, row_span=3)

        anchor = UIAnchorLayout()
        anchor.add(subject)

        self.ui.add(anchor)

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        # Disable UIManager when view gets inactive
        self.ui.disable()

    def on_draw(self):
        self.clear()
        self.ui.draw()


if __name__ == "__main__":
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
