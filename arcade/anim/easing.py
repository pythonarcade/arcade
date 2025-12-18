from collections.abc import Callable
from math import cos, pi, sin, sqrt, tau
from typing import Protocol, TypeVar

T = TypeVar("T")


class Animatable(Protocol):
    def __mul__(self: T, other: T | float, /) -> T: ...

    def __add__(self: T, other: T | float, /) -> T: ...

    def __sub__(self: T, other: T | float, /) -> T: ...


A = TypeVar("A", bound=Animatable)

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


def _ease_linear(t: float) -> float:
    return t


def _ease_in_sine(t: float) -> float:
    """http://easings.net/#easeInSine"""
    return 1 - cos((t * pi / 2))


def _ease_out_sine(t: float) -> float:
    """http://easings.net/#easeOutSine"""
    return sin((t * pi) / 2)


def _ease_sine(t: float) -> float:
    """http://easings.net/#easeInOutSine"""
    return -(cos(t * pi) - 1) / 2


def _ease_in_quad(t: float) -> float:
    """http://easings.net/#easeInQuad"""
    return t * t


def _ease_out_quad(t: float) -> float:
    """http://easings.net/#easeOutQuad"""
    return 1 - (1 - t) * (1 - t)


def _ease_quad(t: float) -> float:
    """http://easings.net/#easeInOutQuad"""
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - pow(-2 * t + 2, 2) / 2


def _ease_in_cubic(t: float) -> float:
    """http://easings.net/#easeInCubic"""
    return t * t * t


def _ease_out_cubic(t: float) -> float:
    """http://easings.net/#easeOutCubic"""
    return 1 - pow(1 - t, 3)


def _ease_cubic(t: float) -> float:
    """http://easings.net/#easeInOutCubic"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def _ease_in_quart(t: float) -> float:
    """http://easings.net/#easeInQuart"""
    return t * t * t * t


def _ease_out_quart(t: float) -> float:
    """http://easings.net/#easeOutQuart"""
    return 1 - pow(1 - t, 4)


def _ease_quart(t: float) -> float:
    """http://easings.net/#easeInOutQuart"""
    if t < 0.5:
        return 8 * t * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 4) / 2


def _ease_in_quint(t: float) -> float:
    """http://easings.net/#easeInQint"""
    return t * t * t * t * t


def _ease_out_quint(t: float) -> float:
    """http://easings.net/#easeOutQint"""
    return 1 - pow(1 - t, 5)


def _ease_quint(t: float) -> float:
    """http://easings.net/#easeInOutQint"""
    if t < 0.5:
        return 16 * t * t * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 5) / 2


def _ease_in_expo(t: float) -> float:
    """http://easings.net/#easeInExpo"""
    if t == 0:
        return 0
    return pow(2, 10 * t - 10)


def _ease_out_expo(t: float) -> float:
    """http://easings.net/#easeOutExpo"""
    if t == 1:
        return 1
    return 1 - pow(2, -10 * t)


def _ease_expo(t: float) -> float:
    """http://easings.net/#easeInOutExpo"""
    if t == 0 or t == 1:
        return t
    elif t < 0.5:
        return pow(2, 20 * t - 10) / 2
    else:
        return (2 - pow(2, -20 * t + 10)) / 2


def _ease_in_circ(t: float) -> float:
    """http://easings.net/#easeInCirc"""
    return 1 - sqrt(1 - pow(t, 2))


def _ease_out_circ(t: float) -> float:
    """http://easings.net/#easeOutCirc"""
    return sqrt(1 - pow(t - 1, 2))


def _ease_circ(t: float) -> float:
    """http://easings.net/#easeInOutCirc"""
    if t < 0.5:
        return (1 - sqrt(1 - pow(2 * t, 2))) / 2
    else:
        return (sqrt(1 - pow(-2 * t + 2, 2)) + 1) / 2


def _ease_in_back(t: float) -> float:
    """http://easings.net/#easeInBack"""
    return (C3 * t * t * t) - (TEN_PERCENT_BOUNCE * t * t)


def _ease_out_back(t: float) -> float:
    """http://easings.net/#easeOutBack"""
    return 1 + C3 + pow(t - 1, 3) + TEN_PERCENT_BOUNCE * pow(t - 1, 2)


def _ease_back(t: float) -> float:
    """http://easings.net/#easeInOutBack"""
    if t < 0.5:
        return (pow(2 * t, 2) * ((C2 + 1) * 2 * t - C2)) / 2
    else:
        return (pow(2 * t - 2, 2) * ((C2 + 1) * (t * 2 - 2) + C2) + 2) / 2


def _ease_in_elastic(t: float) -> float:
    """http://easings.net/#easeInElastic"""
    if t == 0 or t == 1:
        return t
    return -pow(2, 10 * t - 10) * sin((t * 10 - 10.75) * TAU_ON_THREE)


def _ease_out_elastic(t: float) -> float:
    """http://easings.net/#easeOutElastic"""
    if t == 0 or t == 1:
        return t
    return pow(2, -10 * t) * sin((t * 10 - 0.75) * TAU_ON_THREE) + 1


def _ease_elastic(t: float) -> float:
    """http://easings.net/#easeInOutElastic"""
    if t == 0 or t == 1:
        return t
    if t < 0.5:
        return -(pow(2, 20 * t - 10) * sin((20 * t - 11.125) * TAU_ON_FOUR_AND_A_HALF)) / 2
    else:
        return (pow(2, -20 * t + 10) * sin((20 * t - 11.125) * TAU_ON_FOUR_AND_A_HALF)) / 2 + 1


