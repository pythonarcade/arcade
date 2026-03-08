from copy import deepcopy

from pyglet.event import EVENT_HANDLED

import arcade
from arcade import uicolor
from arcade.gui import UIEvent, UIMousePressEvent
from arcade.gui.events import UIControllerButtonPressEvent, UIOnChangeEvent, UIOnClickEvent
from arcade.gui.experimental import UIScrollArea
from arcade.gui.experimental.focus import UIFocusMixin
from arcade.gui.experimental.scroll_area import UIScrollBar
from arcade.gui.ui_manager import UIManager
from arcade.gui.widgets import UILayout, UIWidget
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIBoxLayout


class _UIDropdownOverlay(UIFocusMixin, UIBoxLayout):
    """Represents the dropdown options overlay with scroll support.

    Contains a UIScrollArea with the option buttons and a UIScrollBar
    for navigating when options exceed the maximum height.
    """

    SCROLL_BAR_WIDTH = 15

    def __init__(
        self,
        max_height: float = 200,
        invert_scroll: bool = False,
        scroll_speed: float = 15.0,
        show_scroll_bar: bool = False,
    ):
        # Horizontal layout: [scroll_area | scroll_bar]
        # size_hint=None prevents UIManager from overriding the rect
        # that UIDropdown.do_layout explicitly sets.
        super().__init__(vertical=False, align="top", size_hint=None)
        self._max_height = max_height
        self._show_scroll_bar = show_scroll_bar

        self._options_layout = UIBoxLayout(size_hint=(1, 0))
        self._scroll_area = UIScrollArea(
            width=100,
            height=100,
            canvas_size=(100, 100),
            size_hint=(1, 1),
        )
        self._scroll_area.invert_scroll = invert_scroll
        self._scroll_area.scroll_speed = scroll_speed
        self._scroll_area.add(self._options_layout)

        super().add(self._scroll_area)

        if show_scroll_bar:
            self._scroll_bar = UIScrollBar(self._scroll_area, vertical=True)
            self._scroll_bar.size_hint = (None, 1)
            self._scroll_bar.rect = self._scroll_bar.rect.resize(width=self.SCROLL_BAR_WIDTH)
            super().add(self._scroll_bar)

    def add_option(self, widget: UIWidget) -> UIWidget:
        """Add an option widget to the options layout."""
        return self._options_layout.add(widget)

    def clear_options(self):
        """Clear all options and reset scroll position."""
        self._options_layout.clear()
        self._scroll_area.scroll_y = 0

    def show(self, manager: UIManager | UIScrollArea):
        manager.add(self, layer=UIManager.OVERLAY_LAYER)

    def hide(self):
        """Hide the overlay."""
        self.set_focus(None)
        if self.parent:
            self.parent.remove(self)

    def on_event(self, event: UIEvent) -> bool | None:
        if isinstance(event, UIMousePressEvent):
            # Click outside of dropdown options
            if not self.rect.point_in_rect((event.x, event.y)):
                self.hide()
                return EVENT_HANDLED

        if isinstance(event, UIControllerButtonPressEvent):
            # TODO find a better and more generic way to handle controller events for this
            if event.button == "b":
                self.hide()
                return EVENT_HANDLED

        return super().on_event(event)


