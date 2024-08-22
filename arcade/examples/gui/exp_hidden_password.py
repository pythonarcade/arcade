"""Creating a hidden password field

This example demonstrates how to create a custom text input
which hides the contents behind a custom character, as often
required for login screens

If arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.exp_hidden_password
"""

from __future__ import annotations

import arcade
from arcade.gui import UIManager, UIInputText, UIOnClickEvent
from arcade.gui.experimental.password_input import UIPasswordInput
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIGridLayout, UIAnchorLayout
from arcade.gui.widgets.text import UILabel


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        grid = UIGridLayout(
            size_hint=(0, 0),  # wrap children
            row_count=3,  # user, pw and login button
            column_count=2,  # label and input field
            vertical_spacing=10,
            horizontal_spacing=5,
        )

        grid.add(UILabel(text="Username:", width=80), column=0, row=0)
        self.username_input = grid.add(UIInputText(), column=1, row=0)

        grid.add(UILabel(text="Password:", width=80), column=0, row=1)
        self.password_input = grid.add(UIPasswordInput(), column=1, row=1)

        self.login_button = grid.add(UIFlatButton(text="Login"), column=0, row=2, column_span=2)
        self.login_button.on_click = self.on_login

        anchor = UIAnchorLayout()  # to center grid on screen
        anchor.add(grid)

        self.ui.add(anchor)

    def on_login(self, event: UIOnClickEvent):
        print(f"User logged in with: {self.username_input.text} {self.password_input.text}")

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
    window = arcade.Window(title="GUI Example: Hidden Password")
    window.show_view(MyView())
    window.run()
