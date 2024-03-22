from enum import Enum
from typing import Any, Callable, Dict, Set

import pyglet

import arcade

from .inputs import InputEnum, InputType, Keys
from .mapping import Action, ActionMapping, Axis, AxisMapping


class ActionState(Enum):
    PRESSED = 1
    RELEASED = 0


class InputManager:

    def __init__(self):
        self.actions: Dict[str, Action] = {}
        self.keys_to_actions: Dict[int, Set[str]] = {}
        self.action_subscribers: Dict[str, Set[Callable[[ActionState], Any]]] = {}
        self.axes: Dict[str, Axis] = {}
        self.axes_state: Dict[str, float] = {}
        self.keys_to_axes: Dict[int, Set[str]] = {}

        self.controller_manager = pyglet.input.ControllerManager()
        self.controller_manager.on_connect = self.on_connect
        self.controller_manager.on_disconnect = self.on_disconnect
        self.controllers = self.controller_manager.get_controllers()

    def on_connect(self, controller):
        self.controllers = self.controller_manager.get_controllers()

    def on_disconnect(self, controller):
        self.controllers = self.controller_manager.get_controllers()

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

    def clear_axis_input(self, axis: str):
        self.axes[axis]._mappings = set()

    def remove_axis(self, name: str):
        to_remove = self.axes.get(name, None)
        if to_remove:
            del self.axes[name]
            del self.axes_state[name]

    def axis(self, name: str) -> float:
        return self.axes_state[name]

    def on_key_press(self, key: int, modifiers) -> None:
        if key not in self.keys_to_actions:
            # We have no actions registered on this key, do nothing
            return

        for action_name in tuple(self.keys_to_actions[key]):
            action = self.actions[action_name]
            for mapping in action._mappings:
                hit = True
                if mapping._modifiers:
                    for mod in mapping._modifiers:
                        if not modifiers & mod:
                            hit = False

                if hit:
                    arcade.get_window().dispatch_event(
                        "on_action", action_name, ActionState.PRESSED
                    )
                    if action_name in self.action_subscribers:
                        for subscriber in tuple(self.action_subscribers[action_name]):
                            subscriber(ActionState.PRESSED)

        for axis_name in tuple(self.keys_to_axes[key]):
            axis = self.axes[axis_name]
            for mapping in axis._mappings:
                scale = mapping._scale
                self.axes_state[axis_name] = scale

    def on_key_release(self, key: int, modifiers) -> None:
        if key not in self.keys_to_actions:
            # We have no actions registered on this key, do nothing
            return

        for action_name in self.keys_to_actions[key]:
            action = self.actions[action_name]
            for mapping in action._mappings:
                hit = True
                if mapping._modifiers:
                    for mod in mapping._modifiers:
                        if not modifiers & mod:
                            hit = False

                if hit:
                    arcade.get_window().dispatch_event(
                        "on_action", action_name, ActionState.RELEASED
                    )
                    if action_name in self.action_subscribers:
                        for subscriber in tuple(self.action_subscribers[action_name]):
                            subscriber(ActionState.RELEASED)

        for axis_name in tuple(self.keys_to_axes[key]):
            self.axes_state[axis_name] = 0
            self.axes_state[axis_name] = 0
