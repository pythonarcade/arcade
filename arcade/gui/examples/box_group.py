import arcade
from arcade.gui import UIManager
from arcade.gui.widgets import UIDummy, UIAnchorWidget, UIBoxLayout, UISpace


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.v_box = UIBoxLayout(
            x=0, y=0,
            children=[
                UIDummy(width=200, color=arcade.color.RED).with_space_around(bottom=20),
                UIDummy(width=200, color=arcade.color.YELLOW).with_space_around(bottom=20),
                UIDummy(width=200, color=arcade.color.GREEN).with_space_around(bottom=20),
            ])
        self.manager.add(
            UIAnchorWidget(
                anchor_x="center_x",
                # x_align=-50,
                anchor_y="center_y",
                # y_align=-20,
                child=self.v_box)
        )

        self.h_box = UIBoxLayout(
            vertical=False,
            children=[
                UIDummy(width=100, color=arcade.color.RED),
                UISpace(width=20, height=100),
                UIDummy(width=50, color=arcade.color.YELLOW).with_space_around(right=30),
                UIDummy(width=20, color=arcade.color.GREEN),
            ])

        self.manager.add(
            UIAnchorWidget(
                align_x=20,
                anchor_x="left",
                align_y=20,
                anchor_y="bottom",
                child=self.h_box.with_border())
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()


window = UIMockup()
arcade.run()