def _ease_in_bounce(t: float) -> float:
    """http://easings.net/#easeInBounce"""
    return 1 - (_ease_out_bounce(1 - t))


def _ease_out_bounce(t: float) -> float:
    """http://easings.net/#easeOutBounce"""
    if t < 1 / D1:
        return N1 * t * t
    elif t < 2 / D1:
        return N1 * ((t - 1.5) / D1) * (t - 1.5) + 0.75
    elif t < 2.5 / D1:
        return N1 * ((t - 2.25) / D1) * (t - 2.25) + 0.9375
    else:
        return N1 * ((t - 2.625) / D1) * (t - 2.625) + 0.984375


def _ease_bounce(t: float) -> float:
    """http://easings.net/#easeInOutBounce"""
    if t < 0.5:
        return (1 - _ease_out_bounce(1 - 2 * t)) / 2
    else:
        return (1 + _ease_out_bounce(2 * t - 1)) / 2


class Easing:
    """:py:class:`.EasingFunction`s meant for passing into :py:meth:`.ease`."""

    LINEAR = staticmethod(_ease_linear)
    SINE = staticmethod(_ease_sine)
    SINE_IN = staticmethod(_ease_in_sine)
    SINE_OUT = staticmethod(_ease_out_sine)
    QUAD = staticmethod(_ease_quad)
    QUAD_IN = staticmethod(_ease_in_quad)
    QUAD_OUT = staticmethod(_ease_out_quad)
    CUBIC = staticmethod(_ease_cubic)
    CUBIC_IN = staticmethod(_ease_in_cubic)
    CUBIC_OUT = staticmethod(_ease_out_cubic)
    QUART = staticmethod(_ease_quart)
    QUART_IN = staticmethod(_ease_in_quart)
    QUART_OUT = staticmethod(_ease_out_quart)
    QUINT = staticmethod(_ease_quint)
    QUINT_IN = staticmethod(_ease_in_quint)
    QUINT_OUT = staticmethod(_ease_out_quint)
    EXPO = staticmethod(_ease_expo)
    EXPO_IN = staticmethod(_ease_in_expo)
    EXPO_OUT = staticmethod(_ease_out_expo)
    CIRC = staticmethod(_ease_circ)
    CIRC_IN = staticmethod(_ease_in_circ)
    CIRC_OUT = staticmethod(_ease_out_circ)
    BACK = staticmethod(_ease_back)
    BACK_IN = staticmethod(_ease_in_back)
    BACK_OUT = staticmethod(_ease_out_back)
    ELASTIC = staticmethod(_ease_elastic)
    ELASTIC_IN = staticmethod(_ease_in_elastic)
    ELASTIC_OUT = staticmethod(_ease_out_elastic)
    BOUNCE = staticmethod(_ease_bounce)
    BOUNCE_IN = staticmethod(_ease_in_bounce)
    BOUNCE_OUT = staticmethod(_ease_out_bounce)
    # Aliases to match easing.net names
    SINE_IN_OUT = staticmethod(_ease_sine)
    QUAD_IN_OUT = staticmethod(_ease_quad)
    CUBIC_IN_OUT = staticmethod(_ease_cubic)
    QUART_IN_OUT = staticmethod(_ease_quart)
    QUINT_IN_OUT = staticmethod(_ease_quint)
    EXPO_IN_OUT = staticmethod(_ease_expo)
    CIRC_IN_OUT = staticmethod(_ease_circ)
    BACK_IN_OUT = staticmethod(_ease_back)
    ELASTIC_IN_OUT = staticmethod(_ease_elastic)
    BOUNCE_IN_OUT = staticmethod(_ease_bounce)


# === END EASING FUNCTIONS ===


def _clamp(x: float, low: float, high: float) -> float:
    return high if x > high else max(x, low)


def perc(x: float, start: float, end: float) -> float:
    """
    Convert a value ``x`` to be a percentage of progression between
    ``start`` and ``end``.
    """
    return (x - start) / (end - start)


def lerp(x: float, minimum: A, maximum: A) -> A:
    """
    Convert a percentage ``x`` to be the value when progressed
    that amount between ``minimum`` and ``maximum``.
    """
    return minimum + ((maximum - minimum) * x)


EasingFunction = Callable[[float], float]


def ease(
    minimum: A,
    maximum: A,
    start: float,
    end: float,
    t: float,
    func: EasingFunction = Easing.LINEAR,
    clamped: bool = True,
) -> A:
    """Ease a value according to a curve. Useful for animating properties over time.

    Args:
        minimum: any math-like object (a position, scale, value...); the "start position."
        maximum: any math-like object (a position, scale, value...); the "end position."
        start: a :py:class:`float` defining where progression begins, the "start time."
        end: a :py:class:`float` defining where progression ends, the "end time."
        t: a :py:class:`float` defining the current progression, the "current time."
        func: a :py:class:`.EasingFunction` to modify the result with, typically an
        attribute of :py:class:`.Easing`. Defaults to :py:attr:`.Easing.LINEAR`.
        clamped: a :py:class:`bool`; whether or not to allow the animation to continue past
        the ``start`` and ``end`` "times". Defaults to ``True``.
    """
    p = perc(t, start, end)
    if clamped:
        p = _clamp(p, 0.0, 1.0)
    new_p = func(p)
    return lerp(new_p, minimum, maximum)
