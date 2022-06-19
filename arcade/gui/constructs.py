"""
Constructs, are prepared widget combinations, you can use for common use-cases
"""
from typing import Callable, Tuple

import arcade
from arcade.gui.events import UIBoxDisappearEvent
from arcade.gui.mixins import UIMouseFilterMixin
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIBoxLayout, UIAnchorLayout
from arcade.gui.widgets.text import UITextArea


class UIMessageBox(UIMouseFilterMixin, UIAnchorLayout):
    """
    A simple dialog box that displays a message to the user.

    :param width float: The width of the message box.
    :param height float: The height of the message box.
    :param message_text str: The message text to display.
    :param buttons tuple[str, ...]: List of strings, which are shown as buttons.
    :param disappear bool: Whether the box should disappear after a set time or not.
    :param disappear_time float: The time before the box should disappear.
    :param callback Callable: The callback function which will receive the text of the
        clicked button.
    """

    def __init__(
        self,
        *,
        width: float,
        height: float,
        message_text: str,
        background: arcade.Texture = arcade.load_texture(
            ":resources:gui_basic_assets/window/grey_panel.png"
        ),
        buttons: Tuple[str, ...] = ("Ok",),
        disappear: bool = False,
        disappear_time: float = 3,
        callback: Callable = None,
    ) -> None:
        super().__init__(size_hint=(1, 1))

        # Store a few variables needed for this class
        self._callback: Callable = callback  # type: ignore
        self._disappear: bool = disappear
        self._disappear_time_counter: float = disappear_time
        padding_size = 10

        # Set up the box which will act like a window
        message_box = self.add(UIAnchorLayout(width=width, height=height))
        message_box.with_padding(all=padding_size)
        message_box.with_background(texture=background)
        message_box.add(
            child=UITextArea(
                text=message_text,
                width=width - padding_size,
                height=height - padding_size,
                text_color=arcade.color.BLACK,
            ),
            anchor_x="center",
            anchor_y="top",
        )

        # Set up buttons
        if buttons:
            button_group = UIBoxLayout(vertical=False, space_between=10)
            for button_text in buttons:
                button = UIFlatButton(text=button_text)
                button.on_click = self.on_ok  # type: ignore
                button_group.add(button)

            message_box.add(
                child=button_group,
                anchor_x="right",
                anchor_y="bottom",
            )

    def on_update(self, delta_time: float) -> None:
        if self._disappear:
            self._disappear_time_counter -= delta_time

            # Check if the box should disappear
            if self._disappear_time_counter <= 0:
                self.on_ok(UIBoxDisappearEvent(self))

    def on_ok(self, event) -> None:
        if self.parent is not None:
            self.parent.remove(self)

        result_text = ""
        if hasattr(event.source, "text"):
            result_text = event.source.text

        if self._callback is not None:
            self._callback(result_text)
