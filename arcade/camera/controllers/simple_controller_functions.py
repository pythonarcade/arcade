from typing import Tuple, Callable

from arcade.camera.data import CameraData
from arcade.easing import linear


__all__ = [
    'simple_follow',
    'simple_follow_2D',
    'simple_easing',
    'simple_easing_2D'
]


def _interpolate_3D(s: Tuple[float, float, float], e: Tuple[float, float, float], t: float):
    s_x, s_y, s_z = s
    e_x, e_y, e_z = e

    return s_x + t * (e_x - s_x), s_y + t * (e_y - s_y), s_z + t * (e_z - s_z)


# A set of four methods for moving a camera smoothly in a straight line in various different ways.

def simple_follow(speed: float, target: Tuple[float, float, float], data: CameraData):
    """
    A simple method which moves the camera linearly towards the target point.

    :param speed: The percentage the camera should move towards the target.
    :param target: The 3D position the camera should move towards in world space.
    :param data: The camera data object which stores its position, rotation, and direction.
    """

    data.position = _interpolate_3D(data.position, target, speed)


def simple_follow_2D(speed: float, target: Tuple[float, float], data: CameraData):
    """
    A 2D version of simple_follow. Moves the camera only along the X and Y axis.

    :param speed: The percentage the camera should move towards the target.
    :param target: The 2D position the camera should move towards in world space.
    :param data: The camera data object which stores its position, rotation, and direction.
    """
    simple_follow(speed, target + (0,), data)


def simple_easing(percent: float,
                  start: Tuple[float, float, float],
                  target: Tuple[float, float, float],
                  data: CameraData, func: Callable[[float], float] = linear):
    """
    A simple method which moves a camera in a straight line between two provided points.
    It uses an easing function to make the motion smoother. You can use the collection of
    easing methods found in arcade.easing.

    :param percent: The percentage from 0 to 1 which describes
                    how far between the two points to place the camera.
    :param start: The 3D point which acts as the starting point for the camera motion.
    :param target: The 3D point which acts as the final destination for the camera.
    :param data: The camera data object which stores its position, rotation, and direction.
    :param func: The easing method to use. It takes in a number between 0-1
                 and returns a new number in the same range but altered so the
                 speed does not stay constant. See arcade.easing for examples.
    """

    data.position = _interpolate_3D(start, target, func(percent))


def simple_easing_2D(percent: float,
                     start: Tuple[float, float],
                     target: Tuple[float, float],
                     data: CameraData, func: Callable[[float], float] = linear):
    """
    A 2D version of simple_easing. Moves the camera only along the X and Y axis.

    :param percent: The percentage from 0 to 1 which describes
                    how far between the two points to place the camera.
    :param start: The 3D point which acts as the starting point for the camera motion.
    :param target: The 3D point which acts as the final destination for the camera.
    :param data: The camera data object which stores its position, rotation, and direction.
    :param func: The easing method to use. It takes in a number between 0-1
                 and returns a new number in the same range but altered so the
                 speed does not stay constant. See arcade.easing for examples.
    """

    simple_easing(percent, start + (0,), target + (0,), data, func)

