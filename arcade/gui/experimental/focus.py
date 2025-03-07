import warnings
from typing import Optional

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED
from pyglet.math import Vec2

import arcade
from arcade import MOUSE_BUTTON_LEFT
from arcade.gui.events import (
    UIEvent,
    UIKeyPressEvent,
    UIKeyReleaseEvent,
    UIMousePressEvent,
    UIMouseReleaseEvent,
)
from arcade.gui.experimental.controller import (
    UIControllerButtonPressEvent,
    UIControllerButtonReleaseEvent,
    UIControllerDpadEvent,
)
from arcade.gui.property import ListProperty, Property, bind
from arcade.gui.surface import Surface
from arcade.gui.ui_manager import UIManager
from arcade.gui.widgets import UIInteractiveWidget, UIWidget
from arcade.gui.widgets.layout import UIAnchorLayout
from arcade.gui.widgets.slider import UIBaseSlider


class Focusable(UIWidget):
    """
    A widget that can be focused and provides additional information about focus behavior.

    Attributes:

    neighbor_up: The widget above this widget.
    neighbor_right: The widget right of this widget.
    neighbor_down: The widget below this widget.
    neighbor_left: The widget left of this widget.

    """

    # todo set focused when focused
    focused = Property(False)

    neighbor_up: UIWidget | None = None
    neighbor_right: UIWidget | None = None
    neighbor_down: UIWidget | None = None
    neighbor_left: UIWidget | None = None

    @property
    def ui(self) -> UIManager | None:
        """The UIManager this widget is attached to."""
        w = self
        while w.parent:
            if isinstance(w.parent, UIManager):
                return w.parent
            w = self.parent
        return None


