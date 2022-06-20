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

    :param float width: The width of the message box.
    :param float height: The height of the message box.
    :param str message_text: The message text to display.
    :param arcade.Color bg_color: The background color of the box.
    :param arcade.Texture bg_texture: The background texture of the box.
    :param tuple[str, ...] buttons: List of strings, which are shown as buttons.
    :param bool disappear: Whether the box should disappear after a set time or not.
    :param float disappear_time: The time before the box should disappear.
    :param int padding: The padding size of the box.
    :param Callable callback: The callback function which will receive the text of the
        clicked button.
    """

    def __init__(
        self,
        *,
        width: float,
        height: float,
        message_text: str,
        bg_color: arcade.Color = None,
        bg_texture: arcade.Texture = None,
        buttons: Tuple[str, ...] = ("Ok",),
        disappear: bool = False,
        disappear_time: float = 3,
        padding: int = 10,
        callback: Callable = None,
    ) -> None:
        super().__init__(size_hint=(1, 1))

        # Store a few variables needed for this class
        self._callback: Callable = callback  # type: ignore
        self._disappear: bool = disappear
        self._disappear_time_counter: float = disappear_time

        # Set up the box which will act like a window
        message_box = self.add(UIAnchorLayout(width=width, height=height))
        message_box.with_padding(all=padding)
        message_box.with_background(color=bg_color, texture=bg_texture)
        message_box.add(
            child=UITextArea(
                text=message_text,
                width=width - padding,
                height=height - padding,
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
