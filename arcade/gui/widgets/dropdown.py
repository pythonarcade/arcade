from typing import List

import arcade
from arcade.gui import (
    UIFlatButton,
    UIOnChangeEvent,
    UIOnClickEvent,
    UIWidget,
    UIBoxLayout,
)
from arcade.gui.widgets import UILayout


class UIDropdown(UILayout):
    DIVIDER = None

    def __init__(
            self, default: str = None, options: List[str] = None, style=None, **kwargs
    ):
        if style is None:
            style = {}

        # TODO handle if default value not in options or options empty
        if options is None:
            options = []
        self._options = options
        self._value = default

        super().__init__(style=style, **kwargs)

        # Setup button showing value
        self._default_button = UIFlatButton(
            text=self._value, width=self.width, height=self.height
        )

        self._default_button.on_click = self._on_button_click

        self._layout = UIBoxLayout()
        self._layout.visible = False
        self._update_options()

        # add children after super class setup
        self.add(self._default_button)
        self.add(self._layout)

        self.register_event_type("on_change")

        self.with_border(color=arcade.color.RED)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        old_value = self._value
        self._value = value
        self._default_button.text = self._value

        self._update_options()
        self.dispatch_event("on_change", UIOnChangeEvent(self, old_value, value))
        self.trigger_render()

    def _update_options(self):
        # generate options
        self._layout.clear()
        for option in self._options:
            if option == self.DIVIDER:
                self._layout.add(
                    UIWidget(width=self.width, height=2).with_background(
                        color=arcade.color.GRAY
                    )
                )
                continue

            button = self._layout.add(
                UIFlatButton(
                    text=option,
                    width=self.width,
                    height=self.height,
                    style={
                        "normal_bg": (55, 66, 81)
                        if self.value == option
                        else (95, 111, 131)
                    },
                )
            )
            button.on_click = self._on_option_click

    def _on_button_click(self, event: UIOnClickEvent):
        self._layout.visible = not self._layout.visible

    def _on_option_click(self, event: UIOnClickEvent):
        source: UIFlatButton = event.source
        self.value = source.text
        self._layout.visible = False

    def do_layout(self):
        self._default_button.rect = self.rect

        self._layout.fit_content()  # resize layout to contain widgets
        self._layout.rect = self._layout.rect.align_top(self.bottom - 2).align_left(
            self._default_button.left
        )

    def on_change(self, event: UIOnChangeEvent):
        pass
