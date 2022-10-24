import arcade
from arcade.gui import UIManager, UIBoxLayout
from arcade.gui.widgets import UIDummy, UISpace
from arcade.gui.widgets.layout import UIAnchorLayout


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        anchor = self.manager.add(UIAnchorLayout())

        self.v_box = UIBoxLayout(
            children=[
                UIDummy(width=200, color=arcade.color.RED),
                UIDummy(width=200, color=arcade.color.YELLOW),
                UIDummy(width=200, color=arcade.color.GREEN),
            ],
            space_between=20,
        )
        anchor.add(
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
                UIDummy(width=20, color=arcade.color.GREEN),
            ],
        )
        anchor.add(
            child=self.h_box.with_border(),
            align_x=20,
            anchor_x="left",
            align_y=20,
            anchor_y="bottom",
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()


window = UIMockup()
arcade.run()
