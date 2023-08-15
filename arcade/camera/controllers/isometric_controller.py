from typing import Tuple
from math import sin, cos, radians

from arcade.camera.data import CameraData
from arcade.camera.controllers.simple_controller_functions import quaternion_rotation


class IsometricCameraController:

    def __init__(self, camera_data: CameraData,
                 target: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 angle: float = 0.0,
                 dist: float = 1.0,
                 pixel_angle: bool = True,
                 up: Tuple[float, float, float] = (0.0, 0.0, 1.0),
                 right: Tuple[float, float, float] = (1.0, 0.0, 0.0)):
        self._data: CameraData = camera_data
        self._target: Tuple[float, float, float] = target
        self._angle: float = angle
        self._dist: float = dist

        self._pixel_angle: bool = pixel_angle

        self._up: Tuple[float, float, float] = up
        self._right: Tuple[float, float, float] = right

    def update_position(self):
        # Ref: https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        _pos_rads = radians(26.565 if self._pixel_angle else 30.0)
        _c, _s = cos(_pos_rads), sin(_pos_rads)
        p = (
            (_c * self._right[0] + _s * self._up[0]),
            (_c * self._right[1] + _s * self._up[1]),
            (_c * self._right[2] + _s * self._up[2])
        )

        _x, _y, _z = quaternion_rotation(self._up, p, self._angle + 45)
        self._data.up = self._up
        self._data.forward = -_x, -_y, -_z
        self._data.position = (
            self._target[0] + self._dist*_x,
            self._target[1] + self._dist*_y,
            self._target[2] + self._dist*_z
        )

    def toggle_pixel_angle(self):
        self._pixel_angle = bool(1 - self._pixel_angle)

    @property
    def pixel_angle(self) -> bool:
        return self._pixel_angle

    @pixel_angle.setter
    def pixel_angle(self, _px: bool) -> None:
        self._pixel_angle = _px

    @property
    def zoom(self) -> float:
        return self._data.zoom

    @zoom.setter
    def zoom(self, _zoom: float) -> None:
        self._data.zoom = _zoom

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, _angle: float) -> None:
        self._angle = _angle

    @property
    def target(self) -> Tuple[float, float]:
        return self._target[:2]

    @target.setter
    def target(self, _target: Tuple[float, float]) -> None:
        self._target = _target + (self._target[2],)

    @property
    def target_height(self) -> float:
        return self._target[2]

    @target_height.setter
    def target_height(self, _height: float) -> None:
        self._target = self._target[:2] + (_height,)

    @property
    def target_full(self) -> Tuple[float, float, float]:
        return self._target

    @target_full.setter
    def target_full(self, _target: Tuple[float, float, float]) -> None:
        self._target = _target
