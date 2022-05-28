import arcade
from arcade.gui import UIManager
from arcade.gui.widgets import UIDummy
from arcade.gui.widgets.layout import UIGridLayout, UIAnchorLayout


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        dummy1 = UIDummy(width=50, height=100)
        dummy2 = UIDummy(width=100, height=100)
        dummy3 = UIDummy(width=100, height=50)
        dummy4 = UIDummy(width=50, height=50)

        subject = (
            UIGridLayout(column_count=2, row_count=2)
            .with_border()
            .with_padding(left=10)
        )
        subject.add(dummy1, 0, 0)
        subject.add(dummy2, 0, 1)
        subject.add(dummy3, 1, 0)
        subject.add(dummy4, 1, 1)

        anchor = UIAnchorLayout()
        anchor.add(subject)

        self.manager.add(anchor)

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == "__main__":
    window = UIMockup()
    arcade.run()
