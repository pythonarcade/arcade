from typing import Optional, Set
from arcade.experimental.clock.timer import Timer


class Clock:
    """
    A clock for managing elapsed time, delta time, and timers

    A clock has a tick method that can either be called directly
    or is called by its parent clock. If a clock has a parent
    DO NOT CALL its tick method.

    A clock can have any number of child timers or clocks.
    The children and timers are stored in unordered sets, therefore
    the properties which return them make no promises on the order.

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
                 frozen: bool = False,
                 parent: Optional["Clock"] = None
                 ):
        self.tick_speed: float = tick_speed
        self._frozen: bool = frozen

        self._elapsed_time: float = initial_elapsed_time
        self._tick_count: int = initial_tick_count

        self._parent: Optional[Clock] = parent

        self._children: Set[Clock] = set()
        self._timers: Set[Timer] = set()

        self._delta_time_raw: float = 0.0

    def tick(self, delta_time: float):
        self._tick_count += 1
        if self._frozen:
            return
        self._delta_time_raw = delta_time

        self._elapsed_time = self._delta_time_raw * self.tick_speed

        for child in tuple(self._children):
            child.tick(self._delta_time_raw * self.tick_speed)

        for timer in tuple(self._timers):
            if timer.complete:
                timer.kill()
            timer.check()

    #def create_new_child(self, *,
    #                     tick_speed: float = 1.0,
    #                     inherit_elapsed: bool = False,
    #                     inherit_count: bool = False,
    #                     lifespan: float = 0.0
    #                    ) -> "Clock":
    #    pass

    #def create_new_timer(self, duration: float, callback: Callable,
    #                     *args,
    #                     **kwargs
    #                     ) -> Timer:
    #    pass

    def add_clock(self, new_child: "Clock"):
        pass

    def add_timer(self, new_timer: Timer):
        pass

    def free(self):
        if self._parent:
            self._parent.pop_child(self)

    def time_since(self, start: float):
        return self._elapsed_time - start

    @property
    def delta_time(self):
        return self._delta_time_raw * self._tick_speed

    @property
    def delta_time_raw(self):
        return self._delta_time_raw

    @property
    def elapsed(self):
        return self._elapsed_time

    @property
    def frozen(self):
        return self._frozen

    def freeze(self):
        self._frozen = True

    def unfreeze(self):
        self._frozen = False

    def toggle_frozen(self) -> bool:
        self._frozen = bool(1 - self._frozen)
        return self._frozen

    @property
    def children(self):
        return tuple(self._children)

    def pop_child(self, child: "Clock"):
        pass

    @property
    def timers(self):
        return tuple(self._timers)

    def pop_timer(self, timer: Timer):
        """
        Popping a timer allows you to remove a timer from a clock without destroying the timer.
        """
        pass

    @property
    def parent(self):
        return self._parent

    def transfer_parent(self, new_parent):
        pass

    @property
    def tick_count(self):
        return self._tick_count
