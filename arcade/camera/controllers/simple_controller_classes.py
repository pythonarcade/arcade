from typing import TYPE_CHECKING, Optional, Tuple
from math import e, sin, cos, radians, pi, log
from random import uniform

from arcade.camera.data import CameraData
from arcade.window_commands import get_window

if TYPE_CHECKING:
    from arcade.application import Window


class ScreenShaker2D:
    """
    Ae^{-fx} - Ae^{-(z+f)x}
    """

    def __init__(self, camera_data: CameraData, *,
                 default_falloff: float = 1.0,
                 default_acceleration: float = 1.0,
                 default_amplitude: float = 1.0,
                 default_direction: Optional[Tuple[float, float]] = None):
        self._data: CameraData = camera_data

        self._d_falloff: float = default_falloff
        self._d_acceleration: float = default_acceleration
        self._d_amplitude: float = default_amplitude
        self._d_direction: Optional[Tuple[float, float]] = default_direction

        self._t_falloff: float = default_falloff
        self._t_acceleration: float = default_acceleration
        self._t_amplitude: float = default_amplitude
        self._t_direction: Optional[Tuple[float, float]] = default_direction

    def _curve(self, _t: float):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def stop_after(self, seconds: float):
        pass


class ScreenShaker2D_old:
    """
    Uses the equation Ae^{-fx}sin(v 2 pi x) to create shake effect which lessens over time.
    The shaking can be started with using the Start method. Every value has a default,
    and a temporary value. The temporary values are reset every time the animation
    is started. To stop the animation call stop or stop_in. These do not instantly
    stop the animation, but rather change the animation curve to have a smoother stop.
    The animation also has a jitter value in degrees which is how much to rotate the
    shake direction each oscillation.

    If you want the shaking to stay the same intensity and then quickly stop it is easiest
    to set the falloff to 0.0, and then call stop when you want the shaking to stop.

    where:
        A is the amplitude (size in pixels)
        f is the falloff (Higher the faster. A value of one decays after 2.25 seconds)
        v is the speed (each integer value above one increase the cycles per second by one)
        x is the time since start
        e is euler's constant (pronounced oil-ers)


    Args:
        camera_data: The Camera Data to manipulate.
        window: The Arcade Window, uses currently active by default.
        default_shake_size: The maximum amplitude away from the starting position (Equal to A).
        default_shake_falloff: The rate that the screen shake weakens (Equal to f).
        default_shake_speed: The speed or frequency of oscillations (Equal to v).
        default_shake_jitter: The max angle that the shake direction can change by.
        default_shake_direction: The direction the oscillations follow.
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
              temp_direction: Optional[Tuple[float, float]] = None) -> None:
        """
        Start the shaking animation, you can set a temporary position for any of the components of the
        animation. These values will not be saved once the animation finishes. The true pos is NOT a
        temp value.

        Args:
            true_pos: The position that the shaking will originate from.

            temp_size: A temporary, one animation only, value of the max amplitude of the shaking

            temp_falloff: A temporary, one animation only, value for the speed of falloff. Higher is faster.

            temp_speed: A temporary, one animation only, value for the oscillation speeds.
                        Each integer value adds one full cycle per second.

            temp_jitter: A temporary, one animation only, value which determines the max
                         angle change after each cycle.

            temp_direction: A temporary, one animation only, tuple which describes the x, y direction
                            the shaking will follow.
        """

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
        """
        Calculate the equation A exp(-ft) sin(2v pi t) which describes
        the distance from the true pos.

        Args:
            _t: Time in seconds.
        Returns:
            The calculated Amplitude.
        """
        return self._t_amplitude * e**(-self._t_falloff*_t) * sin(self._t_speed * 2.0 * pi * self._time)

    def estimated_length(self) -> float:
        """
        Estimates how much longer the animation still has to go with the current settings.

        Returns:
            Roughly the number of seconds until the shaking will stop.
        """
        if self._t_falloff == 0.0:
            return float('inf')
        _t = (log(self._t_amplitude) - log(self.stop_range)) / self._t_falloff
        _dt = _t % (0.5 / self._t_speed)  # Find the distance from to the last x = 0.0
        return _t - _dt

    def shaking(self) -> bool:
        """
        Returns whether the controller is causing screen shake or updating.
        """
        return self._shake

    def stop(self) -> None:
        """
        Tell the controller to stop at the next point of 0 amplitude.

        This alters the temporary values used by the controller.
        If any are changed after the fact the controller may not stop.
        """
        self.stop_in(1 / self._t_speed - (self._time % (0.5 / self._t_speed)))

    def stop_in(self, _time: float) -> None:
        """
        Tell the controller to stop after a certain number of seconds.
        The controller will actually stop at the closest point of low amplitude
        to prevent any sudden position snapping.

        This alters the temporary values used by the controller.
        If any are changed after the fact the controller may not stop.

        Args:
            _time: The number of seconds to stop after.
        """
        # This derivation was a pain
        _dt = self._time % (1.0 / self._t_speed)

        _f = log(self._t_amplitude) - log(0.1) - self._t_falloff * self._time
        _a = self._t_amplitude * e**(_f * _dt - self._t_falloff * self._time)

        self._t_amplitude = _a
        self._t_falloff = _f
        self._time = _dt

        _st = (_time + _dt) % (0.5 / self._t_speed)

        self._stop_time = _dt + _time - _st

    def update(self, delta_time: float, true_pos: Optional[Tuple[float, float]] = None) -> None:
        """
        Run the update logic for the controller. This should be called every update, but only once.
        This does not actually change the position of the camera. That is done in update_camera.

        Args:
            delta_time: The length of time since the last update call. Use the delta_time provided
                        in arcade.Window.on_update, or arcade.View.on_update.
                        3.x+: will be replaced whatever delta_time solution is created in the future.

            true_pos: The position from which the oscillation originates. If you have another animation
                      which calculates the position for the camera you can pass it in here, but there is
                      also a pos property.
        """
        if true_pos is not None:
            self._t_pos = true_pos

        if 0.0 <= self._stop_time <= self._time + delta_time:
            self._time = 0.0
            self._shake = False
            return

        if not self._shake:
            self._time = 0.0
            return

        # The oscillator passes through 0.0 at regular intervals.
        # If the next time is past this interval then it is clear that 0.0
        # has been passed and jitter should be calculated.
        _m = 0.5 / self._t_speed
        if self._t_jitter != 0.0 and self._time % _m > (self._time + delta_time) % _m:
            radians_shift = radians(uniform(-self._t_jitter/2.0, self._t_jitter/2.0))
            _c, _s = cos(radians_shift), sin(radians_shift)
            dx = self._t_dir[0] * _c - self._t_dir[1] * _s
            dy = self._t_dir[0] * _s + self._t_dir[1] * _c
            self._t_dir = (dx, dy)

        self._time += delta_time

    def update_camera(self) -> None:
        """
        Take the current time and temp values and update the position of the camera.
        This method has no logic, and should never have any logic. Calling this method multiple times
        will not change the result. If you need to update the true position of the camera
        use the pos property, or the update method.
        """
        step = self._curve(self._time)
        pos = (
            self._t_pos[0] + step * self._t_dir[0],
            self._t_pos[1] + step * self._t_dir[1]
        )
        self._data.position = (pos[0], pos[1], self._data.position[2])

    @property
    def pos(self) -> Tuple[float, float]:
        """
        The point that the shaking offsets from.
        camera position will equal true pos when amplitude is 0
        """
        return self._t_pos

    @pos.setter
    def pos(self, _pos: Tuple[float, float]) -> None:
        """
        The point that the shaking offsets from.
        camera position will equal true pos when amplitude is 0
        """
        self._t_pos = _pos

    @property
    def direction(self) -> Tuple[float, float]:
        """
        The direction the shaking will move in.
        MAKE SURE THE LENGTH IS 1.0.
        """
        return self._t_dir

    @direction.setter
    def direction(self, _dir: Tuple[float, float]):
        """
        Temporarily sets this value. To permanently change it use default_direction

        The direction the shaking will move in.
        MAKE SURE THE LENGTH IS 1.0.
        """
        self._t_dir = _dir
        self._stop_time = self.estimated_length()

    @property
    def jitter(self) -> float:
        """
        The max angle the direction can randomly change by every cycle.
        """
        return self._t_jitter

    @jitter.setter
    def jitter(self, _jitter: float):
        """
        Temporarily sets this value. To permanently change it use default_jitter

        The max angle the direction can randomly change by every cycle.
        """
        self._t_jitter = _jitter
        self._stop_time = self.estimated_length()

    @property
    def speed(self) -> float:
        """
        The number of oscillations per second.
        Every integer increase causes one extra cycle.
        """
        return self._t_speed

    @speed.setter
    def speed(self, _speed: float):
        """
        Temporarily sets this value. To permanently change it use default_speed

        The number of oscillations per second.
        Every integer increase causes one extra cycle.
        """
        self._t_speed = _speed
        self._stop_time = self.estimated_length()

    @property
    def falloff(self) -> float:
        """
        The rate at which the oscillations die down. Higher the faster.
        The decay uses euler's (pronounced oil-ers) number.
        """
        return self._t_falloff

    @falloff.setter
    def falloff(self, _falloff: float):
        """
        Temporarily sets this value. To permanently change it use default_falloff

        The rate at which the oscillations die down. Higher the faster.
        The decay uses euler's (pronounced oil-ers) number.
        """
        self._t_falloff = _falloff
        self._stop_time = self.estimated_length()

    @property
    def amplitude(self) -> float:
        """
        The maximum length away from the true pos in pixels.
        """
        return self._t_amplitude

    @amplitude.setter
    def amplitude(self, _amplitude: float):
        """
        Temporarily sets this value. To permanently change it use default_amplitude

        The maximum length away from the true pos in pixels.
        """
        self._t_amplitude = _amplitude
        self._stop_time = self.estimated_length()

    @property
    def default_direction(self) -> Tuple[float, float]:
        """
        The direction the shaking will move in.
        MAKE SURE THE LENGTH IS 1.0.
        """

        return self._d_dir

    @default_direction.setter
    def default_direction(self, _dir: Tuple[float, float]):
        """
        Permanently sets this value. To temporarily change it use direction

        The direction the shaking will move in.
        MAKE SURE THE LENGTH IS 1.0.
        """

        self._d_dir = _dir
        self._t_dir = _dir
        self._stop_time = self.estimated_length()

    @property
    def default_jitter(self) -> float:
        """
        The max angle the direction can randomly change by every cycle.
        """
        return self._d_jitter

    @default_jitter.setter
    def default_jitter(self, _jitter: float):
        """
        Permanently sets this value. To temporarily change it use jitter

        The max angle the direction can randomly change by every cycle.
        """
        self._d_jitter = _jitter
        self._t_jitter = _jitter
        self._stop_time = self.estimated_length()

    @property
    def default_speed(self) -> float:
        """
        The number of oscillations per second.
        Every integer increase causes one extra cycle.
        """
        return self._d_speed

    @default_speed.setter
    def default_speed(self, _speed: float):
        """
        Permanently sets this value. To temporarily change it use speed

        The number of oscillations per second.
        Every integer increase causes one extra cycle.
        """
        self._d_speed = _speed
        self._t_speed = _speed
        self._stop_time = self.estimated_length()

    @property
    def default_falloff(self) -> float:
        """
        The rate at which the oscillations die down. Higher the faster.
        The decay uses euler's (pronounced oil-ers) number.
        """
        return self._d_falloff

    @default_falloff.setter
    def default_falloff(self, _falloff: float):
        """
        Permanently sets this value. To temporarily change it use falloff

        The rate at which the oscillations die down. Higher the faster.
        The decay uses euler's (pronounced oil-ers) number.
        """
        self._d_falloff = _falloff
        self._t_falloff = _falloff
        self._stop_time = self.estimated_length()

    @property
    def default_amplitude(self) -> float:
        """
        The maximum length away from the true pos in pixels.
        """
        return self._d_amplitude

    @default_amplitude.setter
    def default_amplitude(self, _amplitude: float):
        """
        Permanently sets this value. To temporarily change it use amplitude

        The maximum length away from the true pos in pixels.
        """
        self._d_amplitude = _amplitude
        self._t_amplitude = _amplitude
        self._stop_time = self.estimated_length()


def _shakey():
    from arcade import Window, draw_point

    from arcade.camera import Camera2D

    win = Window()
    cam = Camera2D()
    shake = ScreenShaker2D(cam.data, 200, default_shake_speed=3.0, default_shake_jitter=20, default_shake_falloff=0.0)

    def on_key_press(*args):
        if shake.shaking():
            shake.stop()
        else:
            shake.start()

    win.on_key_press = on_key_press  # type: ignore

    def on_update(delta_time: float):
        shake.update(delta_time)

    win.on_update = on_update  # type: ignore

    def on_draw():
        win.clear()
        shake.update_camera()
        cam.use()
        draw_point(100, 100, (255, 255, 255, 255), 10)

    win.on_draw = on_draw  # type: ignore

    win.run()


if __name__ == '__main__':
    _shakey()

