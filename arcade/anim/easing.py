"""Core easing annotations and helper functions."""

from math import cos, pi, sin, sqrt, tau
from typing import Protocol, TypeVar

T = TypeVar("T")


# This needs to be a Protocol rather than an annotation
# due to our build configuration being set to pick up
# classes but not type annotations.
class EasingFunction(Protocol):
    """Any :py:func:`callable` object which maps linear completion to a curve.

    .. tip:: See :py:class:`Easing` for the most common easings.

             Pass them to :py:func:`.ease` via the ``func``
             keyword argument.

    If the built-in easing curves are not enough, you can define
    your own. Functions should match this pattern:

    .. code-block:: python

       def f(t: float) -> t:
           ...

    For advanced users, any object with a matching :py:meth:`~object.__call__`
    method can be passed as an easing function.
    """

    def __call__(self, __t: float) -> float: ...


class Interpolatable(Protocol):
    """Matches types with support for the following operations:

    .. list-table::
       :header-rows: 1

       * - Method
         - Summary

       * - :py:meth:`~object.__mul__`
         - Multiplication by a scalar

       * - :py:meth:`~object.__add__`
         - Addition

       * - :py:meth:`~object.__sub__`
         - Subtraction

    .. important:: The :py:mod:`pyglet.math` matrix types are currently unsupported.

                   Although vector types work, matrix multiplication is
                   subtly different. It uses a separate :py:meth:`~object.__matmul__`
                   operator for multiplication.
    """

    def __mul__(self: T, other: T | float, /) -> T: ...

    def __add__(self: T, other: T | float, /) -> T: ...

    def __sub__(self: T, other: T | float, /) -> T: ...


A = TypeVar("A", bound=Interpolatable)

# === BEGIN EASING FUNCTIONS ===

# CONSTANTS USED FOR EASING EQUATIONS
# *: The constants C2, C3, N1, and D1 don't have clean analogies,
# so remain unnamed.
TEN_PERCENT_BOUNCE = 1.70158
C2 = TEN_PERCENT_BOUNCE * 1.525
C3 = TEN_PERCENT_BOUNCE + 1
TAU_ON_THREE = tau / 3
TAU_ON_FOUR_AND_A_HALF = tau / 4.5
N1 = 7.5625
D1 = 2.75


