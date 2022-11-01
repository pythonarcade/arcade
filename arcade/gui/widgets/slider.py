from dataclasses import dataclass
from typing import Optional, Tuple, Union, Mapping

from pyglet.event import EVENT_UNHANDLED

import arcade
from arcade import Color
from arcade.gui import (
    Surface,
    UIEvent,
    UIMouseMovementEvent,
    UIMouseDragEvent,
    UIMousePressEvent,
    UIMouseReleaseEvent,
)
from arcade.gui.events import UIOnChangeEvent
from arcade.gui.property import Property, bind
from arcade.gui.style import UIStyleBase, UIStyledWidget


class UISlider(UIStyledWidget):
    value = Property(0)
    hovered = Property(False)
    pressed = Property(False)
    disabled = Property(False)

    @dataclass
    class UIStyle(UIStyleBase):
        bg: Color = (94, 104, 117)
        border: Color = (77, 81, 87)
        border_width: int = 1
        filled_bar: Color = (50, 50, 50)
        unfilled_bar: Color = (116, 125, 123)

    DEFAULT_STYLE = {
        "normal": UIStyle(),
        "hover": UIStyle(
            bg=(96, 103, 112),
            border=(77, 81, 87),
            border_width=2,
            filled_bar=(50, 50, 50),
            unfilled_bar=(116, 125, 123),
        ),
        "press": UIStyle(
            bg=(96, 103, 112),
            border=(77, 81, 87),
            border_width=3,
            filled_bar=(50, 50, 50),
            unfilled_bar=(116, 125, 123),
        ),
        "disabled": UIStyle(
            bg=(94, 104, 117),
            border=(77, 81, 87),
            border_width=1,
            filled_bar=(50, 50, 50),
            unfilled_bar=(116, 125, 123),
        )
    }

    def __init__(
        self,
        *,
        value=0,
        min_value=0,
        max_value=100,
        x=0,
        y=0,
        width=300,
        height=20,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        style: Union[Mapping[str, UIStyleBase], None] = None,  # typing: ignore
        **kwargs,
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            style=style or UISlider.DEFAULT_STYLE,
            **kwargs,
        )

        self.value = value
        self.vmin = min_value
        self.vmax = max_value

        self.cursor_radius = self.height // 3

        # trigger render on value changes
        bind(self, "value", self.trigger_render)
        bind(self, "hovered", self.trigger_render)
        bind(self, "pressed", self.trigger_render)
        bind(self, "disabled", self.trigger_render)

        self.register_event_type("on_change")

    def get_current_state(self) -> str:
        if self.disabled:
            return "disabled"
        elif self.pressed:
            return "press"
        elif self.hovered:
            return "hover"
        else:
            return "normal"

    def _x_for_value(self, value):
        x = self.content_rect.x
        nval = (value - self.vmin) / self.vmax
        return (
            x
            + self.cursor_radius
            + nval * (self.content_width - 2 * self.cursor_radius)
        )

    @property
    def norm_value(self):
        """Normalized value between 0.0 and 1.0"""
        return (self.value - self.vmin) / self.vmax

    @norm_value.setter
    def norm_value(self, value):
        """Normalized value between 0.0 and 1.0"""
        self.value = min(value * (self.vmax - self.vmin) + self.vmin, self.vmax)

    @property
    def value_x(self):
        return self._x_for_value(self.value)

    @value_x.setter
    def value_x(self, nx):
        cr = self.content_rect

        x = min(cr.right - self.cursor_radius, max(nx, cr.x + self.cursor_radius))
        if self.width == 0:
            self.norm_value = 0
        else:
            self.norm_value = (x - cr.x - self.cursor_radius) / float(
                self.content_width - 2 * self.cursor_radius
            )

    def do_render(self, surface: Surface):
        style = self.get_current_style()

        self.prepare_render(surface)

        # TODO accept constructor params
        slider_height = self.content_height // 4
        cursor_radius = self.cursor_radius

        slider_left_x = self._x_for_value(self.vmin)
        slider_right_x = self._x_for_value(self.vmax)
        cursor_center_x = self.value_x

        slider_bottom = (self.content_height - slider_height) // 2
        slider_center_y = self.content_height // 2

        # slider
        bg_slider_color = style.get("unfilled_bar", (116, 125, 123))
        fg_slider_color = style.get("filled_bar", (50, 50, 50))

        arcade.draw_xywh_rectangle_filled(
            slider_left_x - self.content_rect.x,
            slider_bottom,
            slider_right_x - slider_left_x,
            slider_height,
            bg_slider_color,
        )
        arcade.draw_xywh_rectangle_filled(
            slider_left_x - self.content_rect.x,
            slider_bottom,
            cursor_center_x - slider_left_x,
            slider_height,
            fg_slider_color,
        )

        # cursor
        border_width = style.get("border_width", 1)
        cursor_color = style.get("bg", (94, 104, 117))
        cursor_outline_color = style.get("border", (77, 81, 87))

        rel_cursor_x = cursor_center_x - self.content_rect.x
        arcade.draw_circle_filled(
            rel_cursor_x, slider_center_y, cursor_radius, cursor_color
        )
        arcade.draw_circle_filled(
            rel_cursor_x, slider_center_y, cursor_radius // 4, cursor_outline_color
        )
        arcade.draw_circle_outline(
            rel_cursor_x,
            slider_center_y,
            cursor_radius,
            cursor_outline_color,
            border_width,
        )

    def _cursor_pos(self) -> Tuple[int, int]:
        return self.value_x, self.y + self.height // 2

    def _is_on_cursor(self, x: float, y: float) -> bool:
        cursor_center_x, cursor_center_y = self._cursor_pos()
        cursor_radius = self.cursor_radius
        distance_to_cursor = arcade.get_distance(x, y, cursor_center_x, cursor_center_y)
        return distance_to_cursor <= cursor_radius

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if isinstance(event, UIMouseMovementEvent):
            self.hovered = self._is_on_cursor(event.x, event.y)

        if isinstance(event, UIMouseDragEvent):
            if self.pressed:
                old_value = self.value
                self.value_x = event.x
                self.dispatch_event("on_change", UIOnChangeEvent(self, old_value, self.value))  # type: ignore

        if isinstance(event, UIMousePressEvent):
            if self._is_on_cursor(event.x, event.y):
                self.pressed = True

        if isinstance(event, UIMouseReleaseEvent):
            self.pressed = False

        return EVENT_UNHANDLED

    def on_change(self, event: UIOnChangeEvent):
        pass
