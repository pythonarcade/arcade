import arcade
from arcade.gui import UIManager
from arcade.gui.widgets import UIDummy, UIAnchorWidget


class UIMockup(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.manager.add(UIAnchorWidget(
            child=UIDummy(color=arcade.color.RED),
            anchor_x="center_x",
            anchor_y="top",
        ))

        self.manager.add(UIAnchorWidget(
            child=UIDummy(color=arcade.color.BLUE),
            anchor_x="right",
            anchor_y="center_y",
        ))

        self.manager.add(UIAnchorWidget(
            child=UIDummy(color=arcade.color.GREEN),
            anchor_x="center_x",
            anchor_y="center_y",
        ))

        self.manager.add(UIAnchorWidget(
            child=UIDummy(color=arcade.color.YELLOW),
            anchor_x="left",
            anchor_y="bottom",
        ))

        self.manager.add(UIAnchorWidget(
            child=UIDummy(color=arcade.color.ORANGE),
            anchor_x="left",
            align_x=20,
            anchor_y="center_y",
        ))

        self.manager.add(UIAnchorWidget(
            child=UIDummy(color=arcade.color.ORANGE),
            anchor_x="right",
            align_x=-40,
            anchor_y="bottom",
            align_y=40,
        ))

    def on_draw(self):
        self.clear()
        self.manager.draw()


window = UIMockup()
arcade.run()
