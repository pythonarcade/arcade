from __future__ import annotations

import warnings
from collections.abc import Iterable
from typing import TypeVar

from pyglet.event import EVENT_UNHANDLED

import arcade
from arcade import XYWH
from arcade.gui.events import (
    UIEvent,
    UIKeyPressEvent,
    UIMouseDragEvent,
    UIMouseEvent,
    UIMouseMovementEvent,
    UIMousePressEvent,
    UIMouseReleaseEvent,
    UIMouseScrollEvent,
)
from arcade.gui.property import Property, bind
from arcade.gui.surface import Surface
from arcade.gui.widgets import UIWidget
from arcade.gui.widgets.layout import UILayout
from arcade.types import LBWH

W = TypeVar("W", bound="UIWidget")


class UIScrollBar(UIWidget):
    """Scroll bar for a UIScrollLayout.

    Indicating the current view position of the scroll area.
    Supports mouse dragging to scroll the content.
    """

    _thumb_hover = Property(False)
    _dragging = Property(False)

    def __init__(self, scroll_area: UIScrollArea, vertical: bool = True):
        size_hint = (0.05, 1) if vertical else (1, 0.05)

        super().__init__(size_hint=size_hint)
        self.scroll_area = scroll_area
        self.with_background(color=arcade.color.LIGHT_GRAY)
        self.with_border(color=arcade.uicolor.GRAY_CONCRETE)
        self.vertical = vertical

        bind(self, "_thumb_hover", UIScrollBar.trigger_render)
        bind(self, "_dragging", UIScrollBar.trigger_render)
        bind(scroll_area, "scroll_x", self.trigger_full_render, weak=True)
        bind(scroll_area, "scroll_y", self.trigger_full_render, weak=True)
        bind(scroll_area, "rect", self.trigger_full_render, weak=True)

    def on_event(self, event: UIEvent) -> bool | None:
        # check if we are scrollable
        if not self._scrollable():
            return EVENT_UNHANDLED

        # detect if event is mouse down and inside the scroll thumb
        # if so, start dragging the thumb
        thumb_rect_relative = self._thumb_rect()
        thumb_rect = thumb_rect_relative.move(*self.rect.bottom_left)

        if isinstance(event, UIMouseMovementEvent):
            self._thumb_hover = thumb_rect.point_in_rect(event.pos)

        if isinstance(event, UIMousePressEvent) and thumb_rect.point_in_rect(event.pos):
            self._dragging = True
            return True

        # detect if event is mouse drag and thumb is being dragged
        # if so, update the scroll position
        if isinstance(event, UIMouseDragEvent) and self._dragging:
            sx, sy = event.pos - self.rect.bottom_left
            sx -= self._scroll_bar_size() / 2
            sy -= self._scroll_bar_size() / 2

            scroll_area = self.scroll_area

            if self.vertical:
                available_track_size = self.content_height - self._scroll_bar_size()
                target_progress = 1 - sy / available_track_size
                target_progress = max(0, min(1, target_progress))

                scroll_range = scroll_area.surface.height - scroll_area.content_height
                scroll_area.scroll_y = -target_progress * scroll_range
            else:
                available_track_size = self.content_width - self._scroll_bar_size()
                target_progress = sx / available_track_size
                target_progress = max(0, min(1, target_progress))
                scroll_range = scroll_area.surface.width - scroll_area.content_width
                scroll_area.scroll_x = -target_progress * scroll_range

            return True

        # detect if event is mouse up and thumb is being dragged
        # if so, stop dragging the thumb
        if isinstance(event, UIMouseReleaseEvent) and self._dragging:
            self._dragging = False
            return True

        return EVENT_UNHANDLED

    def _scroll_bar_size(self):
        # based on: https://stackoverflow.com/a/16367035

        content_size = (
            self.scroll_area.surface.height if self.vertical else self.scroll_area.surface.width
        )
        view_size = (
            self.scroll_area.content_height if self.vertical else self.scroll_area.content_width
        )
        ratio = view_size / content_size

        scoll_range = self.content_height if self.vertical else self.content_width

        return scoll_range * ratio

    def _scrollable(self):
        return (
            self.scroll_area.surface.height - self.scroll_area.content_height
            if self.vertical
            else self.scroll_area.surface.width - self.scroll_area.content_width
        ) > 0

    def _thumb_rect(self):
        """Calculate the rect of the thumb."""
        scroll_area = self.scroll_area

        scroll_value = scroll_area.scroll_y if self.vertical else scroll_area.scroll_x
        scroll_range = (
            scroll_area.surface.height - scroll_area.content_height
            if self.vertical
            else scroll_area.surface.width - scroll_area.content_width
        )

        if not self._scrollable():
            # content is smaller than the scroll area, full size thumb
            return LBWH(0, 0, self.content_width, self.content_height)

        scroll_progress = -scroll_value / scroll_range

        content_size = self.content_height if self.vertical else self.content_width
        available_track_size = content_size - self._scroll_bar_size()

        if self.vertical:
            scroll_bar_y = self._scroll_bar_size() / 2 + available_track_size * (
                1 - scroll_progress
            )
            scroll_bar_x = self.content_width / 2
            return XYWH(scroll_bar_x, scroll_bar_y, self.content_width, self._scroll_bar_size())

        else:
            scroll_bar_x = self._scroll_bar_size() / 2 + available_track_size * scroll_progress
            scroll_bar_y = self.content_height / 2
            return XYWH(scroll_bar_x, scroll_bar_y, self._scroll_bar_size(), self.content_height)

    def do_render(self, surface: Surface):
        """Render the scroll bar."""
        self.prepare_render(surface)

        if self._dragging:
            thumb_color = arcade.uicolor.DARK_BLUE_WET_ASPHALT
        elif self._thumb_hover:
            thumb_color = arcade.uicolor.GRAY_CONCRETE
        else:
            thumb_color = arcade.uicolor.GRAY_ASBESTOS

        # draw the thumb
        arcade.draw_rect_filled(
            rect=self._thumb_rect(),
            color=thumb_color,
        )


