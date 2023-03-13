from itertools import cycle

import arcade
from arcade.gui import UIManager, UIOnClickEvent
from arcade.gui.constructs import UIButtonRow
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIAnchorLayout

STYLES = [
    UIFlatButton.DEFAULT_STYLE,
    {  # RED
        "normal": UIFlatButton.UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            bg=arcade.color.RED,
            border=None,
            border_width=0,
        ),
        "hover": UIFlatButton.UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            bg=arcade.color.RED,
            border=arcade.color.RED_ORANGE,
            border_width=2,
        ),
        "press": UIFlatButton.UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.BLACK,
            bg=arcade.color.RED_ORANGE,
            border=arcade.color.RED_DEVIL,
            border_width=2,
        ),
        "disabled": UIFlatButton.UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.GRAY,
            bg=arcade.color.DARK_SLATE_GRAY,
            border=arcade.color.DAVY_GREY,
            border_width=2,
        ),
    },
    {  # BLUE
        "normal": UIFlatButton.UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            bg=arcade.color.BLUE,
            border=None,
            border_width=0,
        ),
        "hover": UIFlatButton.UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            bg=arcade.color.BLUE,
            border=arcade.color.BLUE_BELL,
            border_width=2,
        ),
        "press": UIFlatButton.UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.BLACK,
            bg=arcade.color.BLUE_BELL,
            border=arcade.color.BLUE_GRAY,
            border_width=2,
        ),
        "disabled": UIFlatButton.UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.GRAY,
            bg=arcade.color.GRAY_BLUE,
            border=arcade.color.DAVY_GREY,
            border_width=2,
        ),
    },
]


class DemoWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)

        # Init UIManager
        self.manager = UIManager()
        self.manager.enable()

        # Set background
        self.background_color = arcade.color.DARK_BLUE_GRAY

        # Use a UIAnchorWidget to place the UILabels in the top left corner
        anchor = self.manager.add(UIAnchorLayout())
        row = anchor.add(UIButtonRow(button_factory=UIFlatButton))

        button1 = row.add_button("Click me to switch style", multiline=True)

        style_options = cycle(STYLES)
        next(style_options)  # skip default style in first round

        @button1.event("on_click")
        def change_style(event: UIOnClickEvent):
            btn: UIFlatButton = event.source
            btn.style = next(style_options)
            btn.trigger_render()

        button2 = row.add_button("Toggle disable", multiline=True)

        @button2.event("on_click")
        def toggle(*_):
            button1.disabled = not button1.disabled

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == "__main__":
    DemoWindow().run()
