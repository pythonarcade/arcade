import warnings
from types import EllipsisType

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED
from pyglet.math import Vec2

import arcade
from arcade import MOUSE_BUTTON_LEFT
from arcade.gui.events import (
    UIControllerButtonPressEvent,
    UIControllerButtonReleaseEvent,
    UIControllerDpadEvent,
    UIControllerEvent,
    UIEvent,
    UIKeyPressEvent,
    UIKeyReleaseEvent,
    UIMousePressEvent,
    UIMouseReleaseEvent,
)
from arcade.gui.property import ListProperty, Property, bind
from arcade.gui.surface import Surface
from arcade.gui.widgets import FocusMode, UIInteractiveWidget, UIWidget
from arcade.gui.widgets.layout import UIAnchorLayout
from arcade.gui.widgets.slider import UIBaseSlider


class UIFocusable(UIWidget):
    """
    A widget that provides additional information about focus neighbors.

    Attributes:

    neighbor_up: The widget above this widget.
    neighbor_right: The widget right of this widget.
    neighbor_down: The widget below this widget.
    neighbor_left: The widget left of this widget.
    """

    focus_mode = FocusMode.ALL

    neighbor_up: UIWidget | None = None
    neighbor_right: UIWidget | None = None
    neighbor_down: UIWidget | None = None
    neighbor_left: UIWidget | None = None