class UIScrollArea(UILayout):
    """A widget that can scroll its children.

    Children are laid out on an internal canvas, which resizes itself to fit
    all children (at least the size of the scroll area itself). The visible
    part of the canvas is controlled by :py:attr:`scroll_x` and
    :py:attr:`scroll_y` (both range from ``0`` at the start of the content
    to a negative value at the end).

    For a typical scrollable list, add a container with ``size_hint=(1, 0)``
    (fill the width of the scroll area, grow to the natural content height)
    like ``UIBoxLayout``.

    Scrolling is supported via mouse wheel, :class:`UIScrollBar` and, while
    the mouse hovers the widget, the keyboard
    (arrow keys, PageUp/PageDown, Home/End).

    .. note::
        Content containing labels may finish sizing only during the first
        layout pass and render on the following frame. Single-frame capture
        pipelines (e.g. CI screenshots) should draw two frames.

    This widget is experimental, the API might change.

    Args:
        x: x position of the widget
        y: y position of the widget
        width: width of the widget
        height: height of the widget
        children: children of the widget
        size_hint: size hint of the widget
        size_hint_min: minimum size hint of the widget
        size_hint_max: maximum size hint of the widget
        canvas_size: deprecated, the canvas is sized automatically to fit
            all children
        overscroll_x: allow over scrolling in x direction (scroll past the end)
        overscroll_y: allow over scrolling in y direction (scroll past the end)
        scroll_speed: speed of scrolling in pixels per scroll event,
            defaults to :py:attr:`scroll_speed`
        invert_scroll: invert the scroll direction,
            defaults to :py:attr:`invert_scroll`
        **kwargs: passed to UIWidget
    """

    scroll_x = Property[float](default=0.0)
    scroll_y = Property[float](default=0.0)

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 300,
        height: float = 300,
        children: Iterable[UIWidget] = tuple(),
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        canvas_size=None,
        overscroll_x=False,
        overscroll_y=False,
        scroll_speed: float = 15.0,
        invert_scroll: bool = False,
        **kwargs,
    ):
        self.default_anchor_x = "left"
        self.default_anchor_y = "bottom"
        self.overscroll_x = overscroll_x
        self.overscroll_y = overscroll_y
        self.scroll_speed = scroll_speed
        self.invert_scroll = invert_scroll
        self._hovering = False

        if canvas_size is not None:
            warnings.warn(
                "canvas_size is deprecated, the canvas is sized automatically to fit all children",
                DeprecationWarning,
                stacklevel=2,
            )
        else:
            canvas_size = (max(int(width), 1), max(int(height), 1))

        # The canvas has to match the window's pixel ratio,
        # otherwise content renders at reduced resolution on hi-DPI displays.
        self.surface = Surface(
            size=canvas_size,
            pixel_ratio=arcade.get_window().get_pixel_ratio(),
        )

        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            children=children,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs,
        )

        bind(self, "scroll_x", UIScrollArea.trigger_full_render)
        bind(self, "scroll_y", UIScrollArea.trigger_full_render)

    def add(self, child: W, **kwargs) -> W:
        """Add a child to the widget."""
        super().add(child, **kwargs)
        self.trigger_full_render()

        return child

    def remove(self, child: UIWidget):
        """Remove a child from the widget."""
        super().remove(child)
        self.trigger_full_render()

    def do_layout(self):
        """Layout the children of the widget."""
        total_min_x = 0
        total_min_y = 0

        for child in self.children:
            new_rect = child.rect
            # apply sizehint
            shw, shh = child.size_hint or (None, None)
            # default min_size to be at least 1 for w and h, required by surface
            shw_min, shh_min = child.size_hint_min or (1, 1)
            shw_max, shh_max = child.size_hint_max or (None, None)

            if shw is not None:
                new_width = shw * self.content_width

                new_width = max(shw_min or 1, new_width)
                if shw_max is not None:
                    new_width = min(shw_max, new_width)
                new_rect = new_rect.resize(width=new_width)

            if shh is not None:
                new_height = shh * self.content_height
                new_height = max(shh_min or 1, new_height)

                if shh_max is not None:
                    new_height = min(shh_max, new_height)
                new_rect = new_rect.resize(height=new_height)

            new_rect = new_rect.align_top(self.surface.height).align_left(0)
            total_min_x = max(total_min_x, new_rect.width)
            total_min_y = max(total_min_y, new_rect.height)

            if new_rect != child.rect:
                child.rect = new_rect

        # the canvas covers at least the visible area, so children which do not
        # fill the scroll area never leave the viewport partially uncovered
        # and scroll ranges never become negative
        total_min_x = max(round(total_min_x), round(self.content_width), 1)
        total_min_y = max(round(total_min_y), round(self.content_height), 1)

        # resize surface to fit all children
        if self.surface.size != (total_min_x, total_min_y):
            self.surface.resize(
                size=(total_min_x, total_min_y), pixel_ratio=self.surface.pixel_ratio
            )
            # preserve the scroll position when content changes,
            # only clamp it into the new scroll range
            self._clamp_scroll()

    def _do_render(self, surface: Surface, force=False) -> bool:
        if not self.visible:
            return False

        should_render = force or self._requires_render
        rendered = False

        with self.surface.activate():
            if should_render:
                self.surface.clear()

            if self.visible:
                for child in self.children:
                    rendered |= child._do_render(self.surface, should_render)

        if should_render or rendered:
            rendered = True
            self.do_render_base(surface)
            self.do_render(surface)
            self._rendered = True
            self._requires_render = False

        return rendered

    def do_render(self, surface: Surface):
        """Renders the scolled surface into the given surface."""
        self.prepare_render(surface)

        offset_x, offset_y = self._get_scroll_offset()
        # position surface and draw visible area
        self.surface.position = offset_x, offset_y
        self.surface.draw(LBWH(-offset_x, -offset_y, self.content_width, self.content_height))

    def _get_scroll_offset(self):
        """calculates the scroll offset for the surface position,
        also used for calculating mouse event offset."""
        normal_pos_y = self.surface.height - self.content_height

        return self.scroll_x, -normal_pos_y - self.scroll_y

    def _clamp_scroll(self):
        """Clamp the scroll position into the valid scroll range.

        Axes with overscroll enabled are not clamped.
        """
        if not self.overscroll_x:
            # clip scroll_x between 0 and -(self.surface.width - self.width)
            scroll_range = int(self.content_width - self.surface.width)
            scroll_range = min(0, scroll_range)  # clip to 0 if content is smaller than surface
            self.scroll_x = max(scroll_range, min(0.0, self.scroll_x))

        if not self.overscroll_y:
            # clip scroll_y between 0 and -(self.surface.height - self.height)
            scroll_range = int(self.content_height - self.surface.height)
            scroll_range = min(0, scroll_range)  # clip to 0 if content is smaller than surface
            self.scroll_y = max(scroll_range, min(0.0, self.scroll_y))

    def _scroll_by_key(self, symbol: int) -> bool:
        """Scroll on arrow keys, PageUp/PageDown, Home and End.

        Returns True if the key was handled.
        """
        v_scrollable = self.surface.height > self.content_height
        h_scrollable = self.surface.width > self.content_width

        if symbol == arcade.key.UP and v_scrollable:
            self.scroll_y += self.scroll_speed
        elif symbol == arcade.key.DOWN and v_scrollable:
            self.scroll_y -= self.scroll_speed
        elif symbol == arcade.key.LEFT and h_scrollable:
            self.scroll_x += self.scroll_speed
        elif symbol == arcade.key.RIGHT and h_scrollable:
            self.scroll_x -= self.scroll_speed
        elif symbol == arcade.key.PAGEUP and v_scrollable:
            self.scroll_y += self.content_height
        elif symbol == arcade.key.PAGEDOWN and v_scrollable:
            self.scroll_y -= self.content_height
        elif symbol == arcade.key.HOME and v_scrollable:
            self.scroll_y = 0.0
        elif symbol == arcade.key.END and v_scrollable:
            self.scroll_y = float(min(0, int(self.content_height - self.surface.height)))
        else:
            return False

        self._clamp_scroll()
        return True

    def on_event(self, event: UIEvent) -> bool | None:
        """Handle scrolling of the widget."""
        if isinstance(event, UIMouseMovementEvent):
            self._hovering = self.rect.point_in_rect(event.pos)

        if isinstance(event, UIMouseDragEvent) and not self.rect.point_in_rect(event.pos):
            return EVENT_UNHANDLED

        if isinstance(event, UIMouseScrollEvent) and self.rect.point_in_rect(event.pos):
            invert = -1 if self.invert_scroll else 1

            self.scroll_x -= -event.scroll_x * self.scroll_speed * invert
            self.scroll_y -= event.scroll_y * self.scroll_speed * invert

            self._clamp_scroll()
            return True

        if isinstance(event, UIKeyPressEvent) and self._hovering:
            if self._scroll_by_key(event.symbol):
                return True

        child_event = event
        if isinstance(event, UIMouseEvent):
            if self.rect.point_in_rect(event.pos):
                # create a new event with the position relative to the child
                off_x, off_y = self._get_scroll_offset()

                child_event = type(event)(**event.__dict__)  # type: ignore
                child_event.x = int(event.x - self.left - off_x)
                child_event.y = int(event.y - self.bottom - off_y)

            else:
                # event is outside the scroll area, do not pass it to the children
                return EVENT_UNHANDLED

        return super().on_event(child_event)
