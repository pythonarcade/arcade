"""Sizing widgets using size hint keyword arguments

The following keyword arguments can be used to set preferred size
information for layouts which arrange widgets

* size_hint
* size_hint_max
* size_hint_min

Please note the following:

* These do nothing outside a layout
* They are only hints, and do not guarantee that a specific size will
  be provided.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.6_size_hints
"""

from __future__ import annotations

import arcade
from arcade.gui import UIAnchorLayout, UIDummy, UIBoxLayout, UIView


class MyView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_BELIZE_HOLE

        anchor = self.ui.add(UIAnchorLayout())

        self.ui_dummy = UIDummy(size_hint_max=(200, None), size_hint=(1, 0.6))
        self.box = UIBoxLayout(
            children=[
                UIDummy(size_hint_max=(50, None), size_hint=(1, 0.3)),
                UIDummy(size_hint_max=(100, None), size_hint=(1, 0.3)),
                self.ui_dummy,
            ],
            size_hint=(0.5, 0.5),
        )
        anchor.add(
            child=self.box,
            anchor_x="center_x",
            anchor_y="center_y",
        )


if __name__ == "__main__":
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
