from random import choice
from typing import Any

import arcade
from arcade.experimental.uistyle import UIFlatButtonStyle_default, UIFlatButtonStyle
from arcade.gui import UIManager, UIOnClickEvent
from arcade.gui.events import UIOnActionEvent
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout

STYLES = [
    UIFlatButtonStyle_default,
    {  # RED
        "normal": UIFlatButtonStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            bg=arcade.color.RED,
            border=None,
            border_width=0,
        ),
        "hover": UIFlatButtonStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            bg=arcade.color.RED,
            border=arcade.color.RED_ORANGE,
            border_width=2,
        ),
        "press": UIFlatButtonStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.BLACK,
            bg=arcade.color.RED_ORANGE,
            border=arcade.color.RED_DEVIL,
            border_width=2,
        ),
        "disabled": UIFlatButtonStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.GRAY,
            bg=arcade.color.DARK_SLATE_GRAY,
            border=arcade.color.DAVY_GREY,
            border_width=2,
        )
    },
    {  # BLUE
        "normal": UIFlatButtonStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            bg=arcade.color.BLUE,
            border=None,
            border_width=0,
        ),
        "hover": UIFlatButtonStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            bg=arcade.color.BLUE,
            border=arcade.color.BLUE_BELL,
            border_width=2,
        ),
        "press": UIFlatButtonStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.BLACK,
            bg=arcade.color.BLUE_BELL,
            border=arcade.color.BLUE_GRAY,
            border_width=2,
        ),
        "disabled": UIFlatButtonStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.GRAY,
            bg=arcade.color.GRAY_BLUE,
            border=arcade.color.DAVY_GREY,
            border_width=2,
        )
    }
]


class UIButtonRow(UIBoxLayout):
    """
    Places buttons in a row.
    :param bool vertical: Whether the button row is vertical or not.
    :param str align: Where to align the button row.
    :param Any size_hint: Tuple of floats (0.0 - 1.0) of how much space of the parent should be requested.
    :param size_hint_min: Min width and height in pixel.
    :param size_hint_max: Max width and height in pixel.
    :param int space_between: The space between the children.
    :param Any style: Not used.
    :param Tuple[str, ...] button_labels: The labels for the buttons.
    :param Callable callback: The callback function which will receive the text of the clicked button.
    """

    def __init__(
        self,
        vertical: bool = False,
        align: str = "center",
        size_hint: Any = (0, 0),
        size_hint_min: Any = None,
        size_hint_max: Any = None,
        space_between: int = 10,
        style: Any = None,
        button_factory: type = UIFlatButton,
    ):
        super().__init__(
            vertical=vertical,
            align=align,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            space_between=space_between,
            style=style,

        )
        self.register_event_type("on_action")

        self.button_factory = button_factory

    def add_button(self, label: str, *, on_click=None, style=None, ):
        button = self.button_factory(text=label, style=style)
        button.on_click = self._on_click  # type: ignore
        self.add(button)

        if on_click:
            # Add on_click callback as event handler
            button.event("on_click")(on_click)

        return button

    def on_action(self, event: UIOnActionEvent):
        pass

    def _on_click(self, event: UIOnClickEvent):
        self.dispatch_event("on_action", UIOnActionEvent(event.source, event.source.text))


class DemoWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)

        # Init UIManager
        self.manager = UIManager()
        self.manager.enable()

        # Set background
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Use a UIAnchorWidget to place the UILabels in the top left corner
        anchor = self.manager.add(UIAnchorLayout())
        row = anchor.add(UIButtonRow(button_factory=UIFlatButton))

        def on_click(event: UIOnClickEvent):
            event.source.style = choice(STYLES)
            btn: UIFlatButton = event.source
            btn.trigger_render()

        button = row.add_button("Click me to switch style", on_click=on_click)

        def toggle(*_):
            button.disabled = not button.disabled

        row.add_button("Toggle disable", on_click=toggle)

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == '__main__':
    DemoWindow().run()
