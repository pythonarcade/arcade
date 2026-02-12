# type: ignore
from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any, TypeVar

import pyglet
from pyglet.input.base import Controller
from typing_extensions import TypedDict

import arcade
from arcade.input import inputs
from arcade.input.input_mapping import (
    Action,
    ActionMapping,
    Axis,
    AxisMapping,
    serialize_action,
    serialize_axis,
)
from arcade.input.inputs import InputEnum, InputType
from arcade.input.raw_dicts import RawAction, RawAxis
from arcade.types import OneOrIterableOf
from arcade.utils import grow_sequence


class RawInputManager(TypedDict):
    actions: list[RawAction]
    axes: list[RawAxis]
    controller_deadzone: float


_K = TypeVar("_K")
_V = TypeVar("_V")


def _clean_dicts(to_remove: _V, *dicts_to_clean: dict[_K, set[_V]]) -> None:
    """Clean a dictionary in-place.

    This helps simplify serialization code for controller config.
    """
    to_discard = []
    for to_clean in dicts_to_clean:
        if to_discard:
            to_discard.clear()

        for key, set_value in to_clean.items():
            set_value.discard(to_remove)
            if len(set_value) == 0:
                to_discard.append(key)

        for key in to_discard:
            del to_clean[key]


class ActionState(Enum):
    PRESSED = 1
    RELEASED = 0


class InputDevice(Enum):
    KEYBOARD = 0
    CONTROLLER = 1


