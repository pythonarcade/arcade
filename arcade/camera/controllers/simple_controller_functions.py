from typing import Tuple, Callable, Optional
from math import sin, cos, radians

from arcade.camera.data import CameraData
from arcade.easing import linear
from pyglet.math import Vec3

__all__ = [
    'simple_follow_3D',
    'simple_follow_2D',
    'simple_easing_3D',
    'simple_easing_2D',
    'strafe',
    'quaternion_rotation',
    'rotate_around_forward',
    'rotate_around_up',
    'rotate_around_right'
]


def strafe(data: CameraData, direction: Tuple[float, float]):
    """
    Move the CameraData in a 2D direction aligned to the up-right plane of the view.
    A value of [1, 0] will move the camera sideways while a value of [0, 1]
    will move the camera upwards. Works irrespective of which direction the camera is facing.
    Ensure the up and forward vectors are unit-length or the size of the motion will be incorrect.
    """
    _forward = Vec3(*data.forward)
    _up = Vec3(*data.up)
    _right = _forward.cross(_up)

    _pos = data.position

    offset = _right * direction[0] + _up * direction[1]
    data.position = (
        _pos[0] + offset[0],
        _pos[1] + offset[1],
        _pos[2] + offset[2]
    )


def quaternion_rotation(axis: Tuple[float, float, float],
                        vector: Tuple[float, float, float],
                        angle: float) -> Tuple[float, float, float]:
    """
    Rotate a 3-dimensional vector of any length clockwise around a 3-dimensional unit length vector.

    This method of vector rotation is immune to rotation-lock, however it takes a little more effort
    to find the axis of rotation rather than 3 angles of rotation.
    Ref: https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html.

    Example:
        import arcade
        from arcade.camera.controllers import quaternion_rotation


        # Rotating a sprite around a point
        sprite = arcade.Sprite(center_x=0.0, center_y=10.0)
        rotation_point = (0.0, 0.0)

        # Find the relative vector between the sprite and point to rotate. (Must be a 3D vector)
        relative_position = sprite.center_x - rotation_point[0], sprite.center_y - rotation_point[1], 0.0

        # Because arcade uses the X and Y axis for 2D co-ordinates the Z-axis becomes the rotation axis.
        rotation_axis = (0.0, 0.0, 1.0)

        # Rotate the vector 45 degrees clockwise.
        new_relative_position = quaternion_rotation(rotation_axis, relative_position, 45)


        sprite.position = (
            rotation_point[0] + new_relative_position[0],
            rotation_point[1] + new_relative_position[1]
        )

    Args:
        axis:
            The unit length vector that will be rotated around
        vector:
            The 3-dimensional vector to be rotated
        angle:
            The angle in degrees to rotate the vector clock-wise by

    Returns:
        A rotated 3-dimension vector with the same length as the argument vector.
    """

    _rotation_rads = -radians(angle)
    p1, p2, p3 = vector
    _c2, _s2 = cos(_rotation_rads / 2.0), sin(_rotation_rads / 2.0)

    q0, q1, q2, q3 = (
        _c2,
        _s2 * axis[0],
        _s2 * axis[1],
        _s2 * axis[2]
    )
    q0_2, q1_2, q2_2, q3_2 = q0 ** 2, q1 ** 2, q2 ** 2, q3 ** 2
    q01, q02, q03, q12, q13, q23 = q0 * q1, q0 * q2, q0 * q3, q1 * q2, q1 * q3, q2 * q3

    _x = p1 * (q0_2 + q1_2 - q2_2 - q3_2) + 2.0 * (p2 * (q12 - q03) + p3 * (q02 + q13))
    _y = p2 * (q0_2 - q1_2 + q2_2 - q3_2) + 2.0 * (p1 * (q03 + q12) + p3 * (q23 - q01))
    _z = p3 * (q0_2 - q1_2 - q2_2 + q3_2) + 2.0 * (p1 * (q13 - q02) + p2 * (q01 + q23))

    return _x, _y, _z


def rotate_around_forward(data: CameraData, angle: float):
    """
    Rotate the CameraData up vector around the CameraData forward vector, perfect for rotating the screen.
    This rotation will be around (0.0, 0.0) of the camera projection.
    If that is not the center of the screen this method may appear erroneous.
    Uses arcade.camera.controllers.quaternion_rotation internally.

    Args:
        data:
            The camera data to modify. The data's up vector is rotated around its forward vector
        angle:
            The angle in degrees to rotate clockwise by
    """
    data.up = quaternion_rotation(data.forward, data.up, angle)


