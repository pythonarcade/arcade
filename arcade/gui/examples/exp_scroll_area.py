"""
This example is a proof-of-concept for a UIScrollArea.

You can currently scroll through the UIScrollArea in the following ways:

* scrolling the mouse wheel
* dragging with middle mouse button

It currently needs the following improvements:

* A better API, including scroll direction control
* UIScrollBars

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.exp_scroll_area
"""

from __future__ import annotations

import arcade
from arcade import Window
from arcade.gui import UIManager, UIDummy, UIBoxLayout, UIFlatButton, UIInputText
from arcade.gui.experimental.scroll_area import UIScrollArea


class MyWindow(Window):
    def __init__(self):
        super().__init__()

        self.ui = UIManager()
        self.ui.enable()
        self.background_color = arcade.color.WHITE
        self.input = self.ui.add(UIInputText(x=450, y=300).with_border())

        self.scroll_area = UIScrollArea(x=100, y=100).with_border()
        self.ui.add(self.scroll_area)

        anchor = self.scroll_area.add(UIBoxLayout(width=300, height=300, space_between=20))
        anchor.add(UIDummy(height=50))
        anchor.add(UIFlatButton(text="Hello from scroll area", multiline=True))
        anchor.add(UIInputText().with_border())

    def on_draw(self):
        self.clear()
        self.ui.draw()


if __name__ == "__main__":
    MyWindow().run()
