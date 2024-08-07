from __future__ import annotations
from typing import Optional, Union

from arcade.clock import Clock, GLOBAL_CLOCK

def boot_strap_clock(clock: Optional[Clock] = None):
    """
    Because the sub_clock is not a fully featured part of arcade we have to
    manipulate the clocks before the can be used with sub_clocks.

    This step will no longer be required when SubClocks become part of the main
    library.

    calling it will boostrap the global clock.
    DO NOT CALL MORE THAN ONCE PER CLOCK.

    Args:
        clock: a clcok that has yet to be setup. Defaults to arcade.clock.GLOBAL_CLOCK.
    """
    clock = clock or GLOBAL_CLOCK

    if hasattr(clock, 'children'):
        raise ValueError(f'The clock {clock} has already been bootstrapped.')

    clock.children = [] # type: ignore -- No type check will ever like this, but we do what we must.

    def recursive_tick(delta_time: float) -> None:
        clock.tick(delta_time)
        for child in clock.children:  # type: ignore -- we know the clock will have .children
            child.tick(clock._tick_delta_time)

    clock.tick = recursive_tick

    def add_child(child: SubClock):
        clock.children.append(child)  # type: ignore -- we know the clock will have .children

    clock.add_child = add_child  # type: ignore -- we know the clock will have .children


class SubClock(Clock):
    """
    A SubClock which gets ticked by a parent clock and can have its flow
    of time altered independantly of its parent or siblings.

    Args:
        parent: The clock which will tick the SubClock.
            could be the GLOBAL_CLOCK or another SubClock
        tick_speed: A multiplier on how the 'speed' of time.
            i.e. a value of 0.5 means time elapsed half as fast for this clock. Defaults to 1.0.
    """

    def __init__(self, parent: Union[Clock, SubClock, None] = None, tick_speed: float = 1):
        parent = parent or GLOBAL_CLOCK
        super().__init__(parent._elapsed_time, parent._tick, tick_speed)
        self.children: list[SubClock] = []
        try:
            parent.add_child(self)  # type: ignore -- we know the clock will have .children (or if not we want it to yell)
        except AttributeError:
            raise AttributeError(f'The clock {parent} has not been bootstrapped properly'
                                 f'call boot_strap_clock({parent}) before adding children')

    def add_child(self, child: SubClock):
        self.children.append(child)

    def tick(self, delta_time: float):
        super().tick(delta_time)

        for child in self.children:
            child.tick(self.delta_time)
