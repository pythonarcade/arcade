from __future__ import annotations

import warnings
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Mapping, Union

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED
from typing_extensions import override

import arcade
from arcade import Texture, uicolor
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
from arcade.types import RGBA255


class UIBaseSlider(UIInteractiveWidget, metaclass=ABCMeta):
    """Base class for sliders.

    A slider contains of a horizontal track and a thumb.
    The thumb can be moved along the track to set the value of the slider.

    Use the `on_change` event to get notified about value changes.

    Subclasses should implement the `_render_track` and `_render_thumb` methods.

    Args:

        value: Current value of the curosr of the slider.
        min_value: Minimum value of the slider.
        max_value: Maximum value of the slider.
        x: x coordinate of bottom left.
        y: y coordinate of bottom left.
        width: Width of the slider.
        height: Height of the slider.
        size_hint: Size hint of the slider.
        size_hint_min: Minimum size hint of the slider.
        size_hint_max: Maximum size hint of the slider.
        style: Used to style the slider for different states.
        **kwargs: Passed to UIInteractiveWidget.

    """

    value = Property(0.0)

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

        self.register_event_type("on_change")

    def _x_for_value(self, value: float):
        """Provides the x coordinate for the given value."""

        x = self.content_rect.left
        val = (value - self.min_value) / (self.max_value - self.min_value)
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

    @override
    def do_render(self, surface: Surface):
        """Render the slider, including track and thumb."""
        self.prepare_render(surface)
        self._render_track(surface)
        self._render_thumb(surface)

    @abstractmethod
    def _render_track(self, surface: Surface):
        """Render the track of the slider.

        This method should be implemented in a slider implementation.

        Track should stay within self.content_rect.

        Args:
                surface: Surface to render on.
        """
        pass

    @abstractmethod
    def _render_thumb(self, surface: Surface):
        """Render the thumb of the slider.

        This method should be implemented in a slider implementation.

        Thumb should stay within self.content_rect.
        x coordinate of the thumb should be self._thumb_x.

        Args:
            surface: Surface to render on.
        """
        pass

    @override
    def on_event(self, event: UIEvent) -> bool | None:
        """
        Args:
            event: Event to handle.

        Returns: True if event was handled, False otherwise.

        """
        if self.disabled:
            return EVENT_UNHANDLED

        if super().on_event(event):
            return EVENT_HANDLED

        if isinstance(event, UIMouseDragEvent):
            if self.pressed:
                old_value = self.value
                self._thumb_x = event.x
                self.dispatch_event("on_change", UIOnChangeEvent(self, old_value, self.value))
                return EVENT_HANDLED

        return EVENT_UNHANDLED

    @override
    def on_click(self, event: UIOnClickEvent):
        """Handle click events to set the value of the slider.

        A new value is calculated based on the click position and the slider's width and
        the `on_change` event is dispatched.

        Args:
            event: Click event.
        """
        old_value = self.value
        self._thumb_x = event.x
        self.dispatch_event("on_change", UIOnChangeEvent(self, old_value, self.value))

    def on_change(self, event: UIOnChangeEvent):
        """To be implemented by the user, triggered when the cursor's value is changed.

        Args:
            event: Event containing the old and new value of the cursor.
        """
        pass


@dataclass
class UISliderStyle(UIStyleBase):
    """Used to style the slider for different states. Below is its use case.

    .. code:: py

        button = UITextureButton(style={"normal": UITextureButton.UIStyle(...),})

    Args:
        bg: Background color.
        border: Border color.
        border_width: Width of the border.
        filled_track: Color of the filled track.
        unfilled_track: Color of the unfilled track.

    """

    bg: RGBA255 = uicolor.WHITE_SILVER
    border: RGBA255 = uicolor.DARK_BLUE_MIDNIGHT_BLUE
    border_width: int = 2
    filled_track: RGBA255 = uicolor.DARK_BLUE_MIDNIGHT_BLUE
    unfilled_track: RGBA255 = uicolor.WHITE_SILVER


