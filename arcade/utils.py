"""
Various utility functions.

IMPORTANT:
These  should be standalone and not rely on any arcade imports
"""
import functools
import platform
import sys
import warnings
from typing import Tuple, Type, TypeVar
from pathlib import Path


_CT = TypeVar('_CT')  # Comparable type, ie supports the <= operator

__all__ = [
    "OutsideRangeError",
    "IntOutsideRangeError",
    "FloatOutsideRangeError",
    "ByteRangeError",
    "NormalizedRangeError",
    "PerformanceWarning",
    "ReplacementWarning",
    "warning",
    "generate_uuid_from_kwargs",
    "is_raspberry_pi",
    "get_raspberry_pi_info"
]


class OutsideRangeError(ValueError):
    """
    Raised when a value is outside and expected range

    This class and its subclasses are intended to be arcade-internal
    helpers to clearly signal exactly what went wrong. Each helps
    type annotate and template a string describing exactly what went
    wrong.

    :param var_name: the name of the variable or argument
    :param value: the value to fall outside the expected range
    :param lower: the lower bound, inclusive, of the range
    :param upper: the upper bound, inclusive, of the range
    """
    def __init__(self, var_name: str, value: _CT, lower: _CT, upper: _CT):
        super().__init__(f"{var_name} must be between {lower} and {upper}, inclusive, not {value}")
        self.var_name = var_name
        self.value = value
        self.lower = lower
        self.upper = upper


class IntOutsideRangeError(OutsideRangeError):
    """
    An integer was outside an expected range

    This class was originally intended to assist deserialization from
    data packed into ints, such as :py:class:`~arcade.types.Color`.

    :param var_name: the name of the variable or argument
    :param value: the value to fall outside the expected range
    :param lower: the lower bound, inclusive, of the range
    :param upper: the upper bound, inclusive, of the range
    """
    def __init__(self, var_name: str, value: int, lower: int, upper: int):
        super().__init__(var_name, value, lower, upper)


class FloatOutsideRangeError(OutsideRangeError):
    """
    A float value was outside an expected range

    :param var_name: the name of the variable or argument
    :param value: the value to fall outside the expected range
    :param lower: the lower bound, inclusive, of the range
    :param upper: the upper bound, inclusive, of the range
    """
    def __init__(self, var_name: str, value: float, lower: float, upper: float):
        super().__init__(var_name, value, lower, upper)


class ByteRangeError(IntOutsideRangeError):
    """
    An int was outside the range of 0 to 255 inclusive

    :param var_name: the name of the variable or argument
    :param value: the value to fall outside the expected range
    """
    def __init__(self, var_name: str, value: int):
        super().__init__(var_name, value, 0, 255)


class NormalizedRangeError(FloatOutsideRangeError):
    """
    A float was not between 0.0 and 1.0, inclusive

    Note that normalized floats should not normally be bound-checked as
    before drawing as this is taken care of on the GPU side.

    The exceptions to this are when processing data on the Python side,
    especially when it is cheaper to bound check two floats than call
    clamping functions.

    :param var_name: the name of the variable or argument
    :param value: the value to fall outside the expected range
    """
    def __init__(self, var_name: str, value: float):
        super().__init__(var_name, value, 0.0, 1.0)


class PerformanceWarning(Warning):
    """Use this for issuing performance warnings."""
    pass


class ReplacementWarning(Warning):
    """Use this for issuing warnings about naming and functionality changes."""
    pass


def warning(warning_type: Type[Warning], message: str = "", **kwargs):
    def actual_warning_decorator(func):
        nonlocal message
        if warning_type == ReplacementWarning and not message:
            message = f"{func.__name__} is deprecated. Use {kwargs.get('new_name', '')} instead."
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(message, warning_type)
            return func(*args, **kwargs)
        return wrapper
    return actual_warning_decorator


def generate_uuid_from_kwargs(**kwargs) -> str:
    """
    Given key/pair combos, returns a string in uuid format.
    Such as `text='hi', size=32` it will return "text-hi-size-32".
    Called with no parameters, id does NOT return a random unique id.
    """
    if len(kwargs) == 0:
        raise Exception("generate_uuid_from_kwargs has to be used with kwargs, please check the doc.")

    return "|".join(f"{key}={str(value)}" for key, value in kwargs.items())


def is_raspberry_pi() -> bool:
    """
    Determine if the host is a raspberry pi.

    :returns: bool
    """
    return get_raspberry_pi_info()[0]


def get_raspberry_pi_info() -> Tuple[bool, str, str]:
    """
    Determine if the host is a raspberry pi
    with additional info.

    :returns: 3 component tuple.
              bool (is host a raspi)
              str (architecture)
              str (model name)
    """
    # armv7l is raspi 32 bit
    # aarch64 is raspi 64 bit
    architecture = platform.machine()
    model_name = ""

    # The platform for raspi should always be linux
    if not sys.platform == "linux":
        return False, "", ""

    # Check for model info file
    MODEL_PATH = Path("/sys/firmware/devicetree/base/model")
    if MODEL_PATH.exists():
        try:
            model_name = MODEL_PATH.read_text()[:-1]
            if "raspberry pi" in model_name.lower():
                return True, architecture, model_name
        except Exception:
            pass

    return False, "", ""
