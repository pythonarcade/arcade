from dataclasses import dataclass
from typing import Optional

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED
from pyglet.input import Controller
from pyglet.math import Vec2

import arcade
from arcade import ControllerManager, MOUSE_BUTTON_LEFT
from arcade.gui import (
    ListProperty,
    Property,
    Surface,
    UIAnchorLayout,
    UIEvent,
    UIInteractiveWidget,
    UIManager,
    UIMousePressEvent,
    UIMouseReleaseEvent,
    UIWidget,
    bind,
)


@dataclass
class UIControllerEvent(UIEvent):
    """Base class for all UI controller events.

    Args:
        source: The controller that triggered the event.
    """


@dataclass
class UIControllerStickEvent(UIControllerEvent):
    """Triggered when a controller stick is moved.

    Args:
        name: The name of the stick.
        vector: The value of the stick.
    """

    name: str
    vector: Vec2


@dataclass
class UIControllerTriggerEvent(UIControllerEvent):
    """Triggered when a controller trigger is moved.

    Args:
        name: The name of the trigger.
        value: The value of the trigger.
    """

    name: str
    value: float


@dataclass
class UIControllerButtonPressEvent(UIControllerEvent):
    """Triggered when a controller button is pressed.

    Args:
        button: The name of the button.
    """

    button: str


@dataclass
class UIControllerButtonReleaseEvent(UIControllerEvent):
    """Triggered when a controller button is released.

    Args:
        button: The name of the button.
    """

    button: str


@dataclass
class UIControllerDpadEvent(UIControllerEvent):
    """Triggered when a controller dpad is moved.

    Args:
        vector: The value of the dpad.
    """

    vector: Vec2


class ControllerListener:
    """Interface for listening to controller events"""

    def on_stick_motion(self, controller: Controller, name: str, value: Vec2):
        pass

    def on_trigger_motion(self, controller: Controller, name: str, value: float):
        pass

    def on_button_press(self, controller: Controller, button_name: str):
        pass

    def on_button_release(self, controller: Controller, button_name: str):
        pass

    def on_dpad_motion(self, controller: Controller, value: Vec2):
        pass


class UIControllerBridge(ControllerListener):
    """Translates controller events to UIEvents and passes them to the UIManager

    Controller events are not consumed by the UIControllerBridge,
    so they can be used by other systems.

    #TODO change this
    This implicates, that the UIControllerBridge should be the first listener in the chain and
    that other systems should be aware, when not to act on events (like when the UI is active).
    """

    def __init__(self, ui: UIManager):
        self.ui = ui
        self.cm = ControllerManager()

        self.cm.push_handlers(self)
        # bind to existing controllers
        for controller in self.cm.get_controllers():
            print("Controller connected", controller)
            self.on_connect(controller)

    def on_connect(self, controller: Controller):
        controller.push_handlers(self)
        controller.open()

    def on_disconnect(self, controller: Controller):
        controller.remove_handlers(self)
        controller.close()

    # Controller event mapping
    def on_stick_motion(self, controller: Controller, name, value):
        self.ui.dispatch_ui_event(UIControllerStickEvent(controller, name, value))

    def on_trigger_motion(self, controller: Controller, name, value):
        self.ui.dispatch_ui_event(UIControllerTriggerEvent(controller, name, value))

    def on_button_press(self, controller: Controller, button):
        self.ui.dispatch_ui_event(UIControllerButtonPressEvent(controller, button))

    def on_button_release(self, controller: Controller, button):
        self.ui.dispatch_ui_event(UIControllerButtonReleaseEvent(controller, button))

    def on_dpad_motion(self, controller: Controller, value):
        self.ui.dispatch_ui_event(UIControllerDpadEvent(controller, value))


class UIFocusGroup(UIAnchorLayout):
    """A group of widgets that can be focused.

    UIFocusGroup maintains two lists of widgets:
    - The list of focusable widgets.
    - The list of widgets in.

    Use detect_focusable_widgets to automatically detect focusable widgets
    or add_widget to add them manually.

    """

    _widgets = ListProperty[UIWidget]()
    _focused = Property(0)

    def __init__(self, size_hint=(1, 1), **kwargs):
        super().__init__(size_hint=size_hint, **kwargs)

        bind(self, "_focused", self.trigger_full_render)
        bind(self, "_widgets", self.trigger_full_render)

    def on_event(self, event: UIEvent) -> Optional[bool]:

        if super().on_event(event):
            return EVENT_HANDLED

        if isinstance(event, UIControllerDpadEvent):
            if event.vector.x == 1 or event.vector.y == -1:
                self.focus_next()
                return EVENT_HANDLED
            elif event.vector.x == -1 or event.vector.y == 1:
                self.focus_previous()
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
        self._widgets.append(widget)

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

        self._widgets = focusable_widgets

    def focus_next(self):
        self._focused += 1
        if self._focused >= len(self._widgets):
            self._focused = 0

    def focus_previous(self):
        self._focused -= 1
        if self._focused < 0:
            self._focused = len(self._widgets) - 1

    def start_interaction(self):
        widget = self._widgets[self._focused]

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
        else:
            print("Cannot interact widget")

    def end_interaction(self):
        widget = self._widgets[self._focused]

        if isinstance(widget, UIInteractiveWidget):
            widget.dispatch_ui_event(
                UIMouseReleaseEvent(
                    source=self,
                    x=widget.rect.center_x,
                    y=widget.rect.center_y,
                    button=MOUSE_BUTTON_LEFT,
                    modifiers=0,
                )
            )

    # TODO render after children rendered
    def do_render(self, surface: Surface):
        surface.limit(None)
        widget = self._widgets[self._focused]
        arcade.draw_rect_outline(
            rect=widget.rect,
            color=arcade.color.WHITE,
            border_width=2,
        )

    @staticmethod
    def is_focusable(widget):
        return isinstance(widget, UIInteractiveWidget)
