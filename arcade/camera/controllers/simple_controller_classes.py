from typing import TYPE_CHECKING, Optional, Tuple
from math import e, sin, cos, radians, pi, log
from random import uniform

from arcade.camera.data import CameraData
from arcade.window_commands import get_window

if TYPE_CHECKING:
    from arcade.application import Window


class ScreenShaker2D:
    """
    Uses the equation Ae^{-fx}sin(v 2 pi x) to create shake effect which falls off over time.

    where:
        A is the amplitude (size)
        f is the falloff
        v is the speed
        x is the time since start
        e is euler's constant
    """

    stop_range: float = 0.1
    # TODO Doc Strings

    def __init__(self, camera_data: CameraData, default_shake_size: float = 1.0, default_shake_falloff: float = 1.0, *,
                 window: Optional["Window"] = None,
                 default_shake_speed: float = 1.0,
                 default_shake_jitter: float = 0.0,
                 default_shake_direction: Tuple[float, float] = (-1.0, 0.0)):
        self._win: "Window" = window or get_window()
        self._data: CameraData = camera_data

        self._d_dir = default_shake_direction
        self._d_speed = default_shake_speed
        self._d_amplitude = default_shake_size
        self._d_falloff = default_shake_falloff
        self._d_jitter = default_shake_jitter

        self._t_dir = default_shake_direction
        self._t_speed = default_shake_speed
        self._t_amplitude = default_shake_size
        self._t_falloff = default_shake_falloff
        self._t_jitter = default_shake_jitter

        self._shake: bool = False
        self._time: float = 0.0
        self._stop_time: float = -1.0
        self._t_pos: Tuple[float, float] = camera_data.position[:2]

    def start(self, *,
              true_pos: Optional[Tuple[float, float]] = None,
              temp_size: Optional[float] = None,
              temp_falloff: Optional[float] = None,
              temp_speed: Optional[float] = None,
              temp_jitter: Optional[float] = None,
              temp_direction: Optional[Tuple[float, float]] = None):

        self._t_dir = temp_direction if temp_direction is not None else self._d_dir
        self._t_jitter = temp_jitter if temp_jitter is not None else self._d_jitter
        self._t_speed = temp_speed if temp_speed is not None else self._d_speed
        self._t_falloff = temp_falloff if temp_falloff is not None else self._d_falloff
        self._t_amplitude = temp_size if temp_size is not None else self._d_amplitude

        self._time = 0.0
        self._shake = True
        self._t_pos = true_pos if true_pos is not None else self._t_pos
        self._stop_time = self.estimated_length()

    def _curve(self, _t: float) -> float:
        return self._t_amplitude * e**(-self._t_falloff*_t) * sin(self._t_speed * 2.0 * pi * self._time)

    def estimated_length(self) -> float:
        _t = (log(self._t_amplitude) - log(self.stop_range)) / self._t_falloff
        _dt = _t % (0.5 / self._t_speed)  # Find the distance from to the last x = 0.0
        return _t - _dt

    def shaking(self) -> bool:
        return self._shake

    def stop(self):
        self.stop_in(self._t_speed - (self._time % self._t_speed))

    def stop_in(self, _time: float):
        # This derivation was a pain
        _dt = self._time % (1.0 / self._t_speed)

        _f = log(self._t_amplitude) - log(0.1) - self._t_falloff * self._time
        _a = self._t_amplitude * e**(_f * _dt - self._t_falloff * self._time)

        self._t_amplitude = _a
        self._t_falloff = _f
        self._time = _dt

        _st = _time % (0.5 / self._t_speed)
        self._stop_time = _time - _st

    def update(self, delta_time: float, true_pos: Optional[Tuple[float, float]] = None):
        if true_pos is not None:
            self._t_pos = true_pos

        if 0.0 <= self._stop_time <= self._time + delta_time:
            self._time = 0.0
            self._shake = False
            return

        if not self._shake:
            self._time = 0.0
            return

        _m = 0.5 / self._t_speed
        if self._t_jitter != 0.0 and self._time % _m > (self._time + delta_time) % _m:
            radians_shift = radians(uniform(-self._t_jitter/2.0, self._t_jitter/2.0))
            _c, _s = cos(radians_shift), sin(radians_shift)
            dx = self._t_dir[0] * _c - self._t_dir[1] * _s
            dy = self._t_dir[0] * _s + self._t_dir[1] * _c
            self._t_dir = (dx, dy)

        self._time += delta_time

    def update_camera(self, true_pos: Optional[Tuple[float, float]] = None):
        if true_pos is not None:
            self._t_pos = true_pos

        step = self._curve(self._time)
        pos = (
            self._t_pos[0] + step * self._t_dir[0],
            self._t_pos[1] + step * self._t_dir[1]
        )
        self._data.position = (pos[0], pos[1], self._data.position[2])

    @property
    def direction(self) -> Tuple[float, float]:
        return self._t_dir

    @direction.setter
    def direction(self, _dir: Tuple[float, float]):
        self._t_dir = _dir
        self._stop_time = self.estimated_length()

    @property
    def jitter(self) -> float:
        return self._t_jitter

    @jitter.setter
    def jitter(self, _jitter: float):
        self._t_jitter = _jitter
        self._stop_time = self.estimated_length()

    @property
    def speed(self) -> float:
        return self._t_speed

    @speed.setter
    def speed(self, _speed: float):
        self._t_speed = _speed
        self._stop_time = self.estimated_length()

    @property
    def falloff(self) -> float:
        return self._t_falloff

    @falloff.setter
    def falloff(self, _falloff: float):
        self._t_falloff = _falloff
        self._stop_time = self.estimated_length()

    @property
    def amplitude(self) -> float:
        return self._t_amplitude

    @amplitude.setter
    def amplitude(self, _amplitude: float):
        self._t_amplitude = _amplitude
        self._stop_time = self.estimated_length()

    @property
    def default_direction(self) -> Tuple[float, float]:
        return self._d_dir

    @default_direction.setter
    def default_direction(self, _dir: Tuple[float, float]):
        self._d_dir = _dir
        self._t_dir = _dir
        self._stop_time = self.estimated_length()

    @property
    def default_jitter(self) -> float:
        return self._d_jitter

    @default_jitter.setter
    def default_jitter(self, _jitter: float):
        self._d_jitter = _jitter
        self._t_jitter = _jitter
        self._stop_time = self.estimated_length()

    @property
    def default_speed(self) -> float:
        return self._d_speed

    @default_speed.setter
    def default_speed(self, _speed: float):
        self._d_speed = _speed
        self._t_speed = _speed
        self._stop_time = self.estimated_length()

    @property
    def default_falloff(self) -> float:
        return self._d_falloff

    @default_falloff.setter
    def default_falloff(self, _falloff: float):
        self._d_falloff = _falloff
        self._t_falloff = _falloff
        self._stop_time = self.estimated_length()

    @property
    def default_amplitude(self) -> float:
        return self._d_amplitude

    @default_amplitude.setter
    def default_amplitude(self, _amplitude: float):
        self._d_amplitude = _amplitude
        self._t_amplitude = _amplitude
        self._stop_time = self.estimated_length()


def _shakey():
    from arcade import Window, draw_point

    from arcade.camera import Camera2D

    win = Window()
    cam = Camera2D()
    shake = ScreenShaker2D(cam.data, 200, default_shake_speed=1.0, default_shake_jitter=20, default_shake_falloff=0.5)

    def on_key_press(*args):
        if shake.shaking():
            shake.stop()
        else:
            shake.start()

    win.on_key_press = on_key_press

    def on_update(delta_time: float):
        shake.update(delta_time)

    win.on_update = on_update

    def on_draw():
        win.clear()
        shake.update_camera()
        cam.use()
        draw_point(100, 100, (255, 255, 255, 255), 10)

    win.on_draw = on_draw

    win.run()


if __name__ == '__main__':
    _shakey()

