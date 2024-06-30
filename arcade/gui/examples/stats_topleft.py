"""
Displaying stats in the window's top left corner

This example displays numerical stats with labels by using the following:

* A UILabel subclass which uses string formatting to convert numbers
* Vertical UIBoxLayouts to hold the quantity labels & number columns

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.stats_topleft
"""

from __future__ import annotations

import arcade
from arcade.gui import UIManager, UILabel, UIBoxLayout
from arcade.gui.widgets.layout import UIAnchorLayout


class UINumberLabel(UILabel):
    _value: float = 0

    def __init__(self, value=0, format="{value:.0f}", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = format
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.text = self.format.format(value=value)
        self.fit_content()


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        # Init UIManager
        self.ui = UIManager()

        # Create value labels
        self.timer = UINumberLabel(value=20, align="right", size_hint_min=(30, 20))
        wood = UINumberLabel(10, align="right", size_hint_min=(30, 20))
        stone = UINumberLabel(20, align="right", size_hint_min=(30, 20))
        food = UINumberLabel(30, align="right", size_hint_min=(30, 20))

        # Create a vertical BoxGroup to align labels
        self.columns = UIBoxLayout(
            vertical=False,
            children=[
                # Create one vertical UIBoxLayout per column and add the labels
                UIBoxLayout(
                    vertical=True,
                    children=[
                        UILabel(text="Time:", align="left", width=50),
                        UILabel(text="Wood:", align="left", width=50),
                        UILabel(text="Stone:", align="left", width=50),
                        UILabel(text="Food:", align="left", width=50),
                    ],
                ),
                # Create one vertical UIBoxLayout per column and add the labels
                UIBoxLayout(vertical=True, children=[self.timer, wood, stone, food]),
            ],
        )

        # Use a UIAnchorWidget to place the UILabels in the top left corner
        anchor = self.ui.add(UIAnchorLayout())
        anchor.add(align_x=10, anchor_x="left", align_y=-10, anchor_y="top", child=self.columns)

    def on_update(self, delta_time: float):
        self.timer.value += delta_time

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
