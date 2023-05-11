from dataclasses import dataclass
from typing import Optional, Tuple, Union, Mapping

from pyglet.event import EVENT_UNHANDLED

import arcade
from arcade.math import get_distance
from arcade.types import Color, RGBA255
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
from arcade.gui.style import UIStyleBase, UIStyledWidget, UIWidget

class _SliderParent:
    """
    Parent Slider all sliders inherit from

    Creates the base slider properties and methods.
    NOTE: put self.register_event_type("on_change") in child classes

    .. warning:: Not all users can scroll easily!

                     Does NOT inherit from UIWidget
                        do that in the child class.
    """
    value = Property(0)
    hovered = Property(False)
    pressed = Property(False)
    disabled = Property(False)

    def __init__(
        self,
        *,
        value: float = 0,
        cursor_radius = 20,
        min_value: float = 0,
        max_value: float = 100,
        **kwargs,
    ):
        self.value = value
        self.vmin = min_value
        self.vmax = max_value

        self.cursor_radius = cursor_radius

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

    def _x_for_value(self, value) -> float:
        x = self.content_rect.x
        nval = (value - self.vmin) / self.vmax
        return (
            x
            + self.cursor_radius
            + nval * (self.content_width - 2 * self.cursor_radius)
        )

    @property
    def norm_value(self) -> float:
        """Normalized value between 0.0 and 1.0"""
        return (self.value - self.vmin) / self.vmax

    @norm_value.setter
    def norm_value(self, value: float) -> None:
        """Normalized value between 0.0 and 1.0"""
        self.value = min(value * (self.vmax - self.vmin) + self.vmin, self.vmax)

    @property
    def value_x(self) -> float:
        """Returns the current value of the cursor of the slider."""
        return self._x_for_value(self.value)

    @value_x.setter
    def value_x(self, nx: float) -> None:
        cr = self.content_rect

        x = min(cr.right - self.cursor_radius, max(nx, cr.x + self.cursor_radius))
        if self.width == 0:
            self.norm_value = 0
        else:
            self.norm_value = (x - cr.x - self.cursor_radius) / float(
                self.content_width - 2 * self.cursor_radius
            )
    
    def do_render(self, surface: Surface) -> None:
        """Override"""
        pass

    def _cursor_pos(self) -> Tuple[int, int]:
        """
        Override, do in child class
        """
        pass

    def _is_on_cursor(self, x: float, y: float) -> bool:
        cursor_center_x, cursor_center_y = self._cursor_pos()
        cursor_radius = self.cursor_radius
        distance_to_cursor = get_distance(x, y, cursor_center_x, cursor_center_y)
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

    def on_change(self, event: UIOnChangeEvent) -> None:
        """
        To be implemented by the user, triggered when the cursor's value is changed.

        Class inheriting must inherit from a widget
        and do register_event_type("on_change")        
        """
        pass

