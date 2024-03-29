from __future__ import annotations

from enum import Enum
from typing import List, Set, Union

from typing_extensions import TypedDict

from arcade.input import inputs

RawActionMapping = TypedDict(
    "RawActionMapping",
    {
        "input_type": int,
        "input": Union[str, int],
        "mod_shift": bool,
        "mod_ctrl": bool,
        "mod_alt": bool,
    },
)
RawAxisMapping = TypedDict(
    "RawAxisMapping", {"input_type": int, "input": Union[str, int], "scale": float}
)

RawAction = TypedDict("RawAction", {"name": str, "mappings": List[RawActionMapping]})
RawAxis = TypedDict("RawAxis", {"name": str, "mappings": List[RawAxisMapping]})


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
        if isinstance(input, inputs.Keys):
            self._input_type = inputs.InputType.KEYBOARD
        elif isinstance(input, inputs.MouseButtons):
            self._input_type = inputs.InputType.MOUSE_BUTTON
        elif isinstance(input, inputs.MouseAxes):
            self._input_type = inputs.InputType.MOUSE_AXIS
        elif isinstance(input, inputs.ControllerButtons):
            self._input_type = inputs.InputType.CONTROLLER_BUTTON
        elif isinstance(input, inputs.ControllerAxes):
            self._input_type = inputs.InputType.CONTROLLER_AXIS
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


def serialize_action(action: Action) -> RawAction:
    raw_mappings: List[RawActionMapping] = []
    for mapping in action._mappings:
        raw_mappings.append(
            {
                "input": mapping._input.value,
                "input_type": mapping._input_type.value,
                "mod_shift": inputs.Keys.MOD_SHIFT in mapping._modifiers,
                "mod_ctrl": inputs.Keys.MOD_ACCEL in mapping._modifiers,
                "mod_alt": (
                    inputs.Keys.MOD_ALT in mapping._modifiers
                    or inputs.Keys.MOD_OPTION in mapping._modifiers
                ),
            }
        )
    return {"name": action.name, "mappings": raw_mappings}


def parse_raw_axis(raw_axis: RawAxis) -> Axis:
    axis = Axis(raw_axis["name"])
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
        axis.add_mapping(
            AxisMapping(
                input,
                raw_mapping["scale"],
            )
        )

    return axis


def serialize_axis(axis: Axis) -> RawAxis:
    raw_mappings: List[RawAxisMapping] = []
    for mapping in axis._mappings:
        raw_mappings.append(
            {
                "input": mapping._input.value,
                "input_type": mapping._input_type.value,
                "scale": mapping._scale,
            }
        )
    return {"name": axis.name, "mappings": raw_mappings}
