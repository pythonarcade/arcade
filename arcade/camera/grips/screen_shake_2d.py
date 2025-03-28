"""
ScreenShakeController2D:
    Provides an easy way to cause a camera to shake.
"""

from math import exp, floor, log, pi, sin
from random import randint, uniform

from arcade.camera.data_types import CameraData
from arcade.math import quaternion_rotation

__all__ = ("ScreenShake2D",)


class ScreenShake2D:
    """
    Offsets the camera position in a random direction repeatedly over
    a set length of time to create a screen shake effect.

    The amplitude of the screen-shaking grows based on two functions.
    The first is a simple sin wave whose frequency is adjustable.
    This is multiplied with a pair of equations which go from 0-1 smoothly.
    the equation rises using a inverse exponential equation, before decreasing
    using a modified smooth-step sigmoid.

    Args:
        camera_data:
            The CameraData PoD that the controller modifies. Should not be
            changed once initialized.
        max_amplitude:
            The largest possible world space offset.
        falloff_time:
            The length of time in seconds it takes the shaking to reach 0 after
            reaching the maximum. Can be set to a negative number to disable falloff.
        acceleration_duration:
            The length of time in seconds it takes the shaking to reach max
            amplitude. Can be set to 0.0 to start at max amplitude.
        shake_frequency:
            The number of peaks per second. Avoid making it a multiple of half
            the target frame-rate. (e.g. at 60 fps avoid 30, 60, 90, 120, etc.)
        shake_angle:
            The angle around which the shake will focus. Defaults to 0 (horizontal)
            This is actuall 0 or 180 degress as the shake angle is mirrored.
        shake_range:
            The range in degrees from the shake angle that the shake may fall within.
            defaults to 90 degrees. This gives a range of +/- 90 degrees which covers the
            full circle because the shake angle is mirrored 180 degrees.
    """

    def __init__(
        self,
        camera_data: CameraData,
        *,
        max_amplitude: float = 1.0,
        falloff_time: float = 1.0,
        acceleration_duration: float = 1.0,
        shake_frequency: float = 15.0,
        shake_angle: float = 90.0,
        shake_range: float = 90.0,
    ):
        self._data: CameraData = camera_data

        self.max_amplitude: float = max_amplitude
        """The largest possible world space offset."""

        self.falloff_duration: float = falloff_time
        """
        The length of time in seconds it takes the shaking to reach 0
        after reaching the maximum.
        """

        self.shake_frequency: float = shake_frequency
        """
        The number of peaks per second. Avoid making it a multiple of
        half the target frame-rate.
        """

        self._acceleration_duration: float = acceleration_duration

        self.shake_angle: float = shake_angle
        self.shake_range: float = shake_range

        self._shaking: bool = False
        self._length_shaking: float = 0.0

        self._current_dir: float = 0.0
        self._last_vector: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self._last_update_time: float = 0.0

    @property
    def shaking(self) -> bool:
        """Read only property to check if the controller is currently shaking the camera."""
        return self._shaking

    @property
    def duration(self) -> float:
        """
        The length of the screen shake in seconds.

        If falloff is disabled (by setting falloff_duration to a negative number) only returns the
        acceleration duration.

        Setting the duration to a negative number disables falloff.
        While the falloff is disabled setting duration will only set the acceleration.
        Otherwise, scales both the acceleration and falloff time to match new duration.
        """
        if self.falloff_duration < 0.0:
            return self._acceleration_duration
        return self._acceleration_duration + self.falloff_duration

    @duration.setter
    def duration(self, _duration: float) -> None:
        if _duration <= 0.0:
            self.falloff_duration = -1.0

        elif self.falloff_duration < 0.0:
            self._acceleration_duration = _duration
            return

        else:
            ratio = _duration / self.duration
            self._acceleration_duration = ratio * self._acceleration_duration
            self.falloff_duration = ratio * self.falloff_duration

    @property
    def current_amplitude(self) -> float:
        """Read only property which provides the current shake amplitude."""
        return self._calc_amplitude() * self.max_amplitude

    @property
    def acceleration_duration(self) -> float:
        """
        The length of time in seconds it takes for the shaking to reach max amplitude.

        Setting to a value less than zero causes the amplitude to start at max.
        """
        return self._acceleration_duration

    @acceleration_duration.setter
    def acceleration_duration(self, _duration: float) -> None:
        if _duration < 0.0:
            self._acceleration_duration = 0.0
        else:
            self._acceleration_duration = _duration

    @property
    def acceleration(self) -> float:
        """
        The inverse of acceleration time.

        setting to a value less than zero causes the amplitude to start at max.
        """
        if self._acceleration_duration <= 0.0:
            return 0.0
        return 1 / self._acceleration_duration

    @acceleration.setter
    def acceleration(self, _acceleration: float) -> None:
        if _acceleration <= 0.0:
            self._acceleration_duration = 0.0
        else:
            self._acceleration_duration = 1 / _acceleration

    @property
    def falloff(self) -> float:
        """
        The maximum gradient of the amplitude falloff,
        and is the gradient at the inflection point of the sigmoid equation.

        Is inversely proportional to the falloff duration by a factor of 15/8.
        """
        if self.falloff_duration < 0.0:
            return -1.0
        return (15 / 8) * (1 / self.falloff_duration)

    @falloff.setter
    def falloff(self, _falloff: float) -> None:
        if _falloff <= 0.0:
            self.falloff_duration = -1.0
        else:
            self.falloff_duration = (15 / 8) * (1 / _falloff)

    def _acceleration_amp(self, _t: float) -> float:
        """
        The equation for the growing half of the amplitude equation.
        It uses 1.0001 so that at _t = 1.0 the amplitude equals 1.0.

        Args:
            _t: The scaled time. Should be between 0.0 and 1.0
        """
        return 1.0001 - 1.0001 * exp(log(0.0001 / 1.0001) * _t)

    def _falloff_amp(self, _t: float) -> float:
        """
        The equation for the falloff half of the amplitude equation.
        It is based on the 'smootherstep' function.

        Args:
            _t: The scaled time. Should be between 0.0 and 1.0
        """
        return 1 - _t**3 * (_t * (_t * 6.0 - 15.0) + 10.0)

    def _calc_max_amp(self) -> float:
        """
        Determine the maximum amplitude by using either _acceleration_amp() or _falloff_amp().
        If falloff duration is less than 0.0 then the falloff never begins and
        """
        if self._length_shaking <= self._acceleration_duration:
            _t = self._length_shaking / self._acceleration_duration
            return self._acceleration_amp(_t)

        if self.falloff_duration < 0.0:
            return self.max_amplitude

        if self._length_shaking <= self.duration:
            _t = (self._length_shaking - self._acceleration_duration) / self.falloff_duration
            return self._falloff_amp(_t)

        return 0.0

    def _calc_amplitude(self) -> float:
        _max_amp = self._calc_max_amp()
        _sin_amp = sin(self.shake_frequency * 2.0 * pi * self._length_shaking)

        return _sin_amp * _max_amp

    def reset(self) -> None:
        """
        Reset the temporary shaking variables. WILL NOT STOP OR START SCREEN SHAKE.
        """
        self._current_dir = 0.0
        self._last_vector = (0.0, 0.0, 0.0)
        self._last_update_time = 0.0
        self._length_shaking = 0.0

    def start(self) -> None:
        """
        Start the screen-shake.
        """
        self.reset()
        self._shaking = True

    def stop(self) -> None:
        """
        Instantly stop the screen-shake.
        """
        self._data.position = (
            self._data.position[0] - self._last_vector[0],
            self._data.position[1] - self._last_vector[1],
            self._data.position[2] - self._last_vector[2],
        )

        self.reset()
        self._shaking = False

    def update(self, delta_time: float) -> None:
        """
        Update the time, and decide if the shaking should stop.
        Does not actually set the camera position.
        Should not be called more than once an update cycle.

        Args:
            delta_time:
                the length of time in seconds between update calls. Generally pass
                in the delta_time provided by the arcade.Window's on_update method.
        """
        if not self._shaking:
            return

        self._length_shaking += delta_time

        if self.falloff_duration > 0.0 and self._length_shaking >= self.duration:
            self.stop()

    def update_camera(self) -> None:
        """
        Update the position of the camera. Call this just before using the camera.
        because the controller is modifying the PoD directly it stores the last
        offset and resets the camera's position before adding the next offset.
        """
        if not self._shaking:
            return

        if (
            floor(self._last_update_time * 2 * self.shake_frequency)
            < floor(self._length_shaking * 2.0 * self.shake_frequency)
        ) or self._last_update_time == 0.0:
            # Start from the shake angle and then offset by the reflected shake range,
            # then randomly pick whether to mirror to the other side.
            self._current_dir = (
                self.shake_angle
                + uniform(-self.shake_range, self.shake_range)
                + (180 * randint(0, 1))
            )

        _amp = self._calc_amplitude() * self.max_amplitude
        _vec = quaternion_rotation(self._data.forward, self._data.up, self._current_dir)

        _last = self._last_vector
        _pos = self._data.position

        self._data.position = (
            _pos[0] - _last[0] + _vec[0] * _amp,
            _pos[1] - _last[1] + _vec[1] * _amp,
            _pos[2] - _last[2] + _vec[2] * _amp,
        )

        self._last_vector = (_vec[0] * _amp, _vec[1] * _amp, _vec[2] * _amp)
        self._last_update_time = self._length_shaking

    def readjust_camera(self) -> None:
        """
        Can be called after the camera has been used revert the screen_shake.
        While not strictly necessary it is highly advisable. If you are moving the
        camera using an animation or something similar the behavior can start to go
        awry if you do not readjust after the screen shake.
        """
        self._data.position = (
            self._data.position[0] - self._last_vector[0],
            self._data.position[1] - self._last_vector[1],
            self._data.position[2] - self._last_vector[2],
        )
        self._last_vector = (0.0, 0.0, 0.0)

    def __enter__(self):
        self.update_camera()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.readjust_camera()
        return False