class UISlider(_SliderParent, UIStyledWidget["UISlider.UIStyle"]):
    """
    A simple horizontal slider. The value of the slider can be set by moving the cursor(indicator).

    There are four states of the UISlider i.e normal, hovered, pressed and disabled.

    :param float value: Current value of the curosr of the slider.
    :param float min_value: Minimum value of the slider.
    :param float max_value: Maximum value of the slider.
    :param float x: x coordinate of bottom left.
    :param float y: y coordinate of bottom left.
    :param float width: Width of the slider.
    :param float height: Height of the slider.
    :param Mapping[str, "UISlider.UIStyle"] | None style: Used to style the slider for different states.

    """

    @dataclass
    class UIStyle(UIStyleBase):
        """
        Used to style the slider for different states. Below is its use case.

        .. code:: py

            button = UITextureButton(style={"normal": UITextureButton.UIStyle(...),})
        """
        bg: RGBA255 = Color(94, 104, 117)
        border: RGBA255 = Color(77, 81, 87)
        border_width: int = 1
        filled_bar: RGBA255 = Color(50, 50, 50)
        unfilled_bar: RGBA255 = Color(116, 125, 123)

    DEFAULT_STYLE = {
        "normal": UIStyle(),
        "hover": UIStyle(
            bg=Color(96, 103, 112),
            border=Color(77, 81, 87),
            border_width=2,
            filled_bar=Color(50, 50, 50),
            unfilled_bar=Color(116, 125, 123),
        ),
        "press": UIStyle(
            bg=Color(96, 103, 112),
            border=Color(77, 81, 87),
            border_width=3,
            filled_bar=Color(50, 50, 50),
            unfilled_bar=Color(116, 125, 123),
        ),
        "disabled": UIStyle(
            bg=Color(94, 104, 117),
            border=Color(77, 81, 87),
            border_width=1,
            filled_bar=Color(50, 50, 50),
            unfilled_bar=Color(116, 125, 123),
        )
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
        size_hint: Optional[int]=None,
        size_hint_min: Optional[int]=None,
        size_hint_max: Optional[int]=None,
        style: Optional[Mapping[str, "UISlider.UIStyle"]] = None,  # typing: ignore
        **kwargs,
    ) -> None:

        _SliderParent.__init__(
            value=value,
            cursor_radius = height//3,
            min_value=min_value,
            max_value=max_value,
            **kwargs,
        )
        
        UIStyledWidget["UISlider.UIStyle"].__init__(
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

        # trigger render on value changes
        bind(self, "value", self.trigger_full_render)
        bind(self, "hovered", self.trigger_render)
        bind(self, "pressed", self.trigger_render)
        bind(self, "disabled", self.trigger_render)

        self.register_event_type("on_change")

    def do_render(self, surface: Surface) -> None:
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
        bg_slider_color = style.get("unfilled_bar", UISlider.UIStyle.unfilled_bar)
        fg_slider_color = style.get("filled_bar", UISlider.UIStyle.filled_bar)

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
        border_width = style.get("border_width", UISlider.UIStyle.border_width)
        cursor_color = style.get("bg", UISlider.UIStyle.bg)
        cursor_outline_color = style.get("border", UISlider.UIStyle.border)

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

    def _cursor_pos(self) -> Tuple[float, float]:
        return self.value_x, self.y + self.height // 2

class UITextureSlider(UISlider):
    """
    Slider using Textures
    """

    def __init__(
        self,
        bar: Union[Texture, NinePatchTexture],
        thumb: Union[Texture, NinePatchTexture],
        value: float = 0,
        min_value: float = 0,
        max_value: float = 100,
        x: float = 0,
        y: float = 0,
        width: float = 300,
        height: float = 20,
        size_hint: Optional[int]=None,
        size_hint_min: Optional[int]=None,
        size_hint_max: Optional[int]=None,
        style: Optional[Mapping[str, "UISlider.UIStyle"]]=None,
        **kwargs
    ) -> None:
        self.bar = bar
        self.thumb = thumb

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
            style=style,
            **kwargs
        )

    def do_render(self, surface: Surface) -> None:
        style: UISlider.UIStyle = self.get_current_style()  # type: ignore

        self.prepare_render(surface)

        surface.draw_texture(0, 0, self.width, self.height, self.bar)

        # TODO accept constructor params
        slider_height = self.height // 4
        slider_left_x = self._x_for_value(self.vmin)
        cursor_center_x = self.value_x

        slider_bottom = (self.height - slider_height) // 2

        # slider
        arcade.draw_xywh_rectangle_filled(
            slider_left_x - self.x,
            slider_bottom,
            cursor_center_x - slider_left_x,
            slider_height,
            style.filled_bar,
        )

        # cursor
        rel_cursor_x = cursor_center_x - self.x
        surface.draw_texture(
            x=rel_cursor_x - self.thumb.width // 4 + 2,
            y=0,
            width=self.thumb.width // 2,
            height=self.height,
            tex=self.thumb,
        )
