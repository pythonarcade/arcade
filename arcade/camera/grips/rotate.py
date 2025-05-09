from pyglet.math import Vec3

from arcade.camera.data_types import CameraData
from arcade.math import quaternion_rotation

__all__ = ("rotate_around_forward", "rotate_around_up", "rotate_around_right")


def rotate_around_forward(data: CameraData, angle: float) -> tuple[float, float, float]:
    """
    Rotate the CameraData up vector around the CameraData forward vector, perfect
    for rotating the screen.

    This rotation will be around (0.0, 0.0) of the camera projection.
    If that is not the center of the screen this method may appear erroneous.
    Uses arcade.camera.controllers.quaternion_rotation internally.

    Args:
        data:
            The camera data to modify. The data's up vector is rotated around
            its forward vector
        angle:
            The angle in degrees to rotate clockwise by
    """
    return quaternion_rotation(data.forward, data.up, angle)


def rotate_around_up(data: CameraData, angle: float) -> tuple[float, float, float]:
    """
    Rotate the CameraData forward vector around the CameraData up vector.
    Generally only useful in 3D games.
    Uses arcade.camera.controllers.quaternion_rotation internally.

    Args:
        data:
            The camera data to modify. The data's forward vector is rotated
            around its up vector
        angle:
            The angle in degrees to rotate clockwise by
    """
    return quaternion_rotation(data.up, data.forward, angle)


def rotate_around_right(
    data: CameraData, angle: float
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """
    Rotate both the CameraData's forward vector and up vector around a calculated
    right vector. Generally only useful in 3D games.
    Uses arcade.camera.controllers.quaternion_rotation internally.

    Args:
        data:
            The camera data to modify. The data's forward vector is rotated
            around its up vector
        angle:
            The angle in degrees to rotate clockwise by
    """
    _forward = Vec3(data.forward[0], data.forward[1], data.forward[2])
    _up = Vec3(data.up[0], data.up[1], data.up[2])
    _crossed_vec = _forward.cross(_up)
    _right: tuple[float, float, float] = (_crossed_vec.x, _crossed_vec.y, _crossed_vec.z)
    new_forward = quaternion_rotation(_right, data.forward, angle)
    new_up = quaternion_rotation(_right, data.up, angle)
    return new_up, new_forward