class Easing:
    """Built-in easing functions as static methods.

    Each takes the following form:

    .. code-block:: python

       def f(t: float) -> float:
         ...

    Pass them into :py:func:`.ease` via the ``func`` keyword
    argument:

    .. code-block:: python

         from arcade.anim import ease, Easing

         value = ease(
           1.0, 2.0,
           2.0, 3.0,
           2.4,
           func=Easing.SINE_IN)

    """

    # This is a bucket of staticmethods because typing.
    # Enum hates this, and they can't be classmethods.
    # That's why their capitalized, it's meant to be an Enum-like
    # Sorry that this looks strange! -- DigiDuncan

    @staticmethod
    def LINEAR(t: float) -> float:
        """Essentially the 'null' case for easing. Does no easing."""
        return t

    @staticmethod
    def SINE_IN(t: float) -> float:
        """http://easings.net/#easeInSine"""
        return 1 - cos((t * pi / 2))

    @staticmethod
    def SINE_OUT(t: float) -> float:
        """http://easings.net/#easeOutSine"""
        return sin((t * pi) / 2)

    @staticmethod
    def SINE(t: float) -> float:
        """http://easings.net/#easeInOutSine"""
        return -(cos(t * pi) - 1) / 2

    @staticmethod
    def QUAD_IN(t: float) -> float:
        """http://easings.net/#easeInQuad"""
        return t * t

    @staticmethod
    def QUAD_OUT(t: float) -> float:
        """http://easings.net/#easeOutQuad"""
        return 1 - (1 - t) * (1 - t)

    @staticmethod
    def QUAD(t: float) -> float:
        """http://easings.net/#easeInOutQuad"""
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - pow(-2 * t + 2, 2) / 2

    @staticmethod
    def CUBIC_IN(t: float) -> float:
        """http://easings.net/#easeInCubic"""
        return t * t * t

    @staticmethod
    def CUBIC_OUT(t: float) -> float:
        """http://easings.net/#easeOutCubic"""
        return 1 - pow(1 - t, 3)

    @staticmethod
    def CUBIC(t: float) -> float:
        """http://easings.net/#easeInOutCubic"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2

    @staticmethod
    def QUART_IN(t: float) -> float:
        """http://easings.net/#easeInQuart"""
        return t * t * t * t

    @staticmethod
    def QUART_OUT(t: float) -> float:
        """http://easings.net/#easeOutQuart"""
        return 1 - pow(1 - t, 4)

    @staticmethod
    def QUART(t: float) -> float:
        """http://easings.net/#easeInOutQuart"""
        if t < 0.5:
            return 8 * t * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 4) / 2

    @staticmethod
    def QUINT_IN(t: float) -> float:
        """http://easings.net/#easeInQint"""
        return t * t * t * t * t

    @staticmethod
    def QUINT_OUT(t: float) -> float:
        """http://easings.net/#easeOutQint"""
        return 1 - pow(1 - t, 5)

    @staticmethod
    def QUINT(t: float) -> float:
        """http://easings.net/#easeInOutQint"""
        if t < 0.5:
            return 16 * t * t * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 5) / 2

    @staticmethod
    def EXPO_IN(t: float) -> float:
        """http://easings.net/#easeInExpo"""
        if t == 0:
            return 0
        return pow(2, 10 * t - 10)

    @staticmethod
    def EXPO_OUT(t: float) -> float:
        """http://easings.net/#easeOutExpo"""
        if t == 1:
            return 1
        return 1 - pow(2, -10 * t)

    @staticmethod
    def EXPO(t: float) -> float:
        """http://easings.net/#easeInOutExpo"""
        if t == 0 or t == 1:
            return t
        elif t < 0.5:
            return pow(2, 20 * t - 10) / 2
        else:
            return (2 - pow(2, -20 * t + 10)) / 2

    @staticmethod
    def CIRC_IN(t: float) -> float:
        """http://easings.net/#easeInCirc"""
        return 1 - sqrt(1 - pow(t, 2))

    @staticmethod
    def CIRC_OUT(t: float) -> float:
        """http://easings.net/#easeOutCirc"""
        return sqrt(1 - pow(t - 1, 2))

    @staticmethod
    def CIRC(t: float) -> float:
        """http://easings.net/#easeInOutCirc"""
        if t < 0.5:
            return (1 - sqrt(1 - pow(2 * t, 2))) / 2
        else:
            return (sqrt(1 - pow(-2 * t + 2, 2)) + 1) / 2

    @staticmethod
    def BACK_IN(t: float) -> float:
        """http://easings.net/#easeInBack"""
        return (C3 * t * t * t) - (TEN_PERCENT_BOUNCE * t * t)

    @staticmethod
    def BACK_OUT(t: float) -> float:
        """http://easings.net/#easeOutBack"""
        return 1 + C3 * pow(t - 1, 3) + TEN_PERCENT_BOUNCE * pow(t - 1, 2)

    @staticmethod
    def BACK(t: float) -> float:
        """http://easings.net/#easeInOutBack"""
        if t < 0.5:
            return (pow(2 * t, 2) * ((C2 + 1) * 2 * t - C2)) / 2
        else:
            return (pow(2 * t - 2, 2) * ((C2 + 1) * (t * 2 - 2) + C2) + 2) / 2

    @staticmethod
    def ELASTIC_IN(t: float) -> float:
        """http://easings.net/#easeInElastic"""
        if t == 0 or t == 1:
            return t
        return -pow(2, 10 * t - 10) * sin((t * 10 - 10.75) * TAU_ON_THREE)

    @staticmethod
    def ELASTIC_OUT(t: float) -> float:
        """http://easings.net/#easeOutElastic"""
        if t == 0 or t == 1:
            return t
        return pow(2, -10 * t) * sin((t * 10 - 0.75) * TAU_ON_THREE) + 1

    @staticmethod
    def ELASTIC(t: float) -> float:
        """http://easings.net/#easeInOutElastic"""
        if t == 0 or t == 1:
            return t
        if t < 0.5:
            return -(pow(2, 20 * t - 10) * sin((20 * t - 11.125) * TAU_ON_FOUR_AND_A_HALF)) / 2
        else:
            return (pow(2, -20 * t + 10) * sin((20 * t - 11.125) * TAU_ON_FOUR_AND_A_HALF)) / 2 + 1

    @staticmethod
    def BOUNCE_IN(t: float) -> float:
        """http://easings.net/#easeInBounce"""
        return 1 - (Easing.BOUNCE_OUT(1 - t))

    @staticmethod
    def BOUNCE_OUT(t: float) -> float:
        """http://easings.net/#easeOutBounce"""
        if t < 1 / D1:
            return N1 * t * t
        elif t < 2 / D1:
            return N1 * (t - 1.5 / D1) ** 2 + 0.75
        elif t < 2.5 / D1:
            return N1 * (t - 2.25 / D1) ** 2 + 0.9375
        else:
            return N1 * (t - 2.625 / D1) ** 2 + 0.984375

    @staticmethod
    def BOUNCE(t: float) -> float:
        """http://easings.net/#easeInOutBounce"""
        if t < 0.5:
            return (1 - Easing.BOUNCE_OUT(1 - 2 * t)) / 2
        else:
            return (1 + Easing.BOUNCE_OUT(2 * t - 1)) / 2

    # Aliases to match easing.net names
    SINE_IN_OUT = SINE
    QUAD_IN_OUT = QUAD
    CUBIC_IN_OUT = CUBIC
    QUART_IN_OUT = QUART
    QUINT_IN_OUT = QUINT
    EXPO_IN_OUT = EXPO
    CIRC_IN_OUT = CIRC
    BACK_IN_OUT = BACK
    ELASTIC_IN_OUT = ELASTIC
    BOUNCE_IN_OUT = BOUNCE


