from __future__ import annotations

from typing import Iterable, Optional

from pyglet.event import EVENT_UNHANDLED

import arcade
from arcade import XYWH
from arcade.gui import (
    Property,
    Surface,
    UIEvent,
    UILayout,
    UIMouseDragEvent,
    UIMouseEvent,
    UIMouseMovementEvent,
    UIMousePressEvent,
    UIMouseReleaseEvent,
    UIMouseScrollEvent,
    UIWidget,
    bind,
)
from arcade.types import LBWH


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

        self._scroll_bar_size = 20

        bind(self, "_thumb_hover", self.trigger_render)
        bind(self, "_dragging", self.trigger_render)
        bind(scroll_area, "scroll_x", self.trigger_full_render)
        bind(scroll_area, "scroll_y", self.trigger_full_render)
        bind(scroll_area, "content_height", self.trigger_full_render)
        bind(scroll_area, "content_width", self.trigger_full_render)

    def on_event(self, event: UIEvent) -> Optional[bool]:
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
            sx -= self._scroll_bar_size / 2
            sy -= self._scroll_bar_size / 2

            scroll_area = self.scroll_area

            if self.vertical:
                available_track_size = self.content_height - self._scroll_bar_size
                target_progress = 1 - sy / available_track_size
                target_progress = max(0, min(1, target_progress))

                scroll_range = scroll_area.surface.height - scroll_area.content_height
                scroll_area.scroll_y = -target_progress * scroll_range
            else:
                available_track_size = self.content_width - self._scroll_bar_size
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

    def _thumb_rect(self):
        """Calculate the rect of the thumb."""
        scroll_area = self.scroll_area

        scroll_value = scroll_area.scroll_y if self.vertical else scroll_area.scroll_x
        scroll_range = (
            scroll_area.surface.height - scroll_area.content_height
            if self.vertical
            else scroll_area.surface.width - scroll_area.content_width
        )

        scroll_progress = -scroll_value / scroll_range

        content_size = self.content_height if self.vertical else self.content_width
        available_track_size = content_size - self._scroll_bar_size

        if self.vertical:
            scroll_bar_y = self._scroll_bar_size / 2 + available_track_size * (1 - scroll_progress)
            scroll_bar_x = self.content_width / 2
            return XYWH(scroll_bar_x, scroll_bar_y, self.content_width, self._scroll_bar_size)

        else:
            scroll_bar_x = self._scroll_bar_size / 2 + available_track_size * scroll_progress
            scroll_bar_y = self.content_height / 2
            return XYWH(scroll_bar_x, scroll_bar_y, self._scroll_bar_size, self.content_height)

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

    This widget is highly experimental and only provides a proof of concept.

    Args:
        x: x position of the widget
        y: y position of the widget
        width: width of the widget
        height: height of the widget
        children: children of the widget
        size_hint: size hint of the widget
        size_hint_min: minimum size hint of the widget
        size_hint_max: maximum size hint of the widget
        canvas_size: size of the canvas, which is scrollable
        overscroll_x: allow over scrolling in x direction (scroll past the end)
        overscroll_y: allow over scrolling in y direction (scroll past the end)
        **kwargs: passed to UIWidget
    """

    scroll_x = Property[float](default=0.0)
    scroll_y = Property[float](default=0.0)

    scroll_speed = 1.8
    invert_scroll = False

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 300,
        height: float = 300,
        children: Iterable["UIWidget"] = tuple(),
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        canvas_size=(300, 300),
        overscroll_x=False,
        overscroll_y=False,
        **kwargs,
    ):
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
        self.default_anchor_x = "left"
        self.default_anchor_y = "bottom"
        self.overscroll_x = overscroll_x
        self.overscroll_y = overscroll_y

        self.surface = Surface(
            size=canvas_size,
        )

        bind(self, "scroll_x", self.trigger_full_render)
        bind(self, "scroll_y", self.trigger_full_render)

    def add(self, child: "UIWidget", **kwargs):
        """Add a child to the widget."""
        if self._children:
            raise ValueError("UIScrollArea can only have one child")

        super().add(child, **kwargs)
        self.trigger_full_render()

    def remove(self, child: "UIWidget"):
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

        total_min_x = round(total_min_x)
        total_min_y = round(total_min_y)

        # resize surface to fit all children
        if self.surface.size != (total_min_x, total_min_y):
            self.surface.resize(
                size=(total_min_x, total_min_y), pixel_ratio=self.surface.pixel_ratio
            )
            self.scroll_x = 0
            self.scroll_y = 0

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

    def on_event(self, event: UIEvent) -> Optional[bool]:
        """Handle scrolling of the widget."""
        if isinstance(event, UIMouseDragEvent) and not self.rect.point_in_rect(event.pos):
            return EVENT_UNHANDLED

        if isinstance(event, UIMouseScrollEvent) and self.rect.point_in_rect(event.pos):
            invert = -1 if self.invert_scroll else 1

            self.scroll_x -= -event.scroll_x * self.scroll_speed * invert
            self.scroll_y -= event.scroll_y * self.scroll_speed * invert

            # clip scrolling to canvas size
            if not self.overscroll_x:
                # clip scroll_x between 0 and -(self.surface.width - self.width)
                self.scroll_x = min(0, self.scroll_x)
                self.scroll_x = max(self.scroll_x, -int(self.surface.width - self.content_width))

            if not self.overscroll_y:
                # clip scroll_y between 0 and -(self.surface.height - self.height)
                self.scroll_y = min(0, self.scroll_y)
                self.scroll_y = max(self.scroll_y, -int(self.surface.height - self.content_height))

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
