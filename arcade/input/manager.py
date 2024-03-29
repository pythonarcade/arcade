from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

import pyglet
from pyglet.input.base import Controller
from typing_extensions import TypedDict

import arcade

from . import inputs
from .inputs import InputEnum, InputType
from .mapping import (
    Action,
    ActionMapping,
    Axis,
    AxisMapping,
    RawAction,
    RawAxis,
    serialize_action,
    serialize_axis,
)

RawInputManager = TypedDict(
    "RawInputManager",
    {"actions": List[RawAction], "axes": List[RawAxis], "controller_deadzone": float},
)


class ActionState(Enum):
    PRESSED = 1
    RELEASED = 0


class InputDevice(Enum):
    KEYBOARD = 0
    CONTROLLER = 1


class InputManager:

    def __init__(
        self,
        controller: Optional[Controller] = None,
        allow_keyboard: bool = True,
        action_handlers: Union[
            Callable[[str, ActionState], Any], List[Callable[[str, ActionState], Any]]
        ] = [],
        controller_deadzone: float = 0.1,
    ):
        self.actions: Dict[str, Action] = {}
        self.keys_to_actions: Dict[int, Set[str]] = {}
        self.controller_buttons_to_actions: Dict[str, Set[str]] = {}
        self.mouse_buttons_to_actions: Dict[int, Set[str]] = {}
        self.on_action_listeners: List[Callable[[str, ActionState], Any]] = []
        self.action_subscribers: Dict[str, Set[Callable[[ActionState], Any]]] = {}

        self.axes: Dict[str, Axis] = {}
        self.axes_state: Dict[str, float] = {}
        self.keys_to_axes: Dict[int, Set[str]] = {}
        self.controller_buttons_to_axes: Dict[str, Set[str]] = {}
        self.controller_analog_to_axes: Dict[str, Set[str]] = {}

        self.window = arcade.get_window()

        if isinstance(action_handlers, list):
            self.on_action_listeners.extend(action_handlers)
        else:
            self.on_action_listeners.append(action_handlers)

        self._allow_keyboard = allow_keyboard
        if self._allow_keyboard:
            self.window.push_handlers(
                self.on_key_press,
                self.on_key_release,
                self.on_mouse_press,
                self.on_mouse_release,
            )

        self.active_device = None

        if self._allow_keyboard:
            self.active_device = InputDevice.KEYBOARD

        self.controller = None
        self.controller_deadzone = controller_deadzone
        if controller:
            self.controller = controller
            self.controller.open()
            self.controller.push_handlers(
                self.on_button_press,
                self.on_button_release,
                self.on_stick_motion,
                self.on_dpad_motion,
                self.on_trigger_motion,
            )
            self.active_device = InputDevice.CONTROLLER

    def serialize(self) -> RawInputManager:
        raw_actions = []
        for action in self.actions.values():
            raw_actions.append(serialize_action(action))
        raw_axes = []
        for axis in self.axes.values():
            raw_axes.append(serialize_axis(axis))
        return {
            "actions": raw_actions,
            "axes": raw_axes,
            "controller_deadzone": self.controller_deadzone,
        }

    @classmethod
    def parse(cls, raw: RawInputManager) -> InputManager:
        final = cls(controller_deadzone=raw["controller_deadzone"])

        for raw_action in raw["actions"]:
            name = raw_action["name"]
            final.new_action(name)
            for raw_mapping in raw_action["mappings"]:
                raw_input = raw_mapping["input"]
                input_type = inputs.InputType(raw_mapping["input_type"])
                if input_type == inputs.InputType.KEYBOARD:
                    input = inputs.Keys(raw_input)
                elif input_type == inputs.InputType.MOUSE_BUTTON:
                    input = inputs.MouseButtons(raw_input)
                elif input_type == inputs.InputType.MOUSE_AXIS:
                    input = inputs.MouseAxes(raw_input)
                elif input_type == inputs.InputType.CONTROLLER_BUTTON:
                    input = inputs.ControllerButtons(raw_input)
                elif input_type == inputs.InputType.CONTROLLER_AXIS:
                    input = inputs.ControllerAxes(raw_input)
                else:
                    raise AttributeError("Tried to parse an unknown input type")
                final.add_action_input(
                    name,
                    input,
                    raw_mapping["mod_shift"],
                    raw_mapping["mod_ctrl"],
                    raw_mapping["mod_alt"],
                )

        for raw_axis in raw["axes"]:
            name = raw_axis["name"]
            final.new_axis(name)
            for raw_mapping in raw_axis["mappings"]:
                raw_input = raw_mapping["input"]
                input_type = inputs.InputType(raw_mapping["input_type"])
                if input_type == inputs.InputType.KEYBOARD:
                    input = inputs.Keys(raw_input)
                elif input_type == inputs.InputType.MOUSE_BUTTON:
                    input = inputs.MouseButtons(raw_input)
                elif input_type == inputs.InputType.MOUSE_AXIS:
                    input = inputs.MouseAxes(raw_input)
                elif input_type == inputs.InputType.CONTROLLER_BUTTON:
                    input = inputs.ControllerButtons(raw_input)
                elif input_type == inputs.InputType.CONTROLLER_AXIS:
                    input = inputs.ControllerAxes(raw_input)
                else:
                    raise AttributeError("Tried to parse an unknown input type")
                final.add_axis_input(name, input, raw_mapping["scale"])

        return final

    def copy_existing(self, existing: InputManager):
        self.actions = existing.actions.copy()
        self.keys_to_actions = existing.keys_to_actions.copy()
        self.controller_buttons_to_actions = (
            existing.controller_buttons_to_actions.copy()
        )
        self.mouse_buttons_to_actions = existing.mouse_buttons_to_actions.copy()
        self.axes = existing.axes.copy()
        self.axes_state = existing.axes_state.copy()
        self.controller_buttons_to_axes = existing.controller_buttons_to_axes.copy()
        self.controller_analog_to_axes = existing.controller_analog_to_axes.copy()
        self.controller_deadzone = existing.controller_deadzone

    @classmethod
    def from_existing(
        cls,
        existing: InputManager,
        controller: Optional[pyglet.input.Controller] = None,
    ) -> InputManager:
        new = cls(
            allow_keyboard=existing.allow_keyboard,
            controller=controller,
            controller_deadzone=existing.controller_deadzone,
        )
        new.actions = existing.actions.copy()
        new.keys_to_actions = existing.keys_to_actions.copy()
        new.controller_buttons_to_actions = (
            existing.controller_buttons_to_actions.copy()
        )
        new.mouse_buttons_to_actions = existing.mouse_buttons_to_actions.copy()
        new.axes = existing.axes.copy()
        new.axes_state = existing.axes_state.copy()
        new.controller_buttons_to_axes = existing.controller_buttons_to_axes.copy()
        new.controller_analog_to_axes = existing.controller_analog_to_axes.copy()

        return new

    def bind_controller(self, controller: Controller):
        if self.controller:
            self.controller.remove_handlers()

        self.controller = controller
        self.controller.open()
        self.controller.push_handlers(
            self.on_button_press,
            self.on_button_release,
            self.on_stick_motion,
            self.on_dpad_motion,
            self.on_trigger_motion,
        )
        self.active_device = InputDevice.CONTROLLER

    def unbind_controller(self):
        if not self.controller:
            return

        self.controller.remove_handlers(
            self.on_button_press,
            self.on_button_release,
            self.on_stick_motion,
            self.on_dpad_motion,
            self.on_trigger_motion,
        )
        self.controller.close()
        self.controller = None

        if self._allow_keyboard:
            self.active_device = InputDevice.KEYBOARD

    @property
    def allow_keyboard(self):
        return self._allow_keyboard

    @allow_keyboard.setter
    def allow_keyboard(self, value: bool):
        if self._allow_keyboard == value:
            return

        self._allow_keyboard = value
        if self._allow_keyboard:
            self.window.push_handlers(
                self.on_key_press,
                self.on_key_release,
                self.on_mouse_press,
                self.on_mouse_release,
            )
        else:
            self.window.remove_handlers(self)

    def new_action(
        self,
        name: str,
    ):
        action = Action(name)
        self.actions[name] = action

    def remove_action(self, name: str):
        # TODO: Handle all the input->action mappings
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
        elif mapping._input_type == InputType.MOUSE_BUTTON:
            if input.value not in self.mouse_buttons_to_actions:
                self.mouse_buttons_to_actions[input.value] = set()
            self.mouse_buttons_to_actions[input.value].add(action)

    def clear_action_input(self, action: str):
        # TODO: Handle all the input->action mappings(this is just clearing the underlying mapping right now, not the actual link to an action)
        self.actions[action]._mappings = set()

    def register_action_handler(
        self,
        handler: Union[
            Callable[[str, ActionState], Any], List[Callable[[str, ActionState], Any]]
        ],
    ):
        if isinstance(handler, list):
            self.on_action_listeners.extend(handler)
        else:
            self.on_action_listeners.append(handler)

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
        # TODO: handle the input->axis mappings
        self.axes[axis]._mappings = set()

    def remove_axis(self, name: str):
        # TODO: handle the input->axis mappings
        to_remove = self.axes.get(name, None)
        if to_remove:
            del self.axes[name]
            del self.axes_state[name]

    def axis(self, name: str) -> float:
        return self.axes_state[name]

    def dispatch_action(self, action: str, state: ActionState):
        arcade.get_window().dispatch_event("on_action", action, state)
        for listener in self.on_action_listeners:
            listener(action, state)
        if action in self.action_subscribers:
            for subscriber in tuple(self.action_subscribers[action]):
                subscriber(state)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if not self._allow_keyboard:
            return

        self.active_device = InputDevice.KEYBOARD
        mouse_buttons_to_actions = tuple(
            self.mouse_buttons_to_actions.get(button, set())
        )
        for action_name in mouse_buttons_to_actions:
            action = self.actions[action_name]
            hit = True
            for mapping in tuple(action._mappings):
                if mapping._modifiers:
                    for mod in mapping._modifiers:
                        if not modifiers & mod:
                            hit = False

            if hit:
                self.dispatch_action(action_name, ActionState.PRESSED)

    def on_key_press(self, key: int, modifiers) -> None:
        if not self._allow_keyboard:
            return

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

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if not self._allow_keyboard:
            return

        mouse_buttons_to_actions = tuple(
            self.mouse_buttons_to_actions.get(button, set())
        )
        for action_name in mouse_buttons_to_actions:
            action = self.actions[action_name]
            hit = True
            for mapping in tuple(action._mappings):
                if mapping._modifiers:
                    for mod in mapping._modifiers:
                        if not modifiers & mod:
                            hit = False

            if hit:
                self.dispatch_action(action_name, ActionState.RELEASED)

    def on_key_release(self, key: int, modifiers) -> None:
        if not self._allow_keyboard:
            return

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

    def on_button_press(self, controller: Controller, button_name: str):
        self.active_device = InputDevice.CONTROLLER
        buttons_to_actions = tuple(
            self.controller_buttons_to_actions.get(button_name, set())
        )
        for action_name in buttons_to_actions:
            self.dispatch_action(action_name, ActionState.PRESSED)

    def on_button_release(self, controller: Controller, button_name: str):
        buttons_to_actions = tuple(
            self.controller_buttons_to_actions.get(button_name, set())
        )
        for action_name in buttons_to_actions:
            self.dispatch_action(action_name, ActionState.RELEASED)

    def on_stick_motion(self, controller, name, x_value, y_value):
        if (
            x_value > self.controller_deadzone
            or x_value < -self.controller_deadzone
            or y_value > self.controller_deadzone
            or y_value < -self.controller_deadzone
        ):
            self.active_device = InputDevice.CONTROLLER

    def on_dpad_motion(
        self, controller: Controller, left: bool, right: bool, up: bool, down: bool
    ):
        self.active_device = InputDevice.CONTROLLER

    def on_trigger_motion(
        self, controller: Controller, trigger_name: str, value: float
    ):
        self.active_device = InputDevice.CONTROLLER

    def update(self):
        for name in self.axes.keys():
            self.axes_state[name] = 0

        if self.controller and self.active_device == InputDevice.CONTROLLER:
            for name, axis in self.axes.items():
                for mapping in tuple(axis._mappings):
                    if mapping._input_type == InputType.CONTROLLER_AXIS:
                        scale = mapping._scale
                        input = getattr(self.controller, mapping._input.value)  # type: ignore
                        if (
                            input > self.controller_deadzone
                            or input < -self.controller_deadzone
                        ):
                            self.axes_state[name] = input * scale
                    if mapping._input_type == InputType.CONTROLLER_BUTTON:
                        if getattr(self.controller, mapping._input.value):  # type: ignore
                            self.axes_state[name] = mapping._scale
        elif self.active_device == InputDevice.KEYBOARD and self._allow_keyboard:
            for name, axis in self.axes.items():
                for mapping in tuple(axis._mappings):
                    if mapping._input_type == InputType.KEYBOARD:
                        if self.window.keyboard[mapping._input.value]:
                            self.axes_state[name] = mapping._scale
                    elif mapping._input_type == InputType.MOUSE_AXIS:
                        self.axes_state[name] = (
                            self.window.mouse[mapping._input.name.lower()]
                            * mapping._scale
                        )
                    elif mapping._input_type == InputType.MOUSE_BUTTON:
                        if self.window.mouse[mapping._input.value]:
                            self.axes_state[name] = mapping._scale
