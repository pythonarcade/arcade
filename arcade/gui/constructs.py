"""Constructs, are prepared widget combinations, you can use for common use-cases"""

from typing import Any

import arcade
from arcade import uicolor
from arcade.gui.events import UIOnActionEvent, UIOnClickEvent
from arcade.gui.mixins import UIMouseFilterMixin
from arcade.gui.nine_patch import NinePatchTexture
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from arcade.gui.widgets.text import UILabel, UITextArea


class UIMessageBox(UIMouseFilterMixin, UIAnchorLayout):
    """A simple dialog box that pops up a message with buttons to close.
    Subclass this class or overwrite the 'on_action' event handler with

    .. code-block:: python

        box = UIMessageBox(...)
        @box.event("on_action")
        def on_action(event: UIOnActionEvent):
            pass

    Args:
      width: Width of the message box
      height: Height of the message box
      message_text: Text to show as message to the user
      title: Title of the message box, displayed on the top
      buttons: List of strings, which are shown as buttons

    """

    def __init__(
        self,
        *,
        width: float,
        height: float,
        message_text: str,
        title: str | None = None,
        buttons=("Ok",),
    ):
        if not buttons:
            raise ValueError("At least a single value has to be available for `buttons`")

        super().__init__(size_hint=(1, 1))
        self.register_event_type("on_action")
        self.with_background(color=uicolor.GRAY_CONCRETE.replace(a=150))

        space = 20

        # setup frame which will act like the window
        frame = self.add(UIAnchorLayout(width=width, height=height, size_hint=None))

        frame.with_background(
            texture=NinePatchTexture(
                left=7,
                right=7,
                bottom=7,
                top=7,
                texture=arcade.load_texture(":resources:gui_basic_assets/window/panel_gray.png"),
            )
        )

        # setup title
        if title:
            title_label = frame.add(
                child=UILabel(
                    text=title,
                    font_size=16,
                    size_hint=(1, 0),
                    align="center",
                ),
                anchor_y="top",
            )
            title_label.with_padding(all=2, bottom=5)
            title_label.with_background(color=uicolor.DARK_BLUE_MIDNIGHT_BLUE)
            title_offset = title_label.height
        else:
            title_offset = 0

        # Setup text
        text_area = frame.add(
            child=UITextArea(
                text=message_text,
                width=width - space,
                height=height - space,
                text_color=arcade.color.BLACK,
            ),
            anchor_x="center",
            anchor_y="top",
            align_y=-(title_offset + space),
        )
        text_area.with_padding(all=10)

        # setup buttons
        button_group = UIBoxLayout(vertical=False, space_between=10)
        for button_text in buttons:
            button = UIFlatButton(text=button_text)
            button_group.add(button)
            button.on_click = self._on_choice  # type: ignore

        frame.add(
            child=button_group, anchor_x="right", anchor_y="bottom", align_x=-space, align_y=space
        )

    def _on_choice(self, event):
        if self.parent:
            self.parent.remove(self)
        self.dispatch_event("on_action", UIOnActionEvent(self, event.source.text))

    def on_action(self, event: UIOnActionEvent):
        """Called when button was pressed"""
        pass


class UIButtonRow(UIBoxLayout):
    """Places buttons in a row.

    Args:
        vertical: Whether the button row is vertical or not.
        align: Where to align the button row.
        size_hint: Tuple of floats (0.0 - 1.0) of how much space of the
            parent should be requested.
        size_hint_min: Min width and height in pixel.
        size_hint_max: Max width and height in pixel.
        space_between: The space between the children.
        callback: The callback function which will receive the text of
            the clicked button.
        button_factory: The factory to create the buttons. Default is py:class:`UIFlatButton`.
        **kwargs: Passed to UIBoxLayout
    """

    def __init__(
        self,
        *,
        vertical: bool = False,
        align: str = "center",
        size_hint: Any = (0, 0),
        size_hint_min: Any | None = None,
        size_hint_max: Any | None = None,
        space_between: int = 10,
        button_factory: type = UIFlatButton,
        **kwargs,
    ):
        super().__init__(
            vertical=vertical,
            align=align,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            space_between=space_between,
            **kwargs,
        )
        self.register_event_type("on_action")

        self.button_factory = button_factory

    def add_button(self, label: str, *, style=None, multiline=False, **kwargs):
        """Add a button to the row.

        Args:
            label: The text of the button.
            style: The style of the button.
            multiline: Whether the button is multiline or not.
            **kwargs: Passed to the button factory.
        """
        button = self.button_factory(text=label, style=style, multiline=multiline, **kwargs)
        button.on_click = self._on_click
        self.add(button)
        return button

    def on_action(self, event: UIOnActionEvent):
        """Called when button was pressed, override this method to handle button presses."""
        pass

    def _on_click(self, event: UIOnClickEvent):
        self.dispatch_event("on_action", UIOnActionEvent(self, event.source.text))
