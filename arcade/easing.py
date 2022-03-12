"""
Functions used to support easing
"""
from dataclasses import dataclass
from typing import Callable
from typing import Tuple
from .geometry_generic import get_distance


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


def linear(percent: float) -> float:
    """
    Function for linear easing.
    """
    return percent


def _flip(percent: float) -> float:
    return 1.0 - percent


def ease_in(percent: float) -> float:
    """
    Function for ease-in easing.
    """
    return percent * percent


def ease_out(percent: float) -> float:
    """
    Function for ease-out easing.
    """
    return _flip(_flip(percent) * _flip(percent))


def smoothstep(percent: float) -> float:
    """
    Function for smoothstep easing.
    """
    percent = percent * percent * (3.0 - 2.0 * percent)
    return percent


def easing(percent: float, easing_data: EasingData) -> float:
    """
    Function for calculating return value for easing, given percent and easing data.
    """
    return easing_data.start_value + (easing_data.end_value - easing_data.start_value) * \
        easing_data.ease_function(percent)


def ease_angle(start_angle, end_angle, *, time=None, rate=None, ease_function=linear):
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

    easing_data = EasingData(start_value=start_angle,
                             end_value=end_angle,
                             start_period=0,
                             cur_period=0,
                             end_period=time,
                             ease_function=ease_function)
    return easing_data


def ease_angle_update(easing_data: EasingData, delta_time: float) -> Tuple:
    """
    Update angle easing.
    """
    done = False
    easing_data.cur_period += delta_time
    if easing_data.cur_period >= easing_data.end_period:
        easing_data.cur_period = easing_data.end_period

    percent = easing_data.cur_period / easing_data.end_period

    angle = easing(percent, easing_data)

    if percent >= 1.0:
        done = True

        while angle > 360:
            angle -= 360

        while angle < 0:
            angle += 360

    return done, angle


def ease_value(start_value, end_value, *, time=None, rate=None, ease_function=linear):
    """
    Get an easing value
    """
    if rate is not None:
        diff = abs(start_value - end_value)
        time = diff / rate

    easing_data = EasingData(start_value=start_value,
                             end_value=end_value,
                             start_period=0,
                             cur_period=0,
                             end_period=time,
                             ease_function=ease_function)
    return easing_data


def ease_position(start_position, end_position, *, time=None, rate=None, ease_function=linear):
    """
    Get an easing position
    """
    distance = get_distance(start_position[0],
                            start_position[1],
                            end_position[0],
                            end_position[1])

    if rate is not None:
        time = distance / rate

    easing_data_x = ease_value(start_position[0], end_position[0], time=time, ease_function=ease_function)
    easing_data_y = ease_value(start_position[1], end_position[1], time=time, ease_function=ease_function)

    return easing_data_x, easing_data_y


def ease_update(easing_data: EasingData, delta_time: float) -> Tuple:
    """
    Update easing between two values/
    """
    done = False
    easing_data.cur_period += delta_time
    if easing_data.cur_period >= easing_data.end_period:
        easing_data.cur_period = easing_data.end_period

    if easing_data.end_period == 0:
        percent = 1.0
        value = easing_data.end_value
    else:
        percent = easing_data.cur_period / easing_data.end_period
        value = easing(percent, easing_data)

    if percent >= 1.0:
        done = True

    return done, value
