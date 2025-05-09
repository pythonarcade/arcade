from __future__ import annotations

from arcade.clock import GLOBAL_CLOCK, Clock


def boot_strap_clock(clock: Clock | None = None) -> Clock:
    """
    Because the sub_clock is not a fully featured part of Arcade we have to
    manipulate the clocks before the can be used with sub_clocks.

    This step will no longer be required when SubClocks become part of the main
    library.

    calling it will boostrap the global clock.
    DO NOT CALL MORE THAN ONCE PER CLOCK.

    Args:
        clock: a clcok that has yet to be setup. Defaults to arcade.clock.GLOBAL_CLOCK.
    """
    clock = clock or GLOBAL_CLOCK

    if hasattr(clock, "children"):
        raise ValueError(f"The clock {clock} has already been bootstrapped.")

    # No type check will ever like this, but we do what we must.
    clock.children = []  # type: ignore

    def recursive_tick(delta_time: float) -> None:
        clock.tick(delta_time)
        for child in clock.children:  # type: ignore
            child.tick(clock._tick_delta_time)

    # Hey we did a decorator manually! what a time to be alive.
    clock.tick = recursive_tick  # type: ignore

    def add_child(child: SubClock) -> None:
        clock.children.append(child)  # type: ignore

    clock.add_child = add_child  # type: ignore

    return clock


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

    def __init__(self, parent: Clock | SubClock | None = None, tick_speed: float = 1) -> None:
        parent = parent or GLOBAL_CLOCK
        super().__init__(parent._elapsed_time, parent._tick, tick_speed)
        self.children: list[SubClock] = []
        try:
            parent.add_child(self)  # type: ignore
        except AttributeError:
            raise AttributeError(
                f"The clock {parent} has not been bootstrapped properly"
                f"call boot_strap_clock({parent}) before adding children"
            )

    def add_child(self, child: SubClock) -> None:
        self.children.append(child)

    def tick(self, delta_time: float) -> None:
        super().tick(delta_time)

        for child in self.children:
            child.tick(self.delta_time)
