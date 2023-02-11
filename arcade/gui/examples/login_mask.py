from typing import Optional

import arcade
from arcade.gui import UIManager, UIInputText, UIOnClickEvent, UIEvent
from arcade.gui.events import UITextEvent
from arcade.gui.surface import Surface
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIGridLayout, UIAnchorLayout
from arcade.gui.widgets.text import UILabel


class UIPasswordInput(UIInputText):
    def on_event(self, event: UIEvent) -> Optional[bool]:
        if isinstance(event, UITextEvent):
            event.text = event.text.replace("\n", "")  # remove new lines!
            event.text = event.text.replace("\r", "")  # remove new lines!
        return super().on_event(event)

    def do_render(self, surface: Surface):
        self.layout.begin_update()
        position = self.caret.position
        text = self.text
        self.text = "*" * len(self.text)
        super().do_render(surface)
        self.text = text
        self.caret.position = position
        self.layout.end_update()


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        grid = UIGridLayout(
            size_hint=(0, 0),  # wrap children
            row_count=3,  # user, pw and login button
            column_count=2,  # label and input field
            vertical_spacing=10,
            horizontal_spacing=5,
        )

        grid.add(UILabel(text="Username:"), col_num=0, row_num=0)
        self.username_input = grid.add(
            UIInputText(height=25), col_num=1, row_num=0
        ).with_border()

        grid.add(UILabel(text="Password:"), col_num=0, row_num=1)
        self.password_input = grid.add(
            UIPasswordInput(height=25), col_num=1, row_num=1
        ).with_border()

        self.login_button = grid.add(
            UIFlatButton(text="Login"), col_num=0, row_num=2, col_span=2
        )
        self.login_button.on_click = self.on_login

        anchor = UIAnchorLayout()  # to center grid on screen
        anchor.add(grid)

        self.manager.add(anchor)

    def on_login(self, event: UIOnClickEvent):
        print(
            f"User logged in with: {self.username_input.text} {self.password_input.text}"
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == "__main__":
    window = UIMockup()
    arcade.run()
