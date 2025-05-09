from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED
from typing_extensions import override

import arcade
from arcade.gui.events import UIMouseDragEvent, UIMouseEvent, UIMousePressEvent, UIMouseReleaseEvent
from arcade.gui.widgets import UILayout, UIWidget


class UIDraggableMixin(UILayout):
    """UIDraggableMixin can be used to make any :class:`UIWidget` draggable.

    Example, create a draggable Frame, with a background, useful for window like constructs:

        class DraggablePane(UITexturePane, UIDraggableMixin):
            ...

    This will not work when placed in a layout, as the layout will overwrite the position.

    warning:

            This mixin in its current form is not recommended for production use.
            It is a quick way to get a draggable window like widget.
            It does not respect the layout system and can break other widgets
            which rely on the layout system.

    """

    _dragging = False

    @override
    def do_layout(self):
        # FIXME this breaks core UI rules "Widgets are placed by parents", let us not do this
        rect = self.rect
        super().do_layout()
        self.rect = self.rect.align_top(rect.top).align_left(rect.left)

    @override
    def on_event(self, event) -> bool | None:
        """Handle dragging of the widget."""
        if isinstance(event, UIMousePressEvent):
            if event.button == arcade.MOUSE_BUTTON_LEFT and self.rect.point_in_rect(event.pos):
                self._dragging = True
                return EVENT_HANDLED

        if isinstance(event, UIMouseDragEvent) and self._dragging:
            self.rect = self.rect.move(event.dx, event.dy)
            self.trigger_full_render()
            return EVENT_HANDLED

        if isinstance(event, UIMouseReleaseEvent):
            if event.button == arcade.MOUSE_BUTTON_LEFT and self._dragging:
                self._dragging = False
                self.trigger_full_render()
                return EVENT_HANDLED

        return super().on_event(event)


class UIMouseFilterMixin(UIWidget):
    """:class:`UIMouseFilterMixin` can be used to catch all mouse events which occur
    inside this widget.

    Useful for window like widgets, :class:`UIMouseEvents` should not trigger
    effects which are under the widget.
    """

    @override
    def on_event(self, event) -> bool | None:
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
