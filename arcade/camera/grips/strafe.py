from pyglet.math import Vec3

from arcade.camera.data_types import CameraData


def strafe(data: CameraData, direction: tuple[float, float]) -> tuple[float, float, float]:
    """
    Move the CameraData in a 2D direction aligned to the up-right plane of the view.
    A value of [1, 0] will move the camera sideways while a value of [0, 1]
    will move the camera upwards. Works irrespective of which direction the camera is facing.
    """
    _forward = Vec3(*data.forward).normalize()
    _up = Vec3(*data.up).normalize()
    _right = _forward.cross(_up)

    _pos = data.position

    offset = _right * direction[0] + _up * direction[1]
    # fmt: off
    return (
            _pos[0] + offset[0],
            _pos[1] + offset[1],
            _pos[2] + offset[2]
        )
    # fmt: on