def rotate_around_up(data: CameraData, angle: float):
    """
    Rotate the CameraData forward vector around the CameraData up vector.
    Generally only useful in 3D games.
    Uses arcade.camera.controllers.quaternion_rotation internally.

    Args:
        data:
            The camera data to modify. The data's forward vector is rotated around its up vector
        angle:
            The angle in degrees to rotate clockwise by
    """
    data.forward = quaternion_rotation(data.up, data.forward, angle)


def rotate_around_right(data: CameraData, angle: float, forward: bool = True, up: bool = True):
    """
    Rotate both the CameraData's forward vector and up vector around a calculated right vector.
    Generally only useful in 3D games.
    Uses arcade.camera.controllers.quaternion_rotation internally.

    Args:
        data:
            The camera data to modify. The data's forward vector is rotated around its up vector
        angle:
            The angle in degrees to rotate clockwise by
        forward:
            Whether to rotate the forward vector around the right vector
        up:
            Whether to rotate the up vector around the right vector
    """

    _forward = Vec3(data.forward[0], data.forward[1], data.forward[2])
    _up = Vec3(data.up[0], data.up[1], data.up[2])
    _crossed_vec = _forward.cross(_up)
    _right: Tuple[float, float, float] = (_crossed_vec.x, _crossed_vec.y, _crossed_vec.z)
    if forward:
        data.forward = quaternion_rotation(_right, data.forward, angle)
    if up:
        data.up = quaternion_rotation(_right, data.up, angle)


def _interpolate_3D(s: Tuple[float, float, float], e: Tuple[float, float, float], t: float):
    s_x, s_y, s_z = s
    e_x, e_y, e_z = e

    return s_x + t * (e_x - s_x), s_y + t * (e_y - s_y), s_z + t * (e_z - s_z)


# A set of four methods for moving a camera smoothly in a straight line in various different ways.

def simple_follow_3D(speed: float, target: Tuple[float, float, float], data: CameraData):
    """
    A simple method which moves the camera linearly towards the target point.

    Args:
        speed: The percentage the camera should move towards the target (0.0 - 1.0 range)
        target: The 3D position the camera should move towards in world space.
        data: The camera data object which stores its position, rotation, and direction.
    """

    data.position = _interpolate_3D(data.position, target, speed)


def simple_follow_2D(speed: float, target: Tuple[float, float], data: CameraData):
    """
    A 2D version of simple_follow. Moves the camera only along the X and Y axis.

    Args:
        speed: The percentage the camera should move towards the target (0.0 - 1.0 range)
        target: The 2D position the camera should move towards in world space. (vector in XY-plane)
        data: The camera data object which stores its position, rotation, and direction.
    """
    simple_follow_3D(speed, (target[0], target[1], 0.0), data)


def simple_easing_3D(percent: float,
                  start: Tuple[float, float, float],
                  target: Tuple[float, float, float],
                  data: CameraData, func: Callable[[float], float] = linear):
    """
    A simple method which moves a camera in a straight line between two 3D points.
    It uses an easing function to make the motion smoother. You can use the collection of
    easing methods found in arcade.easing.

    Args:
        percent: The percentage from 0 to 1 which describes
                 how far between the two points to place the camera.
        start: The 3D point which acts as the starting point for the camera motion.
        target: The 3D point which acts as the final destination for the camera.
        data: The camera data object which stores its position, rotation, and direction.
        func: The easing method to use. It takes in a number between 0-1
              and returns a new number in the same range but altered so the
              speed does not stay constant. See arcade.easing for examples.
    """

    data.position = _interpolate_3D(start, target, func(percent))


def simple_easing_2D(percent: float,
                     start: Tuple[float, float],
                     target: Tuple[float, float],
                     data: CameraData, func: Callable[[float], float] = linear):
    """
    A simple method which moves a camera in a straight line between two 2D points (along XY plane).
    It uses an easing function to make the motion smoother. You can use the collection of
    easing methods found in arcade.easing.

    Args:
        percent: The percentage from 0 to 1 which describes
                 how far between the two points to place the camera.
        start: The 2D point which acts as the starting point for the camera motion.
        target: The 2D point which acts as the final destination for the camera.
        data: The camera data object which stores its position, rotation, and direction.
        func: The easing method to use. It takes in a number between 0-1
              and returns a new number in the same range but altered so the
              speed does not stay constant. See arcade.easing for examples.
    """

    simple_easing_3D(percent, (start[0], start[1], 0.0), (target[0], target[1], 0.0), data, func)
