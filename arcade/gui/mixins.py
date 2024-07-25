from __future__ import annotations

from typing import Optional

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED
from typing_extensions import override

from arcade.gui.events import UIMouseDragEvent, UIMouseEvent
from arcade.gui.widgets import UILayout, UIWidget


class UIDraggableMixin(UILayout):
    """UIDraggableMixin can be used to make any :class:`UIWidget` draggable.

    Example, create a draggable Frame, with a background, useful for window like constructs:

        class DraggablePane(UITexturePane, UIDraggableMixin):
            ...

    This does overwrite :class:`UILayout` behavior which position themselves,
    like :class:`UIAnchorWidget`

    warning:

            This mixin in its current form is not recommended for production use.
            It is a quick way to get a draggable window like widget.
            It does not respect the layout system and can break other widgets
            which rely on the layout system.

            Further the dragging is not smooth, as it uses a very simple approach.

            Will be fixed in future versions, but might break existing code within a minor update.

    """

    @override
    def do_layout(self):
        # FIXME this breaks all rules, let us not do this

        # Preserve top left alignment, this overwrites self placing behavior like
        # from :class:`UIAnchorWidget`
        rect = self.rect
        super().do_layout()
        self.rect = self.rect.align_top(rect.top).align_left(rect.left)

    @override
    def on_event(self, event) -> Optional[bool]:
        """Handle dragging of the widget."""
        if isinstance(event, UIMouseDragEvent) and self.rect.point_in_rect(event.pos):
            self.rect = self.rect.move(event.dx, event.dy)
            self.trigger_full_render()

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED


class UIMouseFilterMixin(UIWidget):
    """:class:`UIMouseFilterMixin` can be used to catch all mouse events which occur
    inside this widget.

    Useful for window like widgets, :class:`UIMouseEvents` should not trigger
    effects which are under the widget.
    """

    @override
    def on_event(self, event) -> Optional[bool]:
        """Catch all mouse events, that are inside this widget."""
        if super().on_event(event):
            return EVENT_HANDLED

        if isinstance(event, UIMouseEvent):
            # Catch all mouse events, that are inside this widget, to act like a window
            if self.rect.point_in_rect(event.pos):
                return EVENT_HANDLED

        return EVENT_UNHANDLED


class UIWindowLikeMixin(UIMouseFilterMixin, UIDraggableMixin, UIWidget):
    """Makes a widget window like:

    - handles all mouse events that occur within the widgets boundaries
    - can be dragged
    """
