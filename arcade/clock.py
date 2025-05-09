__all__ = (
    "Clock",
    "FixedClock",
    "GLOBAL_CLOCK",
    "GLOBAL_FIXED_CLOCK",
)


class Clock:
    """
    A time keeping class which provides a method for easily tracking the
    elapsed time, delta_time, and number of ticks.

    Arcade provides a global clock which is automatically ticked by the window.

    *Coming post 3.0:*
    you can add 'sub-clocks' to Arcade's top level clock which will tick at the
    same time, and have cumulative tick_speeds. This allows you to slow down
    only certain elements rather than everything.

    Args:
        initial_elapsed: The amount of time the clock should assume has
            already occurred. Defaults to 0.0
        initial_tick: The number of ticks the clock should assume has already
            occurred. Defaults to 0.
        tick_speed: A multiplier on how the 'speed' of time.
            i.e. a value of 0.5 means time elapsed half as fast for this clock. Defaults to 1.0.
    """

    def __init__(
        self, initial_elapsed: float = 0.0, initial_tick: int = 0, tick_speed: float = 1.0
    ):
        self._elapsed_time: float = initial_elapsed
        self._tick: int = initial_tick
        self._tick_delta_time: float = 0.0
        self._tick_speed: float = tick_speed

        self._max_deltatime: float | None = None

    def tick(self, delta_time: float):
        """
        Update the clock with the time that has passed since the last tick.

        Args:
            delta_time: The amount of time that has passed since the last tick.
        """
        if self._max_deltatime is not None:
            delta_time = min(self._max_deltatime, delta_time)

        self._tick_delta_time = delta_time * self._tick_speed
        self._elapsed_time += self._tick_delta_time
        self._tick += 1

    def set_tick_speed(self, new_tick_speed: float):
        """
        Set the speed of time for this clock.

        Args:
            new_tick_speed: A multiplier on the 'speed' of time.
                i.e. a value of 0.5 means time elapsed half as fast for this clock.
        """
        self._tick_speed = new_tick_speed

    def set_max_deltatime(self, max_deltatime: float | None = None):
        """
        Set the maximum deltatime that the clock will allow. If a large dt is passed into
        the clock's tick method it will be clamped. This will desync the game's time with the
        real world elapsed time, but can help protect against lag-spikes, debugger pauses, and
        other pauses to the event loop. This impacts the 'raw' dt so it does not take the clock's
        tick speed into account

        Args:
            max_deltatime: The maximum number of seconds that a clock can have as it's deltatime.
                           If set to None the clock has no limit. Defaults to None.
        """
        self._max_deltatime = max_deltatime

    def time_since(self, time: float) -> float:
        """
        Calculate the amount of time that has passed since the given time.

        Args:
            time: The time to compare against.
        """
        return self._elapsed_time - time

    def ticks_since(self, tick: int) -> int:
        """
        Calculate the number of ticks that have occurred since the given tick.

        Args:
            tick: The tick to compare against.
        """
        return self._tick - tick

    @property
    def max_deltatime(self) -> float | None:
        """
        The maximum deltatime that the clock will allow. If a large dt is passed into
        """
        return self._max_deltatime

    @property
    def time(self) -> float:
        """The total number of seconds that have elapsed for this clock"""
        return self._elapsed_time

    @property
    def t(self) -> float:
        """Alias to Clock.time"""
        return self._elapsed_time

    @property
    def delta_time(self) -> float:
        """The amount of time that elapsed during the last tick"""
        return self._tick_delta_time

    @property
    def dt(self) -> float:
        """Alias to Clock.delta_time"""
        return self.delta_time

    @property
    def speed(self) -> float:
        """
        A modifier on the delta time that elapsed each tick.

        Decreasing the speed will 'slow down' time for this clock
        Immutable in 3.0
        """
        return self._tick_speed

    @property
    def ticks(self) -> int:
        """The number of ticks that have occurred for this clock."""
        return self._tick

    @property
    def tick_count(self) -> int:
        """Alias to Clock.ticks"""
        return self._tick


class FixedClock(Clock):
    """
    A fixed clock which expects its delta_time to stay constant. If it doesn't it
    will throw an error.

    Arcade provides a global fixed clock which is automatically ticked every update

    Args:
        sibling: The unfixed clock which this clock will sync with.
        fixed_tick_rate: The fixed number of seconds that pass
            for this clock every tick. Defaults to ``1.0 / 60.0``.
    """

    def __init__(self, sibling: Clock, fixed_tick_rate: float = 1.0 / 60.0):
        self._sibling_clock: Clock = sibling
        self._fixed_rate: float = fixed_tick_rate
        super().__init__()

    def set_tick_speed(self, new_tick_speed: float):
        """
        Set the speed of time for this clock.

        Args:
            new_tick_speed: A multiplier on the 'speed' of time.
                i.e. a value of 0.5 means time elapsed half as fast for this clock
        """
        raise ValueError(
            "It is not safe to change the tick speed of a fixed clock post initialization."
        )

    def tick(self, delta_time: float):
        """
        Update the clock with the time that has passed since the last tick.

        Args:
            delta_time: The amount of time that has passed since the last tick.
        """
        if delta_time != self._fixed_rate:
            raise ValueError(
                f"the delta_time {delta_time}, "
                f"does not match the fixed clock's required delta_time {self._fixed_rate}"
            )
        super().tick(self._fixed_rate)

    @property
    def rate(self) -> float:
        """The fixed number of seconds that pass for this clock every tick."""
        return self._fixed_rate

    @property
    def accumulated(self) -> float:
        """The total number of seconds that have elapsed for this clock"""
        return self._sibling_clock.time - self._elapsed_time

    @property
    def fraction(self) -> float:
        """The fraction of a fixed tick that has passed since the last tick."""
        return self.accumulated / self._fixed_rate


GLOBAL_CLOCK = Clock()
GLOBAL_FIXED_CLOCK = FixedClock(sibling=GLOBAL_CLOCK)


def _setup_clock(initial_elapsed: float = 0.0, initial_tick: int = 0, tick_speed: float = 1.0):
    """
    Private method used by the Arcade window to setup the global clock post initialization.

    Args:
        initial_elapsed: The amount of time the clock should assume
            has already occurred. Defaults to 0.0
        initial_tick: The number of ticks the clock should assume has
            already occurred. Defaults to 0.
        tick_speed: A multiplier on the 'speed' of time.
            i.e. a value of 0.5 means time elapsed half as fast for this clock.
            Defaults to 1.0.
    """
    GLOBAL_CLOCK._elapsed_time = initial_elapsed  # noqa: SLF001
    GLOBAL_CLOCK._tick = initial_tick  # noqa: SLF001
    GLOBAL_CLOCK._tick_speed = tick_speed  # noqa: SLF001


def _setup_fixed_clock(fixed_tick_rate: float = 1.0 / 60.0):
    """
    Private method used by the Arcade window to setup the global fixed clock
    post initialization.

    Args:
        fixed_tick_rate: The fixed number of seconds that pass
            for this clock every tick. Defaults to 1.0 / 60.0
    """
    GLOBAL_FIXED_CLOCK._elapsed_time = GLOBAL_CLOCK.time  # noqa: SLF001
    GLOBAL_FIXED_CLOCK._tick = GLOBAL_CLOCK.tick_count  # noqa: SLF001
    GLOBAL_FIXED_CLOCK._fixed_rate = fixed_tick_rate  # noqa: SLF001
