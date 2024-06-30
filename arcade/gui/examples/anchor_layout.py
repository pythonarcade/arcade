"""
Positioning UI elements with UIAnchorLayout

UIAnchorLayout aligns widgets added to it to directional anchors, which
include  "left", "center_x", or "top". Dummy widgets react to click events
by changing color.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.anchor_layout
"""

from __future__ import annotations

import arcade
from arcade.gui import UIManager
from arcade.gui.widgets import UIDummy
from arcade.gui.widgets.layout import UIAnchorLayout


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        anchor = self.ui.add(UIAnchorLayout())

        anchor.add(
            child=UIDummy(),
            anchor_x="center_x",
            anchor_y="top",
        )

        anchor.add(
            child=UIDummy(),
            anchor_x="right",
            anchor_y="center_y",
        )

        anchor.add(
            child=UIDummy(),
            anchor_x="center_x",
            anchor_y="center_y",
        )

        anchor.add(
            child=UIDummy(),
            anchor_x="left",
            anchor_y="bottom",
        )

        anchor.add(
            child=UIDummy(),
            anchor_x="left",
            align_x=20,
            anchor_y="center_y",
        )

        anchor.add(
            child=UIDummy(),
            anchor_x="right",
            align_x=-40,
            anchor_y="bottom",
            align_y=40,
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
