import arcade
from arcade.gui import UIManager
from arcade.gui.widgets import UIDummy
from arcade.gui.widgets.layout import UIGridLayout, UIAnchorLayout


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        self.background_color = arcade.color.DARK_BLUE_GRAY

        dummy1 = UIDummy(width=100, height=100)
        dummy2 = UIDummy(width=50, height=50)
        dummy3 = UIDummy(width=50, height=50, size_hint=(.5, .5))
        dummy4 = UIDummy(width=100, height=100)
        dummy5 = UIDummy(width=200, height=100)
        dummy6 = UIDummy(width=100, height=300)

        subject = (
            UIGridLayout(
                column_count=3,
                row_count=3,
                size_hint=(.5, .5),
            )
            .with_border()
            .with_padding()
        )

        subject.add(child=dummy1, col_num=0, row_num=0)
        subject.add(child=dummy2, col_num=0, row_num=1)
        subject.add(child=dummy3, col_num=1, row_num=0)
        subject.add(child=dummy4, col_num=1, row_num=1)
        subject.add(child=dummy5, col_num=0, row_num=2, col_span=2)
        subject.add(child=dummy6, col_num=2, row_num=0, row_span=3)

        anchor = UIAnchorLayout()
        anchor.add(subject)

        self.manager.add(anchor)

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == "__main__":
    window = UIMockup()
    arcade.run()
