from collections import ChainMap
from typing import Optional, Tuple, Union

from pyglet.event import EVENT_UNHANDLED

import arcade
from arcade.experimental.uistyle import UISliderStyle
from arcade.gui import UIWidget, Surface, UIEvent, UIMouseMovementEvent, UIMouseDragEvent, UIMousePressEvent, \
    UIMouseReleaseEvent
from arcade.gui._property import _Property, _bind
from arcade.gui.events import UIOnChangeEvent


class UISlider(UIWidget):
    value = _Property(0)
    hovered = _Property(False)
    pressed = _Property(False)

    def __init__(self,
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
                 style: Union[UISliderStyle, dict, None] = None,
                 **kwargs
                 ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            style=ChainMap(style or {}, UISliderStyle()),  # type: ignore
            **kwargs
        )

        self.value = value
        self.vmin = min_value
        self.vmax = max_value

        self.padding = self.height // 3
        self.cursor_radius = self.height // 3

        # trigger render on value changes
        _bind(self, "value", self.trigger_full_render)
        _bind(self, "hovered", self.trigger_render)
        _bind(self, "pressed", self.trigger_full_render)

        self.register_event_type("on_change")

    def _x_for_value(self, value):
        padding = self.padding
        x = self.x
        nval = (value - self.vmin) / self.vmax
        return x + padding + nval * (self.width - 2 * padding)

    @property
    def norm_value(self):
        """ Normalized value between 0.0 and 1.0"""
        return (self.value - self.vmin) / self.vmax

    @norm_value.setter
    def norm_value(self, value):
        """ Normalized value between 0.0 and 1.0"""
        self.value = min(value * (self.vmax - self.vmin) + self.vmin, self.vmax)

    @property
    def value_x(self):
        return self._x_for_value(self.value)

    @value_x.setter
    def value_x(self, nx):
        padding = self.padding
        x = min(self.right - padding, max(nx, self.x + padding))
        if self.width == 0:
            self.norm_value = 0
        else:
            self.norm_value = (x - self.x - padding) / float(self.width - 2 * padding)

    def do_render(self, surface: Surface):
        state = "pressed" if self.pressed else "hovered" if self.hovered else "normal"

        self.prepare_render(surface)

        # TODO accept constructor params
        slider_height = self.height // 4
        cursor_radius = self.cursor_radius

        slider_left_x = self._x_for_value(self.vmin)
        slider_right_x = self._x_for_value(self.vmax)
        cursor_center_x = self.value_x

        slider_bottom = (self.height - slider_height) // 2
        slider_center_y = self.height // 2

        # slider
        bg_slider_color = self.style[f"{state}_unfilled_bar"]
        fg_slider_color = self.style[f"{state}_filled_bar"]

        arcade.draw_xywh_rectangle_filled(slider_left_x - self.x, slider_bottom, slider_right_x - slider_left_x,
                                          slider_height, bg_slider_color)
        arcade.draw_xywh_rectangle_filled(slider_left_x - self.x, slider_bottom, cursor_center_x - slider_left_x,
                                          slider_height, fg_slider_color)

        # cursor
        border_width = self.style[f"{state}_border_width"]
        cursor_color = self.style[f"{state}_bg"]
        cursor_outline_color = self.style[f"{state}_border"]

        rel_cursor_x = cursor_center_x - self.x
        arcade.draw_circle_filled(rel_cursor_x, slider_center_y, cursor_radius, cursor_color)
        arcade.draw_circle_filled(rel_cursor_x, slider_center_y, cursor_radius // 4, cursor_outline_color)
        arcade.draw_circle_outline(rel_cursor_x, slider_center_y, cursor_radius, cursor_outline_color, border_width)

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
