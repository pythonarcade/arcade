"""Example of using experimental UIRestrictedInputText.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.exp_restricted_input
"""

import arcade
from arcade.gui import UIAnchorLayout, UIBoxLayout, UIView
from arcade.gui.experimental.restricted_input import UIIntInput


class MyView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_BELIZE_HOLE

        root = self.ui.add(UIAnchorLayout())
        bars = root.add(UIBoxLayout(space_between=10))

        # UIWidget based progress bar
        self.input_field = UIIntInput(width=300, height=40, font_size=22)
        bars.add(self.input_field)


def main():
    window = arcade.Window(antialiasing=False)
    window.show_view(MyView())
    arcade.run()


if __name__ == "__main__":
    main()
