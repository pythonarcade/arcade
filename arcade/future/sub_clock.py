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

