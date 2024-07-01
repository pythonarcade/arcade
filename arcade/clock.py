class Clock:
    """
    A time keeping class.

    :Coming post 3.0:
    you can add 'sub-clocks' to arcade's top level clock which will tick at the same time, and
    have cumulative tick_speeds. This allows you to slow down only certain elements rather than everything.
    """

    def __init__(
        self, initial_elapsed: float = 0.0, initial_frame: int = 0, tick_speed: float = 1.0
    ):
        self._elapsed_time: float = initial_elapsed
        self._frame: int = initial_frame
        self._tick_delta_time: float = 0.0
        self._tick_speed: float = tick_speed

    def tick(self, delta_time: float):
        self._tick_delta_time = delta_time * self._tick_speed
        self._elapsed_time += self._tick_delta_time
        self._frame += 1

    def time_since(self, time: float):
        return self._elapsed_time - time

    def frames_since(self, frame: int):
        return self._frame - frame

    @property
    def time(self):
        """
        The total number of seconds that have elapsed for this clock
        """
        return self._elapsed_time

    @property
    def t(self):
        """
        Alias to Clock.time
        """
        return self._elapsed_time

    @property
    def delta_time(self):
        """
        The amount of time that elapsed during the last tick
        """
        return self.delta_time

    @property
    def dt(self):
        """
        Alias to Clock.delta_time
        """
        return self.delta_time

    @property
    def speed(self):
        """
        A modifier on the delta time that elapsed each tick.

        Decreasing the speed will 'slow down' time for this clock
        Immutable in 3.0
        """
        return self._tick_speed

    @property
    def frame(self):
        """
        The number of ticks that have occurred for this clock
        """
        return self._frame

    @property
    def tick_count(self):
        """
        Alias to Clock.frame
        """
        return self._frame


class FixedClock(Clock):
    """
    A fixed clock which expects its delta_time to stay constant. If it doesn't it will throw an error.
    """

    def __init__(self, sibling: Clock, fixed_tick_rate: float = 1.0 / 60.0):
        self._sibling_clock: Clock = sibling
        self._fixed_rate: float = fixed_tick_rate
        super().__init__()

    def tick(self, delta_time: float):
        if delta_time != self._fixed_rate:
            raise ValueError(
                f"the delta_time {delta_time}, "
                f"does not match the fixed clock's required delta_time {self._fixed_rate}"
            )
        super().tick(self._fixed_rate)

    @property
    def rate(self):
        return self._fixed_rate

    @property
    def accumulated(self):
        return self._elapsed_time - self._sibling_clock.time

    @property
    def fraction(self):
        return self.accumulated / self._fixed_rate
