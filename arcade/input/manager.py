from enum import Enum
from typing import Any, Callable, Dict, Optional, Set

import pyglet
from pyglet.input.base import Controller

import arcade

from .inputs import InputEnum, InputType, Keys
from .mapping import Action, ActionMapping, Axis, AxisMapping


class ActionState(Enum):
    PRESSED = 1
    RELEASED = 0


class InputDevice(Enum):
    KEYBOARD = 0
    CONTROLLER = 1


class InputManager:

    def __init__(self, controller: Optional[Controller] = None):
        self.actions: Dict[str, Action] = {}
        self.keys_to_actions: Dict[int, Set[str]] = {}
        self.controller_buttons_to_actions: Dict[str, Set[str]] = {}
        self.action_subscribers: Dict[str, Set[Callable[[ActionState], Any]]] = {}
        self.axes: Dict[str, Axis] = {}
        self.axes_state: Dict[str, float] = {}
        self.keys_to_axes: Dict[int, Set[str]] = {}
        self.controller_buttons_to_axes: Dict[str, Set[str]] = {}
        self.controller_analog_to_axes: Dict[str, Set[str]] = {}

        self.window = arcade.get_window()
        self.window.push_handlers(self.on_key_press, self.on_key_release)

        self.active_device = InputDevice.KEYBOARD

        self.controller = None
        self.controller_deadzone = 0.1
        if controller:
            self.controller = controller
            self.controller.open()
            self.controller.push_handlers(
                self.on_button_press, self.on_button_release, self.on_stick_motion
            )
            self.active_device = InputDevice.CONTROLLER

    def bind_controller(self, controller: Controller):
        if self.controller:
            self.controller.remove_handlers()

        self.controller = controller
        self.controller.open()
        self.controller.push_handlers(
            self.on_button_press, self.on_button_release, self.on_stick_motion
        )
        self.active_device = InputDevice.CONTROLLER

    def new_action(
        self,
        name: str,
    ):
        action = Action(name)
        self.actions[name] = action

    def remove_action(self, name: str):
        to_remove = self.actions.get(name, None)
        if to_remove:
            del self.actions[name]

    def add_action_input(
        self,
        action: str,
        input: InputEnum,
        mod_shift: bool = False,
        mod_ctrl: bool = False,
        mod_alt: bool = False,
    ):
        mapping = ActionMapping(input, mod_shift, mod_ctrl, mod_alt)
        self.actions[action].add_mapping(mapping)

        if mapping._input_type == InputType.KEYBOARD:
            # input is guaranteed to be an instance of Keys enum at this point
            if input.value not in self.keys_to_actions:
                self.keys_to_actions[input.value] = set()
            self.keys_to_actions[input.value].add(action)
        elif mapping._input_type == InputType.CONTROLLER_BUTTON:
            if input.value not in self.controller_buttons_to_actions:
                self.controller_buttons_to_actions[input.value] = set()
            self.controller_buttons_to_actions[input.value].add(action)

    def clear_action_input(self, action: str):
        self.actions[action]._mappings = set()

    def subscribe_to_action(self, name: str, subscriber: Callable[[ActionState], Any]):
        old = self.action_subscribers.get(name, set())
        old.add(subscriber)
        self.action_subscribers[name] = old

    def new_axis(self, name: str):
        if name in self.axes:
            raise AttributeError(f"Tried to create Axis with duplicate name: {name}")

        axis = Axis(name)
        self.axes[name] = axis
        self.axes_state[name] = 0.0

    def add_axis_input(self, axis: str, input: InputEnum, scale: float = 1.0):
        mapping = AxisMapping(input, scale)
        self.axes[axis].add_mapping(mapping)

        if mapping._input_type == InputType.KEYBOARD:
            if input.value not in self.keys_to_axes:
                self.keys_to_axes[input.value] = set()
            self.keys_to_axes[input.value].add(axis)
        elif mapping._input_type == InputType.CONTROLLER_BUTTON:
            if input.value not in self.controller_buttons_to_axes:
                self.controller_buttons_to_axes[input.value] = set()
            self.controller_buttons_to_axes[input.value].add(axis)
        elif mapping._input_type == InputType.CONTROLLER_AXIS:
            if input.value not in self.controller_analog_to_axes:
                self.controller_analog_to_axes[input.value] = set()
            self.controller_analog_to_axes[input.value].add(axis)

    def clear_axis_input(self, axis: str):
        self.axes[axis]._mappings = set()

    def remove_axis(self, name: str):
        to_remove = self.axes.get(name, None)
        if to_remove:
            del self.axes[name]
            del self.axes_state[name]

    def axis(self, name: str) -> float:
        return self.axes_state[name]

    def dispatch_action(self, action: str, state: ActionState):
        arcade.get_window().dispatch_event("on_action", action, state)
        if action in self.action_subscribers:
            for subscriber in tuple(self.action_subscribers[action]):
                subscriber(state)

    def on_key_press(self, key: int, modifiers) -> None:
        if self.active_device != InputDevice.KEYBOARD:
            self.active_device = InputDevice.KEYBOARD
        keys_to_actions = tuple(self.keys_to_actions.get(key, set()))
        for action_name in keys_to_actions:
            action = self.actions[action_name]
            hit = True
            for mapping in tuple(action._mappings):
                if mapping._modifiers:
                    for mod in mapping._modifiers:
                        if not modifiers & mod:
                            hit = False

            if hit:
                self.dispatch_action(action_name, ActionState.PRESSED)

        # keys_to_axes = tuple(self.keys_to_axes.get(key, set()))
        # for axis_name in keys_to_axes:
        #     axis = self.axes[axis_name]
        #     for mapping in tuple(axis._mappings):
        #         if mapping._input.value == key:
        #             self.axes_state[axis_name] = mapping._scale
        #             break

    def on_key_release(self, key: int, modifiers) -> None:
        keys_to_actions = tuple(self.keys_to_actions.get(key, set()))
        for action_name in keys_to_actions:
            action = self.actions[action_name]
            hit = True
            for mapping in tuple(action._mappings):
                if mapping._modifiers:
                    for mod in mapping._modifiers:
                        if not modifiers & mod:
                            hit = False

            if hit:
                self.dispatch_action(action_name, ActionState.RELEASED)

        # keys_to_axes = tuple(self.keys_to_axes.get(key, set()))
        # for axis_name in keys_to_axes:
        #     self.axes_state[axis_name] = 0

    def on_button_press(self, controller: Controller, button_name: str):
        if self.active_device != InputDevice.CONTROLLER:
            self.active_device = InputDevice.CONTROLLER
        buttons_to_actions = tuple(
            self.controller_buttons_to_actions.get(button_name, set())
        )
        for action_name in buttons_to_actions:
            self.dispatch_action(action_name, ActionState.PRESSED)

        buttons_to_axes = tuple(self.controller_buttons_to_axes.get(button_name, set()))
        for axis_name in buttons_to_axes:
            axis = self.axes[axis_name]
            for mapping in tuple(axis._mappings):
                scale = mapping._scale
                self.axes_state[axis_name] = scale

    def on_button_release(self, controller: Controller, button_name: str):
        buttons_to_actions = tuple(
            self.controller_buttons_to_actions.get(button_name, set())
        )
        for action_name in buttons_to_actions:
            self.dispatch_action(action_name, ActionState.RELEASED)

        buttons_to_axes = tuple(self.controller_buttons_to_axes.get(button_name, set()))
        for axis_name in buttons_to_axes:
            self.axes_state[axis_name] = 0

    def on_stick_motion(self, controller, name, x_value, y_value):
        if (
            x_value > self.controller_deadzone
            or x_value < -self.controller_deadzone
            or y_value > self.controller_deadzone
            or y_value < -self.controller_deadzone
        ):
            if self.active_device != InputDevice.CONTROLLER:
                self.active_device = InputDevice.CONTROLLER

    def update(self):
        if self.controller and self.active_device == InputDevice.CONTROLLER:
            for name, axis in self.axes.items():
                self.axes_state[name] = 0
                for mapping in tuple(axis._mappings):
                    if mapping._input_type == InputType.CONTROLLER_AXIS:
                        scale = mapping._scale
                        input = getattr(self.controller, mapping._input.value)  # type: ignore
                        if (
                            input > self.controller_deadzone
                            or input < -self.controller_deadzone
                        ):
                            self.axes_state[name] = input * scale
        elif self.active_device == InputDevice.KEYBOARD:
            for name, axis in self.axes.items():
                self.axes_state[name] = 0
                for mapping in tuple(axis._mappings):
                    if mapping._input_type == InputType.KEYBOARD:
                        if self.window.keyboard[mapping._input.value]:
                            self.axes_state[name] = mapping._scale
