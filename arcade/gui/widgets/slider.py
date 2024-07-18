from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Mapping, Optional, Union

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED

import arcade
from arcade import Texture
from arcade.gui import (
    NinePatchTexture,
    Surface,
    UIEvent,
    UIInteractiveWidget,
    UIMouseDragEvent,
    UIOnClickEvent,
)
from arcade.gui.events import UIOnChangeEvent
from arcade.gui.property import Property, bind
from arcade.gui.style import UIStyleBase, UIStyledWidget
from arcade.types import RGBA255, Color


class UIBaseSlider(UIInteractiveWidget, metaclass=ABCMeta):
    """
    Base class for sliders.

    A slider contains of a horizontal track and a thumb.
    The thumb can be moved along the track to set the value of the slider.

    Use the `on_change` event to get notified about value changes.

    Subclasses should implement the `_render_track` and `_render_thumb` methods.
    """

    value = Property(0)

    def __init__(
        self,
        *,
        value: float = 0,
        min_value: float = 0,
        max_value: float = 100,
        x: float = 0,
        y: float = 0,
        width: float = 300,
        height: float = 20,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        style: Union[Mapping[str, UISliderStyle], None] = None,
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
        self.min_value = min_value
        self.max_value = max_value

        self._cursor_width = self.height // 3

        # trigger render on value changes
        bind(self, "value", self.trigger_full_render)
        bind(self, "hovered", self.trigger_render)
        bind(self, "pressed", self.trigger_render)
        bind(self, "disabled", self.trigger_render)

        self.register_event_type("on_change")  # type: ignore  # https://github.com/pyglet/pyglet/pull/1173  # noqa

    def _x_for_value(self, value: float):
        """Provides the x coordinate for the given value."""

        x = self.content_rect.left
        val = (value - self.min_value) / self.max_value
        return x + self._cursor_width + val * (self.content_width - 2 * self._cursor_width)

    @property
    def norm_value(self):
        """Normalized value between 0.0 and 1.0"""
        return (self.value - self.min_value) / self.max_value

    @norm_value.setter
    def norm_value(self, value):
        """Normalized value between 0.0 and 1.0"""
        self.value = min(value * (self.max_value - self.min_value) + self.min_value, self.max_value)

    @property
    def _thumb_x(self):
        """Returns the current x coordinate of the thumb."""
        return self._x_for_value(self.value)

    @_thumb_x.setter
    def _thumb_x(self, nx):
        """Set thumb x coordinate and update the value."""
        rect = self.content_rect

        x = min(rect.right - self._cursor_width, max(nx, rect.left + self._cursor_width))
        if self.width == 0:
            self.norm_value = 0
        else:
            self.norm_value = (x - rect.left - self._cursor_width) / float(
                self.content_width - 2 * self._cursor_width
            )

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        self._render_track(surface)
        self._render_thumb(surface)

    @abstractmethod
    def _render_track(self, surface):
        """Render the track of the slider.

        This method should be implemented in a slider implementation.

        Track should stay within self.content_rect.
        """
        pass

    @abstractmethod
    def _render_thumb(self, surface):
        """Render the thumb of the slider.

        This method should be implemented in a slider implementation.

        Thumb should stay within self.content_rect.
        x coordinate of the thumb should be self._thumb_x.
        """
        pass

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if super().on_event(event):
            return EVENT_HANDLED

        if isinstance(event, UIMouseDragEvent):
            if self.pressed:
                old_value = self.value
                self._thumb_x = event.x
                self.dispatch_event("on_change", UIOnChangeEvent(self, old_value, self.value))  # type: ignore

        return EVENT_UNHANDLED

    def on_click(self, event: UIOnClickEvent):
        old_value = self.value
        self._thumb_x = event.x
        self.dispatch_event("on_change", UIOnChangeEvent(self, old_value, self.value))  # type: ignore

    def on_change(self, event: UIOnChangeEvent):
        """To be implemented by the user, triggered when the cursor's value is changed."""
        pass


@dataclass
class UISliderStyle(UIStyleBase):
    """
    Used to style the slider for different states. Below is its use case.

    .. code:: py

        button = UITextureButton(style={"normal": UITextureButton.UIStyle(...),})
    """

    bg: RGBA255 = Color(94, 104, 117)
    border: RGBA255 = Color(77, 81, 87)
    border_width: int = 1
    filled_track: RGBA255 = Color(50, 50, 50)
    unfilled_track: RGBA255 = Color(116, 125, 123)


class UISlider(UIStyledWidget[UISliderStyle], UIBaseSlider):
    """
    A simple slider.

    A slider contains of a horizontal track and a thumb.
    The thumb can be moved along the track to set the value of the slider.

    Use the `on_change` event to get notified about value changes.

    There are four states of the UISlider i.e normal, hovered, pressed and disabled.

    :param value: Current value of the curosr of the slider.
    :param min_value: Minimum value of the slider.
    :param max_value: Maximum value of the slider.
    :param x: x coordinate of bottom left.
    :param y: y coordinate of bottom left.
    :param width: Width of the slider.
    :param height: Height of the slider.
    :param Mapping[str, "UISlider.UIStyle"] | None style: Used to style the slider
        for different states.

    """

    UIStyle = UISliderStyle

    DEFAULT_STYLE = {
        "normal": UIStyle(),
        "hover": UIStyle(
            bg=Color(96, 103, 112),
            border=Color(77, 81, 87),
            border_width=2,
            filled_track=Color(50, 50, 50),
            unfilled_track=Color(116, 125, 123),
        ),
        "press": UIStyle(
            bg=Color(96, 103, 112),
            border=Color(77, 81, 87),
            border_width=3,
            filled_track=Color(50, 50, 50),
            unfilled_track=Color(116, 125, 123),
        ),
        "disabled": UIStyle(
            bg=Color(94, 104, 117),
            border=Color(77, 81, 87),
            border_width=1,
            filled_track=Color(50, 50, 50),
            unfilled_track=Color(116, 125, 123),
        ),
    }

    def __init__(
        self,
        *,
        value: float = 0,
        min_value: float = 0,
        max_value: float = 100,
        x: float = 0,
        y: float = 0,
        width: float = 300,
        height: float = 20,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        style: Union[Mapping[str, UISliderStyle], None] = None,
        **kwargs,
    ):
        super().__init__(
            value=value,
            min_value=min_value,
            max_value=max_value,
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

    def get_current_state(self) -> str:
        """Returns the current state of the slider i.e disabled, press, hover or normal."""
        if self.disabled:
            return "disabled"
        elif self.pressed:
            return "press"
        elif self.hovered:
            return "hover"
        else:
            return "normal"

    def _render_track(self, surface: Surface):
        """Render the track of the slider."""
        style = self.get_current_style()

        bg_slider_color = style.get("unfilled_track", UISlider.UIStyle.unfilled_track)
        fg_slider_color = style.get("filled_track", UISlider.UIStyle.filled_track)

        slider_height = self.content_height // 4

        slider_left_x = self._x_for_value(self.min_value)
        slider_right_x = self._x_for_value(self.max_value)
        cursor_center_x = self._thumb_x

        slider_bottom = (self.content_height - slider_height) // 2

        arcade.draw_lbwh_rectangle_filled(
            slider_left_x - self.content_rect.left,
            slider_bottom,
            slider_right_x - slider_left_x,
            slider_height,
            bg_slider_color,
        )
        arcade.draw_lbwh_rectangle_filled(
            slider_left_x - self.content_rect.left,
            slider_bottom,
            cursor_center_x - slider_left_x,
            slider_height,
            fg_slider_color,
        )

    def _render_thumb(self, surface: Surface):
        """Render the thumb of the slider."""
        style = self.get_current_style()

        border_width = style.get("border_width", UISlider.UIStyle.border_width)
        cursor_color = style.get("bg", UISlider.UIStyle.bg)
        cursor_outline_color = style.get("border", UISlider.UIStyle.border)

        cursor_radius = self._cursor_width
        cursor_center_x = self._thumb_x
        slider_center_y = self.content_height // 2

        rel_cursor_x = cursor_center_x - self.content_rect.left
        arcade.draw_circle_filled(rel_cursor_x, slider_center_y, cursor_radius, cursor_color)
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


class UITextureSlider(UISlider):
    """
    A custom slider subclass which supports textures.

    You can copy this as-is into your own project, or you can modify
    the class to have more features as needed.
    """

    def __init__(
        self,
        track: Union[Texture, NinePatchTexture],
        thumb: Union[Texture, NinePatchTexture],
        style=None,
        **kwargs,
    ):
        self._track = track
        self._thumb = thumb

        super().__init__(style=style or UISlider.DEFAULT_STYLE, **kwargs)

    def _render_track(self, surface: Surface):
        style: UISliderStyle = self.get_current_style()  # type: ignore
        surface.draw_texture(0, 0, self.width, self.height, self._track)

        # TODO accept these as constructor params
        slider_height = self.height // 4
        slider_left_x = self._x_for_value(self.min_value)
        cursor_center_x = self._thumb_x

        slider_bottom = (self.height - slider_height) // 2

        # slider
        arcade.draw_lbwh_rectangle_filled(
            slider_left_x - self.left,
            slider_bottom,
            cursor_center_x - slider_left_x,
            slider_height,
            style.filled_track,
        )

    def _render_thumb(self, surface: Surface):
        cursor_center_x = self._thumb_x
        rel_cursor_x = cursor_center_x - self.left
        surface.draw_texture(
            x=rel_cursor_x - self._thumb.width // 4 + 2,
            y=0,
            width=self._thumb.width // 2,
            height=self.height,
            tex=self._thumb,
        )