class InputManager:
    """
    The InputManager is responsible for managing input for a given device, this can be the keyboard/mouse or a controller.

    In general, you can share one InputManager for one controller and the keyboard/mouse, there are even utilities to handle
    automatically switching between them as the active device. However if you intend to have multiple controllers connected
    to your game, each controller should have it's own InputManager.

    For runnable examples of how to use this, please see Arcdade's
    :ref:`built-in InputManager examples <input_manager_examples>`.

    Args:
        controller:
            Either a Pyglet Controller object or None if you only want to use the keyboard/mouse.
        allow_keyboard:
            Whether to allow keyboard input, defaults to True, can be changed safely after initialization.
        action_handlers:
            Either one or a collection of functions that will be called for every action that is triggered.
            :py:meth:`InputManager.subscribe_to_action` may be preferred to subscribe to individual actions instead.
        controller_deadzone:
            The deadzone for controller input, defaults to 0.1. If changes to axis values are within this
            range from the underlying hardware, they will be ignored.
    """
    def __init__(
        self,
        controller: Controller | None = None,
        allow_keyboard: bool = True,
        action_handlers: OneOrIterableOf[Callable[[str, ActionState], Any]] = tuple(),
        controller_deadzone: float = 0.1,
    ):
        self.actions: dict[str, Action] = {}

        # We don't use defaultdict here since:
        # 1. These attributes are unprotected
        # 2. That means sets would be created on *any* access by the user
        # 2. Those leftover sets would complicate serialization
        self.keys_to_actions: dict[int, set[str]] = {}
        self.controller_buttons_to_actions: dict[str, set[str]] = {}
        self.controller_axes_to_actions: dict[str, set[str]] = {}
        self.mouse_buttons_to_actions: dict[int, set[str]] = {}

        self.on_action_listeners: list[Callable[[str, ActionState], Any]] = []
        self.action_subscribers: dict[str, set[Callable[[ActionState], Any]]] = {}

        self.axes: dict[str, Axis] = {}
        self.axes_state: dict[str, float] = {}
        self.keys_to_axes: dict[int, set[str]] = {}
        self.controller_buttons_to_axes: dict[str, set[str]] = {}
        self.controller_analog_to_axes: dict[str, set[str]] = {}

        self.window = arcade.get_window()

        self.register_action_handler(action_handlers)

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
            if not self.controller.device.is_open:
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
        """
        Serializes the current state of the InputManager into a RawInputManager dictionary which can easily be saved to JSON.

        This does not include current values of inputs, but rather the structure of the InputManager. Including:
          - Actions: All registered actions
          - Axes: All registered axis inputs
          - Current Mappings: All current mappings of underlying inputs to actions/axis

        The output dictionary of this function can be passed to :meth:`arcade.InputManager.parse` to create a new InputManager
        from a serialized one.

        Returns:
            A RawInputManager dictionary representing the current state of the InputManager.
        """
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
        """
        Create a new InputManager from a serialized dictionary. Can be used in combination with the :meth:`arcade.InputManager.serialize` to
        save/load input configurations.

        Returns:
            A new InputManager with the state defined in the provided RawInputManager dictionary.
        """
        final = cls(controller_deadzone=raw["controller_deadzone"])

        for raw_action in raw["actions"]:
            name = raw_action["name"]
            final.new_action(name)

            for raw_mapping in raw_action["mappings"]:
                input_instance = inputs.parse_instance(raw_mapping)

                final.add_action_input(
                    name,
                    input_instance,
                    raw_mapping["mod_shift"],
                    raw_mapping["mod_ctrl"],
                    raw_mapping["mod_alt"],
                )

        for raw_axis in raw["axes"]:
            name = raw_axis["name"]
            final.new_axis(name)
            for raw_mapping in raw_axis["mappings"]:
                input_instance = inputs.parse_instance(raw_mapping)

                final.add_axis_input(name, input_instance, raw_mapping["scale"])

        return final

    def copy_existing(self, existing: InputManager):
        """
        Copies the state of another InputManager into this one. Note that this does not create a new InputManager, but modifies the one on which it is called.

        This does not copy current input values, just the structure/mappings of the InputManager.

        If you want to create a new InputManager from an existing one, use :meth:`arcade.InputManager.from_existing`

        Args:
            existing: The InputManager to copy from.
        """
        self.actions = existing.actions.copy()
        self.keys_to_actions = existing.keys_to_actions.copy()
        self.controller_buttons_to_actions = existing.controller_buttons_to_actions.copy()
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
        controller: pyglet.input.Controller | None = None,
    ) -> InputManager:
        """
        Create a new InputManager from an existing one. This does not copy current input values, just the structure/mappings of the InputManager.

        If you want to create a new InputManager from a serialized dictionary, use :meth:`arcade.InputManager.parse`

        Args:
            existing: The InputManager to copy from.
            controller: The controller to use for this InputManager. If None, no Controller will be bound.

        Returns:
            A new InputManager with the state defined in the provided existing InputManager.
        """
        new = cls(
            allow_keyboard=existing.allow_keyboard,
            controller=controller,
            controller_deadzone=existing.controller_deadzone,
        )
        new.copy_existing(existing)

        return new

    def bind_controller(self, controller: Controller):
        """
        Bind a controller to this InputManager. If a controller is already bound, it will be unbound first.

        Upon binding a controller it will be set as the active device.

        Args:
            controller: The controller to bind to this InputManager.
        """
        if self.controller:
            self.unbind_controller()

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
        """
        Unbind the currently bound controller from this InputManager.
        """
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
        """
        Whether the keyboard is allowed for this InputManager. This also effects mouse input.

        If this is false then all keyboard and mouse input will be ignored regardless of if there are mappings for them.
        """
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
        """
        Create a new action with the given name. If an action with the same name already exists, this will do nothing.

        Args:
            name: The name of the action to create.
        """
        if name in self.actions:
            return

        action = Action(name)
        self.actions[name] = action

    def remove_action(self, name: str):
        """
        Remove the specified action. If the action does not exist, this will do nothing.

        Args:
            name: The name of the action to remove.
        """
        to_remove = self.actions.get(name, None)
        if to_remove:
            self.clear_action_input(name)
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
        elif mapping._input_type == InputType.CONTROLLER_AXIS:
            if input.value not in self.controller_axes_to_actions:
                self.controller_axes_to_actions[input.value] = set()
            self.controller_axes_to_actions[input.value].add(action)

    def clear_action_input(self, action: str):
        self.actions[action]._mappings.clear()
        _clean_dicts(
            action,
            self.keys_to_actions,
            self.controller_buttons_to_actions,
            self.controller_axes_to_actions,
            self.mouse_buttons_to_actions,
        )

    def register_action_handler(self, handler: OneOrIterableOf[Callable[[str, ActionState], Any]]):
        grow_sequence(self.on_action_listeners, handler, append_if=callable)

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

    def add_axis_input_combined(self, axis: str, positive: InputEnum, negative: InputEnum, scale: float = 1.0):
        """
        This is a helper function that wraps :meth:`arcade.InputManager.add_axis_input` to add two inputs
        with a positive and negative scale.

        For example, you can do:
        add_axis_input_combined("MoveHorizontal", arcade.Keys.RIGHT, arcade.Keys.LEFT, 1.0)
        instead of:
        add_axis_input("MoveHorizontal", arcade.Keys.RIGHT, 1.0)
        add_axis_input("MoveHorizontal", arcade.Keys.LEFT, -1.0)

        Args:
            axis: The axis name to register the input for
            positive: The input that will correspond to the positive side of the axis
            negative: The input that will correspond to the negative side of the axis
            scale: The value to multiply the input by, for non analog inputs the scale value is used literally.
        """
        self.add_axis_input(axis, positive, scale)
        self.add_axis_input(axis, negative, -scale)

    def clear_axis_input(self, axis: str):
        self.axes[axis]._mappings.clear()
        _clean_dicts(
            axis, self.keys_to_axes, self.controller_analog_to_axes, self.controller_buttons_to_axes
        )

    def remove_axis(self, name: str):
        self.clear_axis_input(name)

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
        mouse_buttons_to_actions = tuple(self.mouse_buttons_to_actions.get(button, set()))
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

    def on_key_press(self, key: int, modifiers: int) -> None:
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

        mouse_buttons_to_actions = tuple(self.mouse_buttons_to_actions.get(button, set()))
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

    def on_key_release(self, key: int, modifiers: int) -> None:
        if not self._allow_keyboard:
            return
        # What, why are we doing any of this repeat tuple conversion in here?
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
        buttons_to_actions = tuple(self.controller_buttons_to_actions.get(button_name, set()))
        for action_name in buttons_to_actions:
            self.dispatch_action(action_name, ActionState.PRESSED)

    def on_button_release(self, controller: Controller, button_name: str):
        buttons_to_actions = tuple(self.controller_buttons_to_actions.get(button_name, set()))
        for action_name in buttons_to_actions:
            self.dispatch_action(action_name, ActionState.RELEASED)

    def on_stick_motion(self, controller: Controller, name: str, motion: pyglet.math.Vec2):
        x_value, y_value = motion.x, motion.y
        if name == "leftx":
            self.window.dispatch_event(
                "on_stick_motion",
                self.controller,
                "leftxpositive" if x_value > 0 else "leftxnegative",
                x_value,
                y_value,
            )
        elif name == "lefty":
            self.window.dispatch_event(
                "on_stick_motion",
                self.controller,
                "leftypositive" if y_value > 0 else "leftynegative",
                x_value,
                y_value,
            )
        elif name == "rightx":
            self.window.dispatch_event(
                "on_stick_motion",
                self.controller,
                "rightxpositive" if x_value > 0 else "rightxpositive",
                x_value,
                y_value,
            )
        elif name == "righty":
            self.window.dispatch_event(
                "on_stick_motion",
                self.controller,
                "rightypositive" if y_value > 0 else "rightynegative",
                x_value,
                y_value,
            )

        axes_to_actions = self.controller_axes_to_actions.get(name, set())

        if (
            x_value > self.controller_deadzone
            or x_value < -self.controller_deadzone
            or y_value > self.controller_deadzone
            or y_value < -self.controller_deadzone
        ):
            self.active_device = InputDevice.CONTROLLER

            for action_name in axes_to_actions:
                self.dispatch_action(action_name, ActionState.PRESSED)

            return

        for action_name in axes_to_actions:
            self.dispatch_action(action_name, ActionState.RELEASED)

    def on_dpad_motion(self, controller: Controller, motion: pyglet.math.Vec2):
        self.active_device = InputDevice.CONTROLLER

    def on_trigger_motion(self, controller: Controller, trigger_name: str, value: float):
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
                        if input > self.controller_deadzone or input < -self.controller_deadzone:
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
                            self.window.mouse[mapping._input.name.lower()] * mapping._scale
                        )
                    elif mapping._input_type == InputType.MOUSE_BUTTON:
                        if self.window.mouse[mapping._input.value]:
                            self.axes_state[name] = mapping._scale
