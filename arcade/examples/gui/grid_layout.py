"""Arrange elements in line with grid tiles with UIGridLayout

UIGridLayout allows you to place elements to cover one or more
cells of a grid. To assign an element more than one grid square,
use the col_span and row_span keyword arguments.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.grid_layout
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

        dummy1 = UIDummy(size_hint=(1, 1))
        dummy2 = UIDummy(width=50, height=50)
        dummy3 = UIDummy(width=50, height=50, size_hint=(0.5, 0.5))
        dummy4 = UIDummy(size_hint=(1, 1))
        dummy5 = UIDummy(size_hint=(1, 1))
        dummy6 = UIDummy(size_hint=(1, 1))

        subject = (
            UIGridLayout(
                column_count=3,
                row_count=3,
                size_hint=(0.5, 0.5),
            )
            .with_border(color=arcade.color.RED)
            .with_padding(all=2)
        )

        subject.add(child=dummy1, column=0, row=0)
        subject.add(child=dummy2, column=0, row=1)
        subject.add(child=dummy3, column=1, row=0)
        subject.add(child=dummy4, column=1, row=1)
        subject.add(child=dummy5, column=0, row=2, column_span=2)
        subject.add(child=dummy6, column=2, row=0, row_span=3)

        anchor = UIAnchorLayout()
        anchor.add(subject)

        self.ui.add(anchor)

        self.ui.execute_layout()
        print(subject.size)
        self.grid = subject

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        # Disable UIManager when view gets inactive
        self.ui.disable()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.D:
            self.grid.legacy_mode = not self.grid.legacy_mode
        return True

    def on_draw(self):
        self.clear()
        self.ui.draw()


if __name__ == "__main__":
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
