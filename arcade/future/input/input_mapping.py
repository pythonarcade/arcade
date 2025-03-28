#  type: ignore
from __future__ import annotations

from arcade.future.input import inputs
from arcade.future.input.raw_dicts import RawAction, RawActionMapping, RawAxis, RawAxisMapping


class Action:
    def __init__(self, name: str) -> None:
        self.name = name
        self._mappings: set[ActionMapping] = set()

    def add_mapping(self, mapping: ActionMapping) -> None:
        self._mappings.add(mapping)

    def remove_mapping(self, mapping: ActionMapping) -> None:
        self._mappings.discard(mapping)


class Axis:
    def __init__(self, name: str) -> None:
        self.name = name
        self._mappings: set[AxisMapping] = set()

    def add_mapping(self, mapping: AxisMapping) -> None:
        self._mappings.add(mapping)

    def remove_mapping(self, mapping: AxisMapping) -> None:
        self._mappings.discard(mapping)


class InputMapping:
    """Base class for other mappings.

    Without subclassing, it's still useful as a type annotation since we
    we use type hashing a lot.
    """

    def __init__(self, input: inputs.InputEnum):
        try:
            self._input_type = inputs.CLASS_TO_INPUT_TYPE[type(input)]
        except KeyError:
            raise TypeError(
                f"Got {input} input specified for ActionMapping must be of of: "
                f"{', '.join((t.__name__ for t in inputs.CLASS_TO_INPUT_TYPE.keys()))}"
            )
        self._input = input


class ActionMapping(InputMapping):
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


class AxisMapping(InputMapping):
    def __init__(self, input: inputs.InputEnum, scale: float):
        super().__init__(input)
        self._scale = scale


def serialize_action(action: Action) -> RawAction:
    raw_mappings: list[RawActionMapping] = []
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
        instance = inputs.parse_mapping_input_enum(raw_mapping)
        axis.add_mapping(
            AxisMapping(
                instance,
                raw_mapping["scale"],
            )
        )

    return axis


def serialize_axis(axis: Axis) -> RawAxis:
    raw_mappings: list[RawAxisMapping] = []
    for mapping in axis._mappings:
        raw_mappings.append(
            {
                "input": mapping._input.value,
                "input_type": mapping._input_type.value,
                "scale": mapping._scale,
            }
        )
    return {"name": axis.name, "mappings": raw_mappings}
