from __future__ import annotations

from typing import Iterable, Optional

from pyglet.event import EVENT_UNHANDLED

import arcade
from arcade.gui import (
    Property,
    Surface,
    UIEvent,
    UIMouseDragEvent,
    UIMouseEvent,
    UIMouseScrollEvent,
    UIWidget,
    bind,
)
from arcade.types import LBWH


class UIScrollArea(UIWidget):
    """A widget that can scroll its children."""

    scroll_x = Property[float](default=0.0)
    scroll_y = Property[float](default=0.0)

    scroll_speed = 1.3
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
        self.surface = Surface(
            size=canvas_size,
        )

        bind(self, "scroll_x", self.trigger_full_render)
        bind(self, "scroll_y", self.trigger_full_render)

    def remove(self, child: "UIWidget"):
        super().remove(child)
        self.trigger_full_render()

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
        self.prepare_render(surface)
        # draw the whole surface, the scissor box, will limit the visible area on screen
        width, height = self.surface.size
        self.surface.position = (-self.scroll_x, -self.scroll_y)
        self.surface.draw(LBWH(0, 0, width, height))

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if isinstance(event, UIMouseDragEvent) and not self.rect.point_in_rect(event.pos):
            return EVENT_UNHANDLED

        # drag scroll area around with middle mouse button
        if isinstance(event, UIMouseDragEvent) and event.buttons & arcade.MOUSE_BUTTON_MIDDLE:
            self.scroll_x -= event.dx
            self.scroll_y -= event.dy
            return True

        if isinstance(event, UIMouseScrollEvent):
            invert = -1 if self.invert_scroll else 1

            self.scroll_x -= event.scroll_x * self.scroll_speed * invert
            self.scroll_y -= event.scroll_y * self.scroll_speed * invert
            return True

        child_event = event
        if isinstance(event, UIMouseEvent):
            child_event = type(event)(**event.__dict__)  # type: ignore
            child_event.x = int(event.x - self.left + self.scroll_x)
            child_event.y = int(event.y - self.bottom + self.scroll_y)

        return super().on_event(child_event)
