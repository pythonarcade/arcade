from __future__ import annotations

from enum import Enum
from typing import List, Set

from arcade.input import inputs


class Action:

    def __init__(self, name: str) -> None:
        self.name = name
        self._mappings: Set[ActionMapping] = set()

    def add_mapping(self, mapping: ActionMapping) -> None:
        self._mappings.add(mapping)

    def remove_mapping(self, mapping: ActionMapping) -> None:
        try:
            self._mappings.remove(mapping)
        except KeyError:
            pass


class Axis:

    def __init__(self, name: str) -> None:
        self.name = name
        self._mappings: Set[AxisMapping] = set()

    def add_mapping(self, mapping: AxisMapping) -> None:
        self._mappings.add(mapping)

    def remove_mapping(self, mapping: AxisMapping) -> None:
        try:
            self._mappings.remove(mapping)
        except KeyError:
            pass


class Mapping:

    def __init__(self, input: inputs.InputEnum):
        if type(input) == inputs.Keys:
            self._input_type = inputs.InputType.KEYBOARD
        elif isinstance(input, inputs.MouseButtons):
            self._input_type = inputs.InputType.MOUSE_BUTTON
        elif isinstance(input, inputs.ControllerButtons):
            self._input_type = inputs.InputType.CONTROLLER_BUTTON
        elif isinstance(input, inputs.InputEnum):
            self._input_type = inputs.InputType.OTHER
        else:
            raise TypeError(
                "Input specified for ActionMapping must inherit from InputEnum"
            )

        self._input = input


class ActionMapping(Mapping):

    def __init__(
        self,
        input: inputs.InputEnum,
        mod_shift: bool = False,
        mod_ctrl: bool = False,
        mod_alt: bool = False,
    ):
        super().__init__(input)
        self._modifiers = set()
        if mod_shift:
            self._modifiers.add(inputs.Keys.MOD_SHIFT.value)
        if mod_ctrl:
            self._modifiers.add(inputs.Keys.MOD_ACCEL.value)
        if mod_alt:
            self._modifiers.add(inputs.Keys.MOD_ALT.value)
            self._modifiers.add(inputs.Keys.MOD_OPTION.value)


class AxisMapping(Mapping):

    def __init__(self, input: inputs.InputEnum, scale: float):
        super().__init__(input)
        self._scale = scale
