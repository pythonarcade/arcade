from typing import Optional, Set, Callable, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from arcade.experimental.clock.timer import Timer



class Clock:
    """
    A clock for managing elapsed time, delta time, and timers

    A clock has a tick method that can either be called directly
    or is called by its parent clock. If a clock has a parent
    DO NOT CALL its tick method.

    A clock can have any number of child timers or clocks.

    The tick speed of a clock is how fast time elapses for it.

    When a clock calls tick on its children it passes its modified delta_time

    Arcade's clocks are synchronous. No matter how long an update takes
    all queries to a clock's elapsed time will be the same. This ensures
    that two objects who have the same lifespan and are created at the
    same time will die on the same frame in the future.
    """

    def __init__(self, *,
                 tick_speed: float = 1.0,
                 initial_elapsed_time: float = 0.0,
                 initial_tick_count: int = 0,
                 parent: Optional["Clock"] = None
                 ):
        self._tick_speed: float = tick_speed

        self._elapsed_time: float = initial_elapsed_time
        self._tick_count: int = initial_tick_count

        self._parent: Optional[Clock] = parent

        self._children: Set[Clock] = set()
        self._timers: Set[Timer] = set()

        self._delta_time_raw: float = 0.0

    def tick(self, delta_time: float):
        self._tick_count += 1
        self._delta_time_raw = delta_time

        self._elapsed_time = self._delta_time_raw * self._tick_speed

        for child in tuple(self._children):
            child.tick(self._delta_time_raw * self._tick_speed)

        for timer in tuple(self._timers):
            if timer.complete:
                timer.kill()
            timer.check()

    def create_new_child(self, *,
                         tick_speed: float = 1.0,
                         inherit_elapsed: bool = False,
                         inherit_count: bool = False,
                         lifespan: float = 0.0
                        ):
        pass

    def create_new_timer(self, duration: float, callback: Callable, *,
                         callback_args: Optional[List[Any]] = None,
                         callback_kwargs: Optional[Dict[str, Any]] = None
                         ):
        args = callback_args or list()
        kwargs = callback_kwargs or dict()
