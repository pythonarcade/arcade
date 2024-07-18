from __future__ import annotations

from copy import deepcopy
from typing import Optional, Union

from pyglet.event import EVENT_HANDLED

import arcade
from arcade.gui import UIEvent, UIMousePressEvent
from arcade.gui.events import UIOnChangeEvent, UIOnClickEvent
from arcade.gui.ui_manager import UIManager
from arcade.gui.widgets import UILayout, UIWidget
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIBoxLayout


class _UIDropdownOverlay(UIBoxLayout):
    """
    Represents the dropdown options overlay.

    Currently only handles closing the overlay when clicked outside of the options.
    """

    # TODO move also options logic to this class

    def show(self, manager: UIManager):
        manager.add(self, layer=UIManager.OVERLAY_LAYER)

    def hide(self):
        """Hide the overlay."""
        self.parent.remove(self)

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if isinstance(event, UIMousePressEvent):
            # Click outside of dropdown options
            if not self.rect.point_in_rect((event.x, event.y)):
                self.hide()
                return EVENT_HANDLED
        return super().on_event(event)


class UIDropdown(UILayout):
    """
    A dropdown layout. When clicked displays a list of options provided.

    Triggers an event when an option is clicked, the event can be read by

    .. code:: py

        dropdown = Dropdown()

        @dropdown.event()
        def on_change(event: UIOnChangeEvent):
            print(event.old_value, event.new_value)

    :param x: x coordinate of bottom left
    :param y: y coordinate of bottom left
    :param width: Width of each of the option.
    :param height: Height of each of the option.
    :param default: The default value shown.
    :param options: The options displayed when the layout is clicked.
    :param style: Used to style the dropdown.
    """

    DIVIDER = None

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 20,
        default: Optional[str] = None,
        options: Optional[list[Union[str, None]]] = None,
        style=None,
        **kwargs,
    ):
        if style is None:
            style = {}

        # TODO handle if default value not in options or options empty
        if options is None:
            options = []
        self._options = options
        self._value = default

        super().__init__(x=x, y=y, width=width, height=height, style=style, **kwargs)

        # Setup button showing value
        self._default_button = UIFlatButton(
            text=self._value or "", width=self.width, height=self.height
        )

        self._default_button.on_click = self._on_button_click  # type: ignore

        self._overlay = _UIDropdownOverlay()
        self._update_options()

        # add children after super class setup
        self.add(self._default_button)

        self.register_event_type("on_change")  # type: ignore  # https://github.com/pyglet/pyglet/pull/1173  # noqa

        self.with_border(color=arcade.color.RED)

    @property
    def value(self) -> Optional[str]:
        """Current selected option."""
        return self._value

    @value.setter
    def value(self, value: Optional[str]):
        """Change the current selected option to a new option."""
        old_value = self._value
        self._value = value
        self._default_button.text = self._value or ""

        self._update_options()
        self.dispatch_event("on_change", UIOnChangeEvent(self, old_value, value))
        self.trigger_render()

    def _update_options(self):
        # generate options
        self._overlay.clear()

        # is there another way then deepcopy, does it matter?
        # ("premature optimization is the root of all evil")
        active_style = deepcopy(UIFlatButton.DEFAULT_STYLE)
        active_style["normal"]["bg"] = (55, 66, 81)

        for option in self._options:
            if option is None:  # None = UIDropdown.DIVIDER, required by pyright
                self._overlay.add(
                    UIWidget(width=self.width, height=2).with_background(color=arcade.color.GRAY)
                )
                continue
            else:
                button = self._overlay.add(
                    UIFlatButton(
                        text=option,
                        width=self.width,
                        height=self.height,
                        style=active_style if self.value == option else UIFlatButton.DEFAULT_STYLE,
                    )
                )
            button.on_click = self._on_option_click

    def _find_ui_manager(self):
        # search tree for UIManager
        parent = self.parent
        while isinstance(parent, UIWidget):
            #
            parent = parent.parent

        return parent if isinstance(parent, UIManager) else None

    def _show_overlay(self):
        manager = self._find_ui_manager()
        if manager is None:
            raise Exception("UIDropdown could not find UIManager in its parents.")

        self._overlay.show(manager)

    def _on_button_click(self, _: UIOnClickEvent):
        self._show_overlay()

    def _on_option_click(self, event: UIOnClickEvent):
        source: UIFlatButton = event.source
        self.value = source.text
        self._overlay.hide()

    def do_layout(self):
        self._default_button.rect = self.rect

        # resize layout to contain widgets
        overlay = self._overlay
        rect = overlay.rect
        if overlay.size_hint_min is not None:
            rect = rect.resize(*overlay.size_hint_min)

        self._overlay.rect = rect.align_top(self.bottom - 2).align_left(self._default_button.left)

    def on_change(self, event: UIOnChangeEvent):
        """
        To be implemented by the user, triggered when the current selected value
        is changed to a different option.
        """
        pass
