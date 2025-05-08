"""
Custom Arcade errors, exceptions, and warnings.
"""

import functools
import warnings
from typing import TypeVar

__all__ = [
    "OutsideRangeError",
    "IntOutsideRangeError",
    "FloatOutsideRangeError",
    "ByteRangeError",
    "NormalizedRangeError",
    "PerformanceWarning",
    "ReplacementWarning",
    "warning",
]

# Since this module forbids importing from the rest of
# Arcade, we make our own local type variables.
_TType = TypeVar("_TType", bound=type)
_CT = TypeVar("_CT")  # Comparable type, ie supports the <= operator


class OutsideRangeError(ValueError):
    """
    Raised when a value is outside and expected range

    This class and its subclasses are intended to be Arcade-internal
    helpers to clearly signal exactly what went wrong. Each helps
    type annotate and template a string describing exactly what went
    wrong.

    Args:
        var_name: The name of the variable or argument
        value: The value that fell outside the expected range
        lower: The lower bound, inclusive, of the range
        upper: The upper bound, inclusive, of the range
    """

    def __init__(self, var_name: str, value: _CT, lower: _CT, upper: _CT) -> None:
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

    Args:
        var_name: The name of the variable or argument
        value: The value that fell outside the expected range
        lower: The lower bound, inclusive, of the range
        upper: The upper bound, inclusive, of the range
    """

    def __init__(self, var_name: str, value: int, lower: int, upper: int) -> None:
        super().__init__(var_name, value, lower, upper)


class FloatOutsideRangeError(OutsideRangeError):
    """
    A float value was outside an expected range

    Args:
        var_name: The name of the variable or argument
        value: The value that fell outside the expected range
        lower: The lower bound, inclusive, of the range
        upper: The upper bound, inclusive, of the range
    """

    def __init__(self, var_name: str, value: float, lower: float, upper: float) -> None:
        super().__init__(var_name, value, lower, upper)


class ByteRangeError(IntOutsideRangeError):
    """
    An int was outside the range of 0 to 255 inclusive

    Args:
        var_name: the name of the variable or argument
        value: the value to fall outside the expected range
    """

    def __init__(self, var_name: str, value: int) -> None:
        super().__init__(var_name, value, 0, 255)


class NormalizedRangeError(FloatOutsideRangeError):
    """
    A float was not between 0.0 and 1.0, inclusive

    Note that normalized floats should not normally be bound-checked as
    before drawing as this is taken care of on the GPU side.

    The exceptions to this are when processing data on the Python side,
    especially when it is cheaper to bound check two floats than call
    clamping functions.

    Args:
        var_name: the name of the variable or argument
        value: the value to fall outside the expected range
    """

    def __init__(self, var_name: str, value: float) -> None:
        super().__init__(var_name, value, 0.0, 1.0)


class PerformanceWarning(Warning):
    """Issuing performance warnings on slow paths."""

    pass


class ReplacementWarning(Warning):
    """Issuing warnings about naming and functionality changes."""

    pass


def warning(warning_type: type[Warning], message: str = "", **kwargs):
    """Warning decorator"""

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
