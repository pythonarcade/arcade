"""
Functions used to support easing
"""

from dataclasses import dataclass
from math import cos, pi, sin
from typing import Callable

from .math import get_distance


@dataclass
class EasingData:
    """
    Data class for holding information about easing.
    """

    start_period: float
    cur_period: float
    end_period: float
    start_value: float
    end_value: float
    ease_function: Callable

    def reset(self) -> None:
        """
        Reset the easing data to its initial state.
        """
        self.cur_period = self.start_period


def linear(percent: float) -> float:
    """
    Function for linear easing.
    """
    return percent


def _flip(percent: float) -> float:
    return 1.0 - percent


def smoothstep(percent: float) -> float:
    """
    Function for smoothstep easing.
    """
    return percent**2 * (3.0 - 2.0 * percent)


def ease_in(percent: float) -> float:
    """
    Function for quadratic ease-in easing.
    """
    return percent**2


def ease_out(percent: float) -> float:
    """
    Function for quadratic ease-out easing.
    """
    return _flip(_flip(percent) * _flip(percent))


def ease_in_out(percent: float) -> float:
    """
    Function for quadratic easing in and out.
    """

    return 2 * percent**2 if percent < 0.5 else 1 - (-2 * percent + 2) ** 2 / 2


def ease_out_elastic(percent: float) -> float:
    """
    Function for elastic ease-out easing.
    """
    c4 = 2 * pi / 3
    result = 0.0
    if percent == 1:
        result = 1
    elif percent > 0:
        result = (2 ** (-10 * percent)) * sin((percent * 10 - 0.75) * c4) + 1
    return result


def ease_out_bounce(percent: float) -> float:
    """
    Function for a bouncy ease-out easing.
    """
    n1 = 7.5625
    d1 = 2.75

    if percent < 1 / d1:
        return n1 * percent * percent
    elif percent < 2 / d1:
        percent_modified = percent - 1.5 / d1
        return n1 * percent_modified * percent_modified + 0.75
    elif percent < 2.5 / d1:
        percent_modified = percent - 2.25 / d1
        return n1 * percent_modified * percent_modified + 0.9375
    else:
        percent_modified = percent - 2.625 / d1
        return n1 * percent_modified * percent_modified + 0.984375


def ease_in_back(percent: float) -> float:
    """
    Function for ease_in easing which moves back before moving forward.
    """
    c1 = 1.70158
    c3 = c1 + 1

    return c3 * percent * percent * percent - c1 * percent * percent


def ease_out_back(percent: float) -> float:
    """
    Function for ease_out easing which moves back before moving forward.
    """
    c1 = 1.70158
    c3 = c1 + 1

    return 1 + c3 * pow(percent - 1, 3) + c1 * pow(percent - 1, 2)


def ease_in_sin(percent: float) -> float:
    """
    Function for ease_in easing using a sin wave
    """
    return 1 - cos((percent * pi) / 2)


def ease_out_sin(percent: float) -> float:
    """
    Function for ease_out easing using a sin wave
    """
    return sin((percent * pi) / 2)


def ease_in_out_sin(percent: float) -> float:
    """
    Function for easing in and out using a sin wave
    """
    return -cos(percent * pi) * 0.5 + 0.5


def easing(percent: float, easing_data: EasingData) -> float:
    """
    Function for calculating return value for easing, given percent and easing data.
    """
    return easing_data.start_value + (
        easing_data.end_value - easing_data.start_value
    ) * easing_data.ease_function(percent)


def ease_angle(
    start_angle: float,
    end_angle: float,
    *,
    time=None,
    rate=None,
    ease_function: Callable = linear,
) -> EasingData | None:
    """
    Set up easing for angles.
    """
    while start_angle - end_angle > 180:
        end_angle += 360

    while start_angle - end_angle < -180:
        end_angle -= 360

    diff = abs(start_angle - end_angle)
    if diff == 0:
        return None

    if rate is not None:
        time = diff / rate

    if time is None:
        raise ValueError("Either the 'time' or the 'rate' parameter needs to be set.")

    easing_data = EasingData(
        start_value=start_angle,
        end_value=end_angle,
        start_period=0,
        cur_period=0,
        end_period=time,
        ease_function=ease_function,
    )
    return easing_data


def ease_angle_update(easing_data: EasingData, delta_time: float) -> tuple[bool, float]:
    """
    Update angle easing.
    """
    done = False
    easing_data.cur_period += delta_time
    easing_data.cur_period = min(easing_data.cur_period, easing_data.end_period)
    percent = easing_data.cur_period / easing_data.end_period

    angle = easing(percent, easing_data)

    if percent >= 1.0:
        done = True

        while angle > 360:
            angle -= 360

        while angle < 0:
            angle += 360

    return done, angle


def ease_value(
    start_value: float, end_value: float, *, time=None, rate=None, ease_function=linear
) -> EasingData:
    """
    Get an easing value
    """
    if rate is not None:
        diff = abs(start_value - end_value)
        time = diff / rate

    if time is None:
        raise ValueError("Either the 'time' or the 'rate' parameter needs to be set.")

    easing_data = EasingData(
        start_value=start_value,
        end_value=end_value,
        start_period=0,
        cur_period=0,
        end_period=time,
        ease_function=ease_function,
    )
    return easing_data


def ease_position(
    start_position, end_position, *, time=None, rate=None, ease_function=linear
) -> tuple[EasingData, EasingData]:
    """
    Get an easing position
    """
    distance = get_distance(start_position[0], start_position[1], end_position[0], end_position[1])

    if rate is not None:
        time = distance / rate

    easing_data_x = ease_value(
        start_position[0], end_position[0], time=time, ease_function=ease_function
    )
    easing_data_y = ease_value(
        start_position[1], end_position[1], time=time, ease_function=ease_function
    )

    return easing_data_x, easing_data_y


def ease_update(easing_data: EasingData, delta_time: float) -> tuple[bool, float]:
    """
    Update easing between two values/
    """
    easing_data.cur_period += delta_time
    easing_data.cur_period = min(easing_data.cur_period, easing_data.end_period)
    if easing_data.end_period == 0:
        percent = 1.0
        value = easing_data.end_value
    else:
        percent = easing_data.cur_period / easing_data.end_period
        value = easing(percent, easing_data)

    done = percent >= 1.0
    return done, value