class UISlider(UIStyledWidget[UISliderStyle], UIBaseSlider):
    """A simple slider.

    A slider consists of a horizontal track and a thumb.
    The thumb can be moved along the track to set the value of the slider.

    Use the `on_change` event to get notified about value changes.

    There are four states of the UISlider i.e. normal, hovered, pressed and disabled.

    Args:
        value: Current value of the cursor of the slider.
        min_value: Minimum value of the slider.
        max_value: Maximum value of the slider.
        x: x coordinate of bottom left.
        y: y coordinate of bottom left.
        width: Width of the slider.
        height: Height of the slider.
        style: Used to style the slider for different states.

    """

    UIStyle = UISliderStyle

    DEFAULT_STYLE = {
        "normal": UIStyle(),
        "hover": UIStyle(
            border=uicolor.BLUE_PETER_RIVER,
            border_width=2,
            filled_track=uicolor.BLUE_PETER_RIVER,
        ),
        "press": UIStyle(
            bg=uicolor.BLUE_PETER_RIVER,
            border=uicolor.DARK_BLUE_WET_ASPHALT,
            border_width=3,
            filled_track=uicolor.BLUE_PETER_RIVER,
        ),
        "disabled": UIStyle(
            bg=uicolor.WHITE_SILVER,
            border_width=1,
            filled_track=uicolor.GRAY_ASBESTOS,
            unfilled_track=uicolor.WHITE_SILVER,
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
        height: float = 25,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        style: Union[dict[str, UISliderStyle], None] = None,
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

    @override
    def get_current_state(self) -> str:
        """Get the current state of the slider.

        Returns:
            ""normal"", ""hover"", ""press"" or ""disabled"".
        """
        if self.disabled:
            return "disabled"
        elif self.pressed:
            return "press"
        elif self.hovered:
            return "hover"
        else:
            return "normal"

    @override
    def _render_track(self, surface: Surface):
        style = self.get_current_style()
        if style is None:
            warnings.warn(f"No style found for state {self.get_current_state()}", UserWarning)
            return

        bg_slider_color = style.get("unfilled_track", UISlider.UIStyle.unfilled_track)
        fg_slider_color = style.get("filled_track", UISlider.UIStyle.filled_track)

        slider_height = self.content_height // 3

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

    @override
    def _render_thumb(self, surface: Surface):
        style = self.get_current_style()
        if style is None:
            warnings.warn(f"No style found for state {self.get_current_state()}", UserWarning)
            return

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
    """A custom slider subclass which supports textures.

    You can copy this as-is into your own project, or you can modify
    the class to have more features as needed.

    Args:
        track_texture: Texture for the track, should be a NinePatchTexture.
        thumb_texture: Texture for the thumb.
        style: Used to style the slider for different states.
        **kwargs: Passed to UISlider.
    """

    def __init__(
        self,
        track_texture: Union[Texture, NinePatchTexture],
        thumb_texture: Union[Texture, NinePatchTexture],
        style=None,
        **kwargs,
    ):
        self._track_tex = track_texture
        self._thumb_tex = thumb_texture

        super().__init__(style=style or UISlider.DEFAULT_STYLE, **kwargs)

    @override
    def _render_track(self, surface: Surface):
        style = self.get_current_style()
        if style is None:
            warnings.warn(f"No style found for state {self.get_current_state()}", UserWarning)
            return

        surface.draw_texture(0, 0, self.width, self.height, self._track_tex)

        # TODO accept these as constructor params
        slider_height = self.height // 4
        slider_left_x = self._x_for_value(self.min_value)
        cursor_center_x = self._thumb_x

        slider_bottom = (self.height - slider_height) // 2

        # slider
        if style.filled_track:
            arcade.draw_lbwh_rectangle_filled(
                slider_left_x - self.left,
                slider_bottom,
                cursor_center_x - slider_left_x,
                slider_height,
                style.filled_track,
            )

    @override
    def _render_thumb(self, surface: Surface):
        cursor_center_x = self._thumb_x
        rel_cursor_x = cursor_center_x - self.left
        surface.draw_texture(
            x=rel_cursor_x - self._thumb_tex.width // 4 + 2,
            y=0,
            width=self._thumb_tex.width // 2,
            height=self.height,
            tex=self._thumb_tex,
        )
