"""
Creating sidebar-like layouts with UIBoxLayout

This example creates left, right, top, and bottom bars by combining the following:

* Placing box layouts inside other box layouts (see the box_layouts example)
* Size hints (see the size_hints example)

To turn this into a real UI, you  can replace the UIDummy widgets with layout
objects which contain other widgets.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.side_bars_with_box_layout
"""

from __future__ import annotations

import arcade
from arcade.gui import UIManager, UIDummy, UIBoxLayout


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        v_box = UIBoxLayout(size_hint=(1, 1))

        top_bar = UIDummy(height=50, size_hint=(1, 0), size_hint_min=(None, 50))
        v_box.add(top_bar)

        h_box = UIBoxLayout(size_hint=(1, 1), vertical=False)
        left_bar = UIDummy(width=50, size_hint=(0, 1), size_hint_min=(50, None))
        h_box.add(left_bar)
        center_area = UIDummy(size_hint=(1, 1))
        h_box.add(center_area)
        right_bar = UIDummy(size_hint=(0, 1), size_hint_min=(100, None))
        h_box.add(right_bar)
        v_box.add(h_box)

        bottom_bar = UIDummy(height=100, size_hint=(1, 0), size_hint_min=(None, 100))
        v_box.add(bottom_bar)

        self.ui.add(v_box)

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        self.ui.disable()

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_draw(self):
        self.clear()
        self.ui.draw()


if __name__ == "__main__":
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
