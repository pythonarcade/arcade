from dataclasses import dataclass

from pyglet.input import Controller
from pyglet.math import Vec2

from arcade import ControllerManager
from arcade.gui import (
    UIEvent,
    UIManager,
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
class UIControllerButtonEvent(UIControllerEvent):
    """Triggered when a controller button used.

    Args:
        button: The name of the button.
    """

    button: str


@dataclass
class UIControllerButtonPressEvent(UIControllerButtonEvent):
    """Triggered when a controller button is pressed.

    Args:
        button: The name of the button.
    """


@dataclass
class UIControllerButtonReleaseEvent(UIControllerButtonEvent):
    """Triggered when a controller button is released.

    Args:
        button: The name of the button.
    """


@dataclass
class UIControllerDpadEvent(UIControllerEvent):
    """Triggered when a controller dpad is moved.

    Args:
        vector: The value of the dpad.
    """

    vector: Vec2


class _ControllerListener:
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


class UIControllerBridge(_ControllerListener):
    """Translates controller events to UIEvents and passes them to the UIManager.

    Controller are automatically connected and disconnected.

    Controller events are consumed by the UIControllerBridge,
    if the UIEvent is consumed by the UIManager.

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
        return self.ui.dispatch_ui_event(UIControllerStickEvent(controller, name, value))

    def on_trigger_motion(self, controller: Controller, name, value):
        return self.ui.dispatch_ui_event(UIControllerTriggerEvent(controller, name, value))

    def on_button_press(self, controller: Controller, button):
        return self.ui.dispatch_ui_event(UIControllerButtonPressEvent(controller, button))

    def on_button_release(self, controller: Controller, button):
        return self.ui.dispatch_ui_event(UIControllerButtonReleaseEvent(controller, button))

    def on_dpad_motion(self, controller: Controller, value):
        return self.ui.dispatch_ui_event(UIControllerDpadEvent(controller, value))
