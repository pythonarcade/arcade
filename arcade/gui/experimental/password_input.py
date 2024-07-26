from __future__ import annotations

from typing import Optional

import arcade.color
from arcade.gui import Surface, UIEvent, UIInputText, UITextInputEvent
from arcade.types import Color, RGBOrA255


class UIPasswordInput(UIInputText):
    """A password input field. The text is hidden with asterisks."""

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 24,
        text: str = "",
        font_name=("Arial",),
        font_size: float = 12,
        text_color: RGBOrA255 = (0, 0, 0, 255),
        multiline=False,
        caret_color: RGBOrA255 = (0, 0, 0, 255),
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        **kwargs,
    ):
        replaced = "*" * len(text)
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            text=replaced,
            font_name=font_name,
            font_size=font_size,
            text_color=arcade.color.TRANSPARENT_BLACK,
            multiline=multiline,
            caret_color=caret_color,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs,
        )
        self._font_name = font_name
        self._font_size = font_size
        self._asterisk_color = Color.from_iterable(text_color)

    @property
    def text_color(self) -> Color:
        return self._asterisk_color

    @text_color.setter
    def text_color(self, new_value: RGBOrA255):
        self._asterisk_color = Color.from_iterable(new_value)

    def on_event(self, event: UIEvent) -> Optional[bool]:
        """Remove new lines from the input, which are not allowed in passwords."""
        if isinstance(event, UITextInputEvent):
            event.text = event.text.replace("\n", "").replace("\r", "")
        return super().on_event(event)

    def do_render(self, surface: Surface):
        """Override to render the text as asterisks."""
        asterisks = "*" * len(self.text)
        # FIXME: I fixed blinking, but broke efficiency and alignment :D
        with surface.activate():
            arcade.draw_text(
                asterisks,
                x=self.rect.left,
                y=self.rect.bottom,
                anchor_x="left",
                anchor_y="bottom",
                align="left",
                width=self.width,
                font_name=self._font_name,
                font_size=self._font_size,
                color=self._asterisk_color,
            )
        super().do_render(surface)