# === END EASING FUNCTIONS ===


def _clamp(x: float, low: float, high: float) -> float:
    return high if x > high else max(x, low)


def norm(x: float, start: float, end: float) -> float:
    """Convert ``x`` to a progress ratio from ``start`` to ``end``.

    The result will be a value normalized to between ``0.0``
    and ``1.0`` if ``x`` is between ``start`` and ``end`. It
    is not clamped, so the result may be less than ``0.0`` or
    ``greater than ``1.0``.

    Arguments:
        x: A value between ``start`` and ``end``.
        start: The start of the range.
        end: The end of the range.

    Returns:
        A range completion progress as a :py:class:`float`.
    """
    return (x - start) / (end - start)


def lerp(progress: float, minimum: A, maximum: A) -> A:
    """Get ``progress`` of the way from``minimum`` to ``maximum``.

    Arguments:
        progress: How far from ``minimum`` to ``maximum`` to go
            from ``0.0`` to ``1.0``.
        minimum: The start value along the path.
        maximum: The maximum value along the path.

    Returns:
        A value ``progress`` of the way from ``minimum`` to ``maximum``.
    """
    return minimum + ((maximum - minimum) * progress)


def ease(
    minimum: A,
    maximum: A,
    start: float,
    end: float,
    t: float,
    func: EasingFunction = Easing.LINEAR,
    clamped: bool = True,
) -> A:
    """Ease a value according to a curve function passed as ``func``.

    Override the default easing curve by passing any :py:class:`.Easing`
    or :py:class:`.EasingFunction` of your choice.

    The ``maximum`` and ``minimum`` must be of compatible types.
    For example, these can include:

    .. list-table::
       :header-rows: 1

       * - Type
         - Value Example
         - Explanation

       * - :py:class:`float`
         - ``0.5``
         - Numbers such as volume or brightness.

       * - :py:class:`~pyglet.math.Vec2`
         - ``Vec2(500.0, 200.0)``
         - A :py:mod:`pyglet.math` vector representing position.

    Arguments:
        minimum: any math-like object (a position, scale, value...); the "start position."
        maximum: any math-like object (a position, scale, value...); the "end position."
        start: a :py:class:`float` defining where progression begins, the "start time."
        end: a :py:class:`float` defining where progression ends, the "end time."
        t: a :py:class:`float` defining the current progression, the "current time."
        func: Defaults to :py:attr:`Easing.LINEAR`, but you can pass an
            :py:class:`Easing` or :py:class:`.EasingFunction` of your choice.
        clamped: Whether the value will be clamped to ``minimum`` and ``maximum``.

    Returns:
        An eased value for the given time ``t``.

    """
    p = norm(t, start, end)
    if clamped:
        p = _clamp(p, 0.0, 1.0)
    new_p = func(p)
    return lerp(new_p, minimum, maximum)


__all__ = ["Interpolatable", "Easing", "EasingFunction", "ease", "norm", "lerp"]
