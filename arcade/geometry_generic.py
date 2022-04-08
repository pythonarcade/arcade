import math
from typing import List


def get_distance(x1: float, y1: float, x2: float, y2: float):
    """ Get the distance between two points. """
    return math.hypot(x1 - x2, y1 - y2)


def clamp(a, low, high):
    """ Clamp a number between a range. """
    if a > high:
        return high
    elif a < low:
        return low
    else:
        return a


def rotate_point(x: float, y: float, cx: float, cy: float,
                 angle_degrees: float) -> List[float]:
    """
    Rotate a point around a center.

    :param x: x value of the point you want to rotate
    :param y: y value of the point you want to rotate
    :param cx: x value of the center point you want to rotate around
    :param cy: y value of the center point you want to rotate around
    :param angle_degrees: Angle, in degrees, to rotate
    :return: Return rotated (x, y) pair
    :rtype: (float, float)
    """
    temp_x = x - cx
    temp_y = y - cy

    # now apply rotation
    angle_radians = math.radians(angle_degrees)
    cos_angle = math.cos(angle_radians)
    sin_angle = math.sin(angle_radians)
    rotated_x = temp_x * cos_angle - temp_y * sin_angle
    rotated_y = temp_x * sin_angle + temp_y * cos_angle

    # translate back
    rounding_precision = 2
    x = round(rotated_x + cx, rounding_precision)
    y = round(rotated_y + cy, rounding_precision)

    return [x, y]


def get_angle_degrees(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Get the angle in degrees between two points.

    :param float x1: x coordinate of the first point
    :param float y1: y coordinate of the first point
    :param float x2: x coordinate of the second point
    :param float y2: y coordinate of the second point
    """

    x_diff = x2 - x1
    y_diff = y2 - y1
    angle = math.degrees(math.atan2(x_diff, y_diff))
    return angle


def get_angle_radians(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Get the angle in radians between two points.

    :param float x1: x coordinate of the first point
    :param float y1: y coordinate of the first point
    :param float x2: x coordinate of the second point
    :param float y2: y coordinate of the second point
    """

    x_diff = x2 - x1
    y_diff = y2 - y1
    angle = math.atan2(x_diff, y_diff)
    return angle
