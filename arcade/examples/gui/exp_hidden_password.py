"""Creating a hidden password field

This example demonstrates how to create a custom text input
which hides the contents behind a custom character, as often
required for login screens.

Due to a bug in the current version of pyglet, the example uses ENTER to switch
fields instead of TAB. This will be fixed in future versions.
(https://github.com/pyglet/pyglet/issues/1197)

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.exp_hidden_password
"""

import arcade
from arcade.gui import UIInputText, UIOnClickEvent, UIView
from arcade.gui.experimental.password_input import UIPasswordInput
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIGridLayout, UIAnchorLayout
from arcade.gui.widgets.text import UILabel
from arcade import resources

# Load kenny fonts shipped with arcade
resources.load_kenney_fonts()


class MyView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_BELIZE_HOLE

        grid = UIGridLayout(
            size_hint=(0, 0),  # wrap children
            row_count=5,  # title | user, pw | login button
            column_count=2,  # label and input field
            vertical_spacing=10,
            horizontal_spacing=5,
        )
        grid.with_padding(all=50)
        grid.with_background(color=arcade.uicolor.GREEN_GREEN_SEA)

        title = grid.add(
            UILabel(text="Login", width=150, font_size=20, font_name="Kenney Future"),
            column=0,
            row=0,
            column_span=2,
        )
        title.with_padding(bottom=20)

        grid.add(UILabel(text="Username:", width=80, font_name="Kenney Future"), column=0, row=1)
        self.username_input = grid.add(
            UIInputText(width=150, font_name="Kenney Future"), column=1, row=1
        )

        grid.add(UILabel(text="Password:", width=80, font_name="Kenney Future"), column=0, row=2)
        self.password_input = grid.add(
            UIPasswordInput(width=150, font_name="Kenney Future"), column=1, row=2
        )
        self.password_input.with_background(color=arcade.uicolor.GREEN_GREEN_SEA)
        # set background to prevent full render on blinking caret

        self.login_button = grid.add(
            UIFlatButton(text="Login", height=30, width=150, size_hint=(1, None)),
            column=0,
            row=3,
            column_span=2,
        )
        self.login_button.on_click = self.on_login

        # add warning label
        self.warning_label = grid.add(
            UILabel(
                text="Use 'TAB' to switch fields, then enter to login",
                width=150,
                font_size=10,
                font_name="Kenney Future",
            ),
            column=0,
            row=4,
            column_span=2,
        )

        anchor = UIAnchorLayout()  # to center grid on screen
        anchor.add(grid)

        self.add_widget(anchor)

        # activate username input field
        self.username_input.activate()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        # if username field active, switch fields with enter
        if self.username_input.active:
            if symbol == arcade.key.TAB:
                self.username_input.deactivate()
                self.password_input.activate()
                return True
            elif symbol == arcade.key.ENTER:
                self.username_input.deactivate()
                self.on_login(None)
                return True
        # if password field active, login with enter
        elif self.password_input.active:
            if symbol == arcade.key.TAB:
                self.username_input.activate()
                self.password_input.deactivate()
                return True
            elif symbol == arcade.key.ENTER:
                self.password_input.deactivate()
                self.on_login(None)
                return True
        return False

    def on_login(self, event: UIOnClickEvent | None):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        print(f"User logged in with: {username} {password}")


def main():
    window = arcade.Window(title="GUI Example: Hidden Password")
    window.show_view(MyView())
    window.run()


if __name__ == "__main__":
    main()
