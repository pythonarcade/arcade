"""
Constructs, are prepared widget combinations, you can use for common use-cases
"""

from __future__ import annotations

from typing import Any, Optional

import arcade
from arcade.gui.events import UIOnActionEvent, UIOnClickEvent
from arcade.gui.mixins import UIMouseFilterMixin
from arcade.gui.nine_patch import NinePatchTexture
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from arcade.gui.widgets.text import UITextArea


class UIMessageBox(UIMouseFilterMixin, UIAnchorLayout):
    """
    A simple dialog box that pops up a message with buttons to close.
    Subclass this class or overwrite the 'on_action' event handler with

    .. code-block:: python

        box = UIMessageBox(...)
        @box.event("on_action")
        def on_action(event: UIOnActionEvent):
            pass


    :param width: Width of the message box
    :param height: Height of the message box
    :param message_text: Text to show as message to the user
    :param buttons: List of strings, which are shown as buttons
    """

    def __init__(
        self,
        *,
        width: float,
        height: float,
        message_text: str,
        buttons=("Ok",),
    ):
        if not buttons:
            raise ValueError("At least a single value has to be available for `buttons`")

        super().__init__(size_hint=(1, 1))
        self.register_event_type("on_action")  # type: ignore  # https://github.com/pyglet/pyglet/pull/1173  # noqa

        space = 20

        # setup frame which will act like the window
        frame = self.add(UIAnchorLayout(width=width, height=height, size_hint=None))
        frame.with_padding(all=space)

        frame.with_background(
            texture=NinePatchTexture(
                left=7,
                right=7,
                bottom=7,
                top=7,
                texture=arcade.load_texture(":resources:gui_basic_assets/window/grey_panel.png"),
            )
        )

        # Setup text
        frame.add(
            child=UITextArea(
                text=message_text,
                width=width - space,
                height=height - space,
                text_color=arcade.color.BLACK,
            ),
            anchor_x="center",
            anchor_y="top",
        )

        # setup buttons
        button_group = UIBoxLayout(vertical=False, space_between=10)
        for button_text in buttons:
            button = UIFlatButton(text=button_text)
            button_group.add(button)
            button.on_click = self._on_choice  # type: ignore

        frame.add(
            child=button_group,
            anchor_x="right",
            anchor_y="bottom",
        )

    def _on_choice(self, event):
        if self.parent:
            self.parent.remove(self)
        self.dispatch_event("on_action", UIOnActionEvent(self, event.source.text))

    def on_action(self, event: UIOnActionEvent):
        """Called when button was pressed"""
        pass


class UIButtonRow(UIBoxLayout):
    """
    Places buttons in a row.

    :param vertical: Whether the button row is vertical or not.
    :param align: Where to align the button row.
    :param size_hint: Tuple of floats (0.0 - 1.0) of how much space of the parent
        should be requested.
    :param size_hint_min: Min width and height in pixel.
    :param size_hint_max: Max width and height in pixel.
    :param space_between: The space between the children.
    :param style: Not used.
    :param Tuple[str, ...] button_labels: The labels for the buttons.
    :param callback: The callback function which will receive the text of the clicked button.
    """

    def __init__(
        self,
        *,
        vertical: bool = False,
        align: str = "center",
        size_hint: Any = (0, 0),
        size_hint_min: Optional[Any] = None,
        size_hint_max: Optional[Any] = None,
        space_between: int = 10,
        style: Optional[Any] = None,
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
        self.register_event_type("on_action")  # type: ignore  # https://github.com/pyglet/pyglet/pull/1173  # noqa

        self.button_factory = button_factory

    def add_button(
        self,
        label: str,
        *,
        style=None,
        multiline=False,
    ):
        button = self.button_factory(text=label, style=style, multiline=multiline)
        button.on_click = self._on_click  # type: ignore
        self.add(button)
        return button

    def on_action(self, event: UIOnActionEvent):
        pass

    def _on_click(self, event: UIOnClickEvent):
        self.dispatch_event("on_action", UIOnActionEvent(self, event.source.text))
