"""
Example shows how to use UIAnchorWidget to position widgets on screen.
Dummy widgets indicate hovered, pressed and clicked.
"""

import arcade
from arcade.gui import UIManager, UIBoxLayout
from arcade.gui.widgets import UIDummy
from arcade.gui.widgets.layout import UIAnchorLayout


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        anchor = self.manager.add(UIAnchorLayout())

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

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_key_press(self, symbol: int, modifiers: int):

        print(self.ui_dummy.rect)
        print(self.box.rect)


window = UIMockup()
arcade.run()
