from typing import Optional

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED

from arcade.gui.widgets import UIWidget, UILayout
from arcade.gui.events import UIMouseDragEvent, UIMouseEvent


class UIDraggableMixin(UILayout):
    """
    UIDraggableMixin can be used to make any :class:`UIWidget` draggable.

    Example, create a draggable Frame, with a background, useful for window like constructs:

        class DraggablePane(UITexturePane, UIDraggableMixin):
            ...

    This does overwrite :class:`UILayout` behaviour which position themselves, like :class:`UIAnchorWidget`

    """

    def do_layout(self):
        # Preserve top left alignment, this overwrites self placing behaviour like from :class:`UIAnchorWidget`
        rect = self.rect
        super().do_layout()
        self.rect = self.rect.align_top(rect.top).align_left(rect.left)

    def on_event(self, event) -> Optional[bool]:
        if isinstance(event, UIMouseDragEvent) and self.rect.collide_with_point(event.x, event.y):
            self.rect = self.rect.move(event.dx, event.dy)
            self.trigger_full_render()

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED


class UIMouseFilterMixin(UIWidget):
    """
    :class:`UIMouseFilterMixin` can be used to catch all mouse events which occur inside this widget.

    Useful for window like widgets, :class:`UIMouseEvents` should not trigger effects which are under the widget.
    """

    def on_event(self, event) -> Optional[bool]:
        if super().on_event(event):
            return EVENT_HANDLED

        if isinstance(event, UIMouseEvent):
            # Catch all mouse events, that are inside this widget, to act like a window
            if self.rect.collide_with_point(*event.pos):
                return EVENT_HANDLED

        return EVENT_UNHANDLED


class UIWindowLikeMixin(UIMouseFilterMixin, UIDraggableMixin, UIWidget):
    """
    Makes a widget window like:

    - handles all mouse events that occur within the widgets boundaries
    - can be dragged
    """
