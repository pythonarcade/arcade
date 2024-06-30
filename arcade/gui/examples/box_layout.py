"""
Arrange widgets in vertical or horizontal lines with UIBoxLayout

The direction UIBoxLayout follows is controlled by the `vertical` keyword
argument. It is True by default. Pass False to it to arrange elements in
a horizontal line.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.box_layout
"""

from __future__ import annotations

import arcade
from arcade.gui import UIManager, UIBoxLayout
from arcade.gui.widgets import UIDummy, UISpace
from arcade.gui.widgets.layout import UIAnchorLayout


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        anchor = self.ui.add(UIAnchorLayout())

        self.v_box = UIBoxLayout(
            children=[
                UIDummy(width=200, color=arcade.color.RED),
                UIDummy(width=200, color=arcade.color.YELLOW),
                UIDummy(width=200, color=arcade.color.GREEN),
            ],
            space_between=20,
        ).with_border()
        anchor.add(
            align_x=200,
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.v_box,
        )

        self.h_box = UIBoxLayout(
            vertical=False,
            children=[
                UIDummy(width=100, color=arcade.color.RED),
                UISpace(width=20, height=100),
                UIDummy(width=50, color=arcade.color.YELLOW).with_padding(right=30),
                UIDummy(width=100, color=arcade.color.GREEN),
            ],
        )
        anchor.add(
            child=self.h_box.with_border(),
            anchor_x="center_x",
            anchor_y="center_y",
            align_x=-200,
        )

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