class UIDropdown(UILayout):
    """A dropdown layout. When clicked displays a list of options provided.

    Triggers an event when an option is clicked, the event can be read by

    .. code:: py

        dropdown = Dropdown()

        @dropdown.event()
        def on_change(event: UIOnChangeEvent):
            print(event.old_value, event.new_value)

    Args:
        x: x coordinate of bottom left
        y: y coordinate of bottom left
        width: Width of each of the option.
        height: Height of each of the option.
        default: The default value shown.
        options: The options displayed when the layout is clicked.
        max_height: Maximum height of the dropdown menu before scrolling is enabled.
        invert_scroll: Invert the scroll direction of the dropdown menu.
        scroll_speed: Speed of scrolling in the dropdown menu.
        show_scroll_bar: Show a scroll bar in the dropdown menu.
        primary_style: The style of the primary button.
        dropdown_style: The style of the buttons in the dropdown.
        active_style: The style of the dropdown button, which represents the active option.
    """

    DIVIDER = None

    DEFAULT_BUTTON_STYLE = {
        "normal": UIFlatButton.UIStyle(
            font_color=uicolor.GREEN_NEPHRITIS,
        ),
        "hover": UIFlatButton.UIStyle(
            font_color=uicolor.WHITE,
            bg=uicolor.DARK_BLUE_WET_ASPHALT,
            border=uicolor.GRAY_CONCRETE,
        ),
        "press": UIFlatButton.UIStyle(
            font_color=uicolor.DARK_BLUE_MIDNIGHT_BLUE,
            bg=uicolor.WHITE_CLOUDS,
            border=uicolor.GRAY_CONCRETE,
        ),
        "disabled": UIFlatButton.UIStyle(
            font_color=uicolor.WHITE_SILVER,
            bg=uicolor.GRAY_ASBESTOS,
        ),
    }
    DEFAULT_DROPDOWN_STYLE = {
        "normal": UIFlatButton.UIStyle(),
        "hover": UIFlatButton.UIStyle(
            font_color=uicolor.WHITE,
            bg=uicolor.DARK_BLUE_WET_ASPHALT,
            border=uicolor.GRAY_CONCRETE,
        ),
        "press": UIFlatButton.UIStyle(
            font_color=uicolor.DARK_BLUE_MIDNIGHT_BLUE,
            bg=uicolor.WHITE_CLOUDS,
            border=uicolor.GRAY_CONCRETE,
        ),
        "disabled": UIFlatButton.UIStyle(
            font_color=uicolor.WHITE_SILVER,
            bg=uicolor.GRAY_ASBESTOS,
        ),
    }

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 150,
        height: float = 30,
        default: str | None = None,
        options: list[str | None] | None = None,
        max_height: float = 200,
        invert_scroll: bool = False,
        scroll_speed: float = 15.0,
        show_scroll_bar: bool = False,
        primary_style=None,
        dropdown_style=None,
        active_style=None,
        **kwargs,
    ):
        if primary_style is None:
            primary_style = self.DEFAULT_BUTTON_STYLE
        if dropdown_style is None:
            dropdown_style = self.DEFAULT_DROPDOWN_STYLE
        if active_style is None:
            active_style = self.DEFAULT_BUTTON_STYLE

        # TODO handle if default value not in options or options empty
        if options is None:
            options = []
        self._options = options
        self._value = default

        super().__init__(x=x, y=y, width=width, height=height, **kwargs)

        self._default_style = deepcopy(primary_style)
        self._dropdown_style = deepcopy(dropdown_style)
        self._active_style = deepcopy(active_style)

        # Setup button showing value
        self._default_button = UIFlatButton(
            text=self._value or "", width=self.width, height=self.height, style=self._default_style
        )
        self._default_button.on_click = self._on_button_click  # type: ignore

        self._overlay = _UIDropdownOverlay(
            max_height=max_height,
            invert_scroll=invert_scroll,
            scroll_speed=scroll_speed,
            show_scroll_bar=show_scroll_bar,
        )
        self._update_options()

        # add children after super class setup
        self.add(self._default_button)

        self.register_event_type("on_change")

    @property
    def value(self) -> str | None:
        """Current selected option."""
        return self._value

    @value.setter
    def value(self, value: str | None):
        """Change the current selected option to a new option."""
        old_value = self._value
        self._value = value
        self._default_button.text = self._value or ""

        self._update_options()
        self.dispatch_event("on_change", UIOnChangeEvent(self, old_value, value))
        self.trigger_render()

    def _update_options(self):
        # generate options
        self._overlay.clear_options()

        for option in self._options:
            if option is None:  # None = UIDropdown.DIVIDER, required by pyright
                self._overlay.add_option(
                    UIWidget(width=self.width, height=2).with_background(color=arcade.color.GRAY)
                )
                continue
            else:
                button = self._overlay.add_option(
                    UIFlatButton(
                        text=option,
                        width=self.width,
                        height=self.height,
                        style=self._active_style if self.value == option else self._dropdown_style,
                    )
                )
            button.on_click = self._on_option_click

        self._overlay.detect_focusable_widgets()

    def _show_overlay(self):
        # traverse parents until UIManager or UIScrollArea is found
        parent = self.parent
        while parent is not None:
            if isinstance(parent, UIManager):
                break
            if isinstance(parent, UIScrollArea):
                break
            parent = parent.parent

        if parent is None:
            raise Exception("UIDropdown could not find a valid parent for the overlay.")

        self._overlay.show(parent)

    def _on_button_click(self, _: UIOnClickEvent):
        self._show_overlay()

    def _on_option_click(self, event: UIOnClickEvent):
        source: UIFlatButton = event.source
        self._overlay.hide()
        self.value = source.text

    def do_layout(self):
        """Position the overlay, this is not a common thing to do in do_layout,
        but is required for the dropdown."""
        self._default_button.rect = self.rect

        # Calculate total options height
        total_h = 0
        for option in self._options:
            total_h += 2 if option is None else self.height

        # Cap at max_height
        overlay = self._overlay
        visible_h = min(total_h, overlay._max_height) if total_h > 0 else self.height
        scroll_bar_w = _UIDropdownOverlay.SCROLL_BAR_WIDTH if overlay._show_scroll_bar else 0
        overlay_w = self.width + scroll_bar_w

        overlay.rect = (
            overlay.rect
            .resize(overlay_w, visible_h)
            .align_top(self.bottom - 2)
            .align_left(self._default_button.left)
        )

    def on_change(self, event: UIOnChangeEvent):
        """To be implemented by the user, triggered when the current selected value
        is changed to a different option.
        """
        pass
