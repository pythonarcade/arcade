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

        dummy1 = UIDummy(width=100, height=100)
        dummy2 = UIDummy(width=50, height=50)
        dummy3 = UIDummy(width=50, height=50)
        dummy4 = UIDummy(width=100, height=100)
        dummy5 = UIDummy(width=200, height=100)
        dummy6 = UIDummy(width=100, height=200)

        subject = (
            UIGridLayout(
                column_count=3,
                row_count=3,
            )
            .with_border()
            .with_padding()
        )

        subject.add(dummy1, 0, 0)
        subject.add(dummy2, 0, 1)
        subject.add(dummy3, 1, 0)
        subject.add(dummy4, 1, 1)
        subject.add(dummy5, 0, 2, col_span=2)
        subject.add(dummy6, 2, 0, row_span=3)

        anchor = UIAnchorLayout()
        anchor.add(subject)

        self.manager.add(anchor)

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == "__main__":
    window = UIMockup()
    arcade.run()