class UIFocusMixin(UIWidget):
    """A group of widgets that can be focused.

    UIFocusGroup maintains two lists of widgets:
    - The list of focusable widgets.
    - The list of widgets within (normal widget children).

    Use `detect_focusable_widgets()` to automatically detect focusable widgets
    or explicitly use `add_widget()`.

    The Group can be navigated with the keyboard (TAB/ SHIFT + TAB) or controller (DPad).

    - DPAD: Navigate between focusable widgets. (up, down, left, right)
    - TAB: Navigate between focusable widgets.
    - 'A' Button or SPACE: Interact with the focused widget.

    """

    _focused_widget = Property[UIWidget | None](None)
    _focusable_widgets = ListProperty[UIWidget]()
    _interacting: UIWidget | None = None

    _debug = Property(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        bind(self, "_debug", self.trigger_full_render)
        bind(self, "_focused_widget", self.trigger_full_render)
        bind(self, "_focusable_widgets", self.trigger_full_render)

    def on_event(self, event: UIEvent) -> bool | None:
        # pass events to children first, including controller events
        # so they can handle them
        if super().on_event(event):
            return EVENT_HANDLED

        if isinstance(event, UIControllerEvent):
            # if no focused widget, set the first focusable widget
            if self.focused_widget is None and self._focusable_widgets:
                self.set_focus()
                return EVENT_HANDLED

        if isinstance(event, UIKeyPressEvent):
            if event.symbol == arcade.key.TAB:
                if event.modifiers & arcade.key.MOD_SHIFT:
                    self.focus_previous()
                else:
                    self.focus_next()

                return EVENT_HANDLED

            elif event.symbol == arcade.key.SPACE:
                self._start_interaction()
                return EVENT_HANDLED

        elif isinstance(event, UIKeyReleaseEvent):
            if event.symbol == arcade.key.SPACE:
                self._end_interaction()
                return EVENT_HANDLED

        elif isinstance(event, UIControllerDpadEvent):
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
                self._start_interaction()
                return EVENT_HANDLED
        elif isinstance(event, UIControllerButtonReleaseEvent):
            if event.button == "a":
                self._end_interaction()
                return EVENT_HANDLED

        return EVENT_UNHANDLED

    @classmethod
    def _walk_widgets(cls, root: UIWidget):
        for child in reversed(root.children):
            yield child
            yield from cls._walk_widgets(child)

    def detect_focusable_widgets(self):
        """Automatically detect focusable widgets."""
        widgets = self._walk_widgets(self)

        focusable_widgets = []
        for widget in reversed(list(widgets)):
            if self.is_focusable(widget):
                focusable_widgets.append(widget)

        self._focusable_widgets = focusable_widgets

    @property
    def focused_widget(self) -> UIWidget | None:
        """Return the currently focused widget.
        If no widget is focused, return None."""
        return self._focused_widget

    def set_focus(self, widget: UIWidget | None | EllipsisType = ...):
        """Set the focus to a specific widget.

        Set the focus to a specific widget. The widget must be in the list of
        focusable widgets. If the widget is not in the list, a ValueError is raised.

        Setting the focus to None will remove the focus from the current widget.
        If `...` is passed (default), the focus will be set to the first
        focusable widget in the list.

        Args:
            widget: The widget to focus.
        """
        # de-focus the current widget
        if widget is None:
            if self.focused_widget is not None:
                self.focused_widget.focused = False
                self._focused_widget = None
            return

        # resolve ...
        if widget is Ellipsis:
            if self._focusable_widgets:
                widget = self._focusable_widgets[0]
            else:
                raise ValueError(
                    "No focusable widgets in the group, "
                    "use `detect_focusable_widgets()` to detect them."
                )

        # handle new focus
        if widget not in self._focusable_widgets:
            raise ValueError("Widget is not focusable or not in the group.")

        if self.focused_widget is not None:
            self.focused_widget.focused = False
        widget.focused = True
        self._focused_widget = widget

    def focus_up(self):
        widget = self.focused_widget
        if isinstance(widget, UIFocusable):
            if widget.neighbor_up:
                self.set_focus(widget.neighbor_up)
                return

        self.focus_previous()

    def focus_down(self):
        widget = self.focused_widget
        if isinstance(widget, UIFocusable):
            if widget.neighbor_down:
                self.set_focus(widget.neighbor_down)
                return

        self.focus_next()

    def focus_left(self):
        widget = self.focused_widget
        if isinstance(widget, UIFocusable):
            if widget.neighbor_left:
                self.set_focus(widget.neighbor_left)
                return

        self.focus_previous()

    def focus_right(self):
        widget = self.focused_widget
        if isinstance(widget, UIFocusable):
            if widget.neighbor_right:
                self.set_focus(widget.neighbor_right)
                return

        self.focus_next()

    def focus_next(self):
        """Focus the next widget in the list of focusable widgets of this group"""
        if self.focused_widget is None:
            warnings.warn("No focused widget. Do not change focus.")
            return

        if self.focused_widget not in self._focusable_widgets:
            warnings.warn("Focused widget not in focusable widgets list. Do not change focus.")
            return

        focused_index = self._focusable_widgets.index(self.focused_widget) + 1
        focused_index %= len(self._focusable_widgets)  # wrap around
        self.set_focus(self._focusable_widgets[focused_index])

    def focus_previous(self):
        """Focus the previous widget in the list of focusable widgets of this group"""
        if self.focused_widget is None:
            warnings.warn("No focused widget. Do not change focus.")
            return

        if self.focused_widget not in self._focusable_widgets:
            warnings.warn("Focused widget not in focusable widgets list. Do not change focus.")
            return

        focused_index = self._focusable_widgets.index(self.focused_widget) - 1
        # automatically wrap around via index -1
        self.set_focus(self._focusable_widgets[focused_index])

    def _start_interaction(self):
        # TODO this should be handled in the widget

        widget = self.focused_widget

        if isinstance(widget, UIInteractiveWidget):
            widget.dispatch_ui_event(
                UIMousePressEvent(
                    source=self,
                    x=int(widget.rect.center_x),
                    y=int(widget.rect.center_y),
                    button=MOUSE_BUTTON_LEFT,
                    modifiers=0,
                )
            )
            self._interacting = widget
        else:
            print("Cannot interact widget")

    def _end_interaction(self):
        widget = self.focused_widget

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
                    x=int(x),
                    y=int(y),
                    button=MOUSE_BUTTON_LEFT,
                    modifiers=0,
                )
            )

    def _do_render(self, surface: Surface, force=False) -> bool:
        rendered = super()._do_render(surface, force)

        if rendered:
            self.do_post_render(surface)

        return rendered

    def do_post_render(self, surface: Surface):
        surface.limit(None)

        widget = self.focused_widget
        if not widget:
            return

        if self._debug:
            # debugging
            if isinstance(widget, UIFocusable):
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
        return widget.focus_mode is not FocusMode.NONE


class UIFocusGroup(UIFocusMixin, UIAnchorLayout):
    pass
