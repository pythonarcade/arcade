""":py:class:`typing.TypedDict` entries.

Placing them here prevents circular import issues.
"""

from typing import Union

from typing_extensions import TypedDict


class RawBindBase(TypedDict):
    """General base for raw axis or action binds.

    Anything matching this can be passed to
    :py:func:`~arcade.future.input.inputs.parse_mapping_input_enum` to
    extract a corresponding :py:class:`~arcade.future.input.inputs.InputEnum`
    value.

    For specific raw types, see:

    * :py:class:`RawActionMapping`
    * :py:class:`RawAxisMapping`
    """

    input_type: int
    input: Union[str, int]


class RawActionMapping(RawBindBase):
    mod_shift: bool
    mod_ctrl: bool
    mod_alt: bool


class RawAxisMapping(RawBindBase):
    scale: float


class RawAction(TypedDict):
    """Annotates the raw form for :py:class:`ActionMapping`."""

    name: str
    mappings: list[RawActionMapping]


class RawAxis(TypedDict):
    """Annotates the raw form for :py:class:`AxisMapping`."""

    name: str
    mappings: list[RawAxisMapping]
