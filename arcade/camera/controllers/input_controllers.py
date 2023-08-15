# TODO: Are 2D and 3D versions of a very simple controller
#  intended to be used for debugging.
from typing import TYPE_CHECKING, Tuple
from copy import deepcopy

from pyglet.math import Vec3

from arcade.camera.data import CameraData
from arcade.camera.controllers.simple_controller_functions import rotate_around_forward
from arcade.window_commands import get_window
import arcade.key as KEYS
if TYPE_CHECKING:
    from arcade.application import Window


class PolledCameraController2D:
    MOVE_UP: int = KEYS.W
    MOVE_DOWN: int = KEYS.S

    MOVE_RIGHT: int = KEYS.D
    MOVE_LEFT: int = KEYS.A

    ROTATE_RIGHT: int = KEYS.E
    ROTATE_LEFT: int = KEYS.Q

    ZOOM_IN: int = KEYS.PLUS
    ZOOM_OUT: int = KEYS.MINUS

    RESET: int = KEYS.R
    SAVE: int = KEYS.U

    TOGGLE_MOUSE_CENTER: int = KEYS.T

    MOVE_SPEED: float = 600.0
    ROTATE_SPEED: float = 60.0

    def __init__(self, data: CameraData, *, window: "Window" = None):
        self._win: "Window" = window or get_window()

        self._data: CameraData = data

        self._original_data: CameraData = deepcopy(data)

        self._mouse_old_pos: Tuple[float, float] = (0, 0)

        self._testy: float = 0.

    def reset(self):
        self._data.viewport = self._original_data.viewport

        self._data.position = self._original_data.position

        self._data.up = self._original_data.up
        self._data.forward = self._original_data.forward
        self._data.zoom = self._original_data.zoom

    def save(self):
        self._original_data = deepcopy(self._data)

    def change_control_data(self, _new: CameraData, _reset_prev: bool = False):
        if _reset_prev:
            self.reset()
        self._data = _new
        self._original_data = deepcopy(_new)

    def update(self, dt):
        self._testy = ((self._testy - 0.1) + dt) % 2.0 + 0.1
        self._data.zoom = self._testy

        if self._win.keyboard[self.RESET]:
            self.reset()
            return

        if self._win.keyboard[self.SAVE]:
            self.save()
            return

        _rot = self._win.keyboard[self.ROTATE_LEFT] - self._win.keyboard[self.ROTATE_RIGHT]
        if _rot:
            rotate_around_forward(self._data, _rot * dt * self.ROTATE_SPEED)

        _vert = self._win.keyboard[self.MOVE_UP] - self._win.keyboard[self.MOVE_DOWN]
        _hor = self._win.keyboard[self.MOVE_RIGHT] - self._win.keyboard[self.MOVE_LEFT]

        if _vert or _hor:
            _dir = (_hor / (_vert**2.0 + _hor**2.0)**0.5, _vert / (_vert**2.0 + _hor**2.0)**0.5)

            _up = self._data.up
            _right = Vec3(*self._data.forward).cross(Vec3(*self._data.up))

            _cam_pos = self._data.position

            _cam_pos = (
                _cam_pos[0] + dt * self.MOVE_SPEED * (_right[0] * _dir[0] + _up[0] * _dir[1]),
                _cam_pos[1] + dt * self.MOVE_SPEED * (_right[1] * _dir[0] + _up[1] * _dir[1]),
                _cam_pos[2] + dt * self.MOVE_SPEED * (_right[2] * _dir[0] + _up[2] * _dir[1])
            )
            self._data.position = _cam_pos


class PolledCameraController3D:
    MOVE_FORE: int = KEYS.W
    MOVE_BACK: int = KEYS.S

    MOVE_RIGHT: int = KEYS.D
    MOVE_LEFT: int = KEYS.A

    ROTATE_RIGHT: int = KEYS.E
    ROTATE_LEFT: int = KEYS.Q

    ZOOM_IN: int = KEYS.PLUS
    ZOOM_OUT: int = KEYS.MINUS

    RESET: int = KEYS.R
    SAVE: int = KEYS.U

    MOVE_SPEED: float = 600.0
    ROTATE_SPEED: float = 60.0

    def __init__(self, data: CameraData, *, window: "Window" = None, center_mouse: bool = True):
        self._win: "Window" = window or get_window()

        self._data: CameraData = data

        self._original_data: CameraData = deepcopy(data)

        self._mouse_old_pos: Tuple[float, float] = (0, 0)
        self._center_mouse: bool = center_mouse

    def toggle_center_mouse(self):
        self._center_mouse = bool(1 - self._center_mouse)

    def reset(self):
        self._data.viewport = self._original_data.viewport

        self._data.position = self._original_data.position

        self._data.up = self._original_data.up
        self._data.forward = self._original_data.forward
        self._data.zoom = self._original_data.zoom

    def save(self):
        self._original_data = deepcopy(self._data)

    def change_control_data(self, _new: CameraData, _reset_prev: bool = False):
        if _reset_prev:
            self.reset()
        self._data = _new
        self._original_data = deepcopy(_new)

    def update(self, dt):

        if self._center_mouse:
            self._win.set_exclusive_mouse()

        if self._win.keyboard[self.RESET]:
            self.reset()
            return

        if self._win.keyboard[self.SAVE]:
            self.save()
            return

        _rot = self._win.keyboard[self.ROTATE_LEFT] - self._win.keyboard[self.ROTATE_RIGHT]
        if _rot:
            print(self.ROTATE_SPEED)
            rotate_around_forward(self._data, _rot * dt * self.ROTATE_SPEED)

        _move = self._win.keyboard[self.MOVE_FORE] - self._win.keyboard[self.MOVE_BACK]
        _strafe = self._win.keyboard[self.MOVE_RIGHT] - self._win.keyboard[self.MOVE_LEFT]

        if _strafe or _move:
            _for = self._data.forward
            _right = Vec3(*self._data.forward).cross(Vec3(*self._data.up))

            _cam_pos = self._data.position

            _cam_pos = (
                _cam_pos[0] + dt * self.MOVE_SPEED * (_right[0] * _strafe + _for[0] * _move),
                _cam_pos[1] + dt * self.MOVE_SPEED * (_right[1] * _strafe + _for[1] * _move),
                _cam_pos[2] + dt * self.MOVE_SPEED * (_right[2] * _strafe + _for[2] * _move)
            )
            self._data.position = _cam_pos


def fps_test():
    from random import randrange as uniform

    from arcade import Window, SpriteSolidColor, SpriteList
    from arcade.camera import OrthographicProjector, PerspectiveProjector

    win = Window()
    proj = OrthographicProjector()
    cont = PolledCameraController2D(proj.view_data)
    sprites = SpriteList()
    sprites.extend(
        tuple(SpriteSolidColor(uniform(25, 125), uniform(25, 125), uniform(0, win.width), uniform(0, win.height))
              for _ in range(uniform(10, 15)))
    )

    def on_mouse_motion(x, y, dx, dy, *args):
        pass
    win.on_mouse_motion = on_mouse_motion

    def on_update(dt):
        cont.update(dt)
    win.on_update = on_update

    def on_draw():
        win.clear()
        proj.use()
        sprites.draw(pixelated=True)
    win.on_draw = on_draw

    win.run()


if __name__ == '__main__':
    fps_test()