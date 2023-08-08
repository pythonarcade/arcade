# TODO: Treats the camera as a 3D Isometric camera
#  and allows for spinning around a focal point
#  and moving along the isometric grid
from typing import Tuple
from math import sin, cos, radians

from arcade.camera.data import CameraData


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
        p1, p2, p3 = (
            (_c * self._right[0] + _s * self._up[0]),
            (_c * self._right[1] + _s * self._up[1]),
            (_c * self._right[2] + _s * self._up[2])
        )
        _rotation_rads = -radians(self._angle + 45)
        _c2, _s2 = cos(_rotation_rads/2.0), sin(_rotation_rads/2.0)
        q0, q1, q2, q3 = (
            _c2,
            _s2 * self._up[0],
            _s2 * self._up[1],
            _s2 * self._up[2]
        )
        q0_2, q1_2, q2_2, q3_2 = q0**2, q1**2, q2**2, q3**2
        q01, q02, q03, q12, q13, q23 = q0*q1, q0*q2, q0*q3, q1*q2, q1*q3, q2*q3

        _x = p1 * (q0_2 + q1_2 - q2_2 - q3_2) + 2.0 * (p2 * (q12 - q03) + p3 * (q02 + q13))
        _y = p2 * (q0_2 - q1_2 + q2_2 - q3_2) + 2.0 * (p1 * (q03 + q12) + p3 * (q23 - q01))
        _z = p3 * (q0_2 - q1_2 - q2_2 + q3_2) + 2.0 * (p1 * (q13 - q02) + p2 * (q01 + q23))

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


def iso_test():
    from arcade import Window, SpriteSolidColor, Sprite, SpriteList
    from random import choice, uniform
    from arcade.camera import OrthographicProjector, Camera2D
    vals = (50, 100, 150, 200, 250)

    win = Window(1920, 1080)
    cam = OrthographicProjector()
    cam.view_data.position = (0.0, 0.0, 0.0)
    cam.projection_data.near = 0
    cam.projection_data.far = 2500
    controller = IsometricCameraController(
        cam.view_data,
        dist=1000
    )
    sprites = SpriteList(capacity=1200)
    sprites.extend(
        tuple(
            SpriteSolidColor(100, 100, 100 * x, 100 * y, color=(choice(vals), choice(vals), choice(vals), 255))
            for x in range(-5, 6) for y in range(-5, 6)
        )
    )
    _log = tuple(
        Sprite('log.png')
        for _ in range(500)
    )
    for index, sprite in enumerate(_log):
        sprite.depth = index/2.0
    sprites.extend(_log)

    def on_press(r, m):
        controller.target = uniform(-250, 250), 0.0

    def on_draw():
        win.clear()
        cam.use()
        sprites.draw(pixelated=True)

    def on_update(dt: float):
        controller.angle = (controller.angle + 45 * dt) % 360
        controller.update_position()

    win.on_key_press = on_press
    win.on_update = on_update
    win.on_draw = on_draw

    win.run()


if __name__ == '__main__':
    iso_test()
