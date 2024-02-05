"""
Uses the experimental UIConstraintsLayout
"""

from math import sin

import arcade
from arcade import Window, easing
from arcade.gui import UIManager, UIDummy
from arcade.experimental.gui_constraints_layout import (
    UIConstraintsLayout,
    RelativeConstraint,
    UIWidgetAttrMixin,
    EasingConstraint,
    EasingValueConstraint,
    TimedConstraint,
)


class MyDummy(UIWidgetAttrMixin, UIDummy):
    pass


class MyWindow(Window):
    def __init__(self):
        super().__init__()

        self.ui = UIManager()
        self.ui.enable()
        self.background_color = arcade.color.WHITE

        # code to reproduce the error goes here
        root = self.ui.add(UIConstraintsLayout(width=100, height=100))

        # Center on screen
        root.add(
            MyDummy(width=100, height=100),
            center_y=RelativeConstraint(self, "height", factor=0.5),
            center_x=RelativeConstraint(self, "width", factor=0.5),
        )

        # Simple easing, which only provides a factor
        root.add(
            MyDummy(width=100, height=100),
            center_y=RelativeConstraint(self, "height", factor=0.3)
            * EasingConstraint(seconds=2),
            center_x=RelativeConstraint(self, "width", factor=0.9),
        )

        # Easing with start end value, which can also be a constraint
        # start from center_x 0 to center of screen
        first = root.add(
            MyDummy(width=100, height=100),
            center_y=RelativeConstraint(self, "height", factor=0.2),
            center_x=EasingValueConstraint(
                start_value=50,
                end_value=RelativeConstraint(self, "width", factor=0.5),
                ease_function=easing.ease_out_bounce,
                seconds=2,
            ),
        )

        # Second widget, just following the first one
        root.add(
            MyDummy(width=100, height=100),
            center_x=RelativeConstraint(first, "center_x", offset=-150),
            center_y=RelativeConstraint(first, "center_y"),
            height=TimedConstraint(func=lambda t: sin(t * 2)) * 50 + 100,
        )

    def on_draw(self):
        arcade.start_render()
        self.ui.draw()


if __name__ == "__main__":
    MyWindow().run()