class UIFocusMixin(UIWidget):
    """A group of widgets that can be focused.

    UIFocusGroup maintains two lists of widgets:
    - The list of focusable widgets.
    - The list of widgets in.

    Use `detect_focusable_widgets()` to automatically detect focusable widgets
    or add_widget to add them manually.

    The Group can be navigated with the keyboard or controller.

    - DPAD: Navigate between focusable widgets. (up, down, left, right)
    - TAB: Navigate between focusable widgets.
    - A Button or SPACE: Interact with the focused widget.

    """

    _focusable_widgets = ListProperty[UIWidget]()
    _focused = Property(0)
    _interacting: UIWidget | None = None

    _debug = Property(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        bind(self, "_debug", self.trigger_full_render)
        bind(self, "_focused", self.trigger_full_render)
        bind(self, "_focusable_widgets", self.trigger_full_render)

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if super().on_event(event):
            return EVENT_HANDLED

        if isinstance(event, UIKeyPressEvent):
            if event.symbol == arcade.key.TAB:
                if event.modifiers & arcade.key.MOD_SHIFT:
                    self.focus_previous()
                else:
                    self.focus_next()

                return EVENT_HANDLED

            elif event.symbol == arcade.key.SPACE:
                self.start_interaction()
                return EVENT_HANDLED

        elif isinstance(event, UIKeyReleaseEvent):
            if event.symbol == arcade.key.SPACE:
                self.end_interaction()
                return EVENT_HANDLED

        if isinstance(event, UIControllerDpadEvent):
            if self._interacting:
                # TODO this should be handled in the slider!
                # pass dpad events to the interacting widget
                if event.vector.x == 1 and isinstance(self._interacting, UIBaseSlider):
                    self._interacting.norm_value += 0.1
                    return EVENT_HANDLED

                elif event.vector.x == -1 and isinstance(self._interacting, UIBaseSlider):
                    self._interacting.norm_value -= 0.1
                    return EVENT_HANDLED

                return EVENT_HANDLED

            else:
                # switch focus
                if event.vector.x == 1:
                    self.focus_right()
                    return EVENT_HANDLED

                elif event.vector.y == 1:
                    self.focus_up()
                    return EVENT_HANDLED

                elif event.vector.x == -1:
                    self.focus_left()
                    return EVENT_HANDLED

                elif event.vector.y == -1:
                    self.focus_down()
                    return EVENT_HANDLED

        elif isinstance(event, UIControllerButtonPressEvent):
            if event.button == "a":
                self.start_interaction()
                return EVENT_HANDLED
        elif isinstance(event, UIControllerButtonReleaseEvent):
            if event.button == "a":
                self.end_interaction()
                return EVENT_HANDLED

        return EVENT_UNHANDLED

    def add_widget(self, widget):
        self._focusable_widgets.append(widget)

    @classmethod
    def _walk_widgets(cls, root: UIWidget):
        for child in reversed(root.children):
            yield child
            yield from cls._walk_widgets(child)

    def detect_focusable_widgets(self, root: UIWidget = None):
        """Automatically detect focusable widgets."""
        if root is None:
            root = self

        widgets = self._walk_widgets(root)

        focusable_widgets = []
        for widget in reversed(list(widgets)):
            if self.is_focusable(widget):
                focusable_widgets.append(widget)

        self._focusable_widgets = focusable_widgets

    def focus_up(self):
        widget = self._focusable_widgets[self._focused]
        if isinstance(widget, Focusable):
            if widget.neighbor_up:
                _index = self._focusable_widgets.index(widget.neighbor_up)
                self._focused = _index
                return

        self.focus_previous()

    def focus_down(self):
        widget = self._focusable_widgets[self._focused]
        if isinstance(widget, Focusable):
            if widget.neighbor_down:
                _index = self._focusable_widgets.index(widget.neighbor_down)
                self._focused = _index
                return

        self.focus_next()

    def focus_left(self):
        widget = self._focusable_widgets[self._focused]
        if isinstance(widget, Focusable):
            if widget.neighbor_left:
                _index = self._focusable_widgets.index(widget.neighbor_left)
                self._focused = _index
                return

        self.focus_previous()

    def focus_right(self):
        widget = self._focusable_widgets[self._focused]
        if isinstance(widget, Focusable):
            if widget.neighbor_right:
                _index = self._focusable_widgets.index(widget.neighbor_right)
                self._focused = _index
                return

        self.focus_next()

    def focus_next(self):
        self._focused += 1
        if self._focused >= len(self._focusable_widgets):
            self._focused = 0

    def focus_previous(self):
        self._focused -= 1
        if self._focused < 0:
            self._focused = len(self._focusable_widgets) - 1

    def start_interaction(self):
        widget = self._focusable_widgets[self._focused]

        if isinstance(widget, UIInteractiveWidget):
            widget.dispatch_ui_event(
                UIMousePressEvent(
                    source=self,
                    x=widget.rect.center_x,
                    y=widget.rect.center_y,
                    button=MOUSE_BUTTON_LEFT,
                    modifiers=0,
                )
            )
            self._interacting = widget
        else:
            print("Cannot interact widget")

    def end_interaction(self):
        widget = self._focusable_widgets[self._focused]

        if isinstance(widget, UIInteractiveWidget):
            if isinstance(self._interacting, UIBaseSlider):
                # if slider, release outside the slider
                x = self._interacting.rect.left - 1
                y = self._interacting.rect.bottom - 1
            else:
                x = widget.rect.center_x
                y = widget.rect.center_y

            self._interacting = None
            widget.dispatch_ui_event(
                UIMouseReleaseEvent(
                    source=self,
                    x=x,
                    y=y,
                    button=MOUSE_BUTTON_LEFT,
                    modifiers=0,
                )
            )

    def _do_render(self, surface: Surface, force=False) -> bool:
        # TODO: add a post child render hook to UIWidget
        rendered = super()._do_render(surface, force)

        if rendered:
            self.do_post_render(surface)

        return rendered

    def do_post_render(self, surface: Surface):
        surface.limit(None)

        if len(self._focusable_widgets) < self._focused < 0:
            warnings.warn("Focused widget is out of range")
            self._focused = 0
            return

        widget = self._focusable_widgets[self._focused]
        arcade.draw_rect_outline(
            rect=widget.rect,
            color=arcade.color.WHITE,
            border_width=2,
        )

        if self._debug:
            # debugging
            if isinstance(widget, Focusable):
                if widget.neighbor_up:
                    self._draw_indicator(
                        widget.rect.top_center,
                        widget.neighbor_up.rect.bottom_center,
                        color=arcade.color.RED,
                    )
                if widget.neighbor_down:
                    self._draw_indicator(
                        widget.rect.bottom_center,
                        widget.neighbor_down.rect.top_center,
                        color=arcade.color.GREEN,
                    )
                if widget.neighbor_left:
                    self._draw_indicator(
                        widget.rect.center_left,
                        widget.neighbor_left.rect.center_right,
                        color=arcade.color.BLUE,
                    )
                if widget.neighbor_right:
                    self._draw_indicator(
                        widget.rect.center_right,
                        widget.neighbor_right.rect.center_left,
                        color=arcade.color.ORANGE,
                    )

    def _draw_indicator(self, start: Vec2, end: Vec2, color=arcade.color.WHITE):
        arcade.draw_line(start.x, start.y, end.x, end.y, color, 2)
        arcade.draw_circle_filled(end.x, end.y, 5, color, num_segments=4)

    @staticmethod
    def is_focusable(widget):
        return isinstance(widget, (Focusable, UIInteractiveWidget))


class UIFocusGroup(UIFocusMixin, UIAnchorLayout):
    pass
