import pytest as pytest

from arcade.clock import Clock, FixedClock, GLOBAL_CLOCK, GLOBAL_FIXED_CLOCK

def test_clock():
    # GLOBAL_CLOCK.set_tick_speed(1.0)
    time = GLOBAL_CLOCK.time
    ticks = GLOBAL_CLOCK.ticks
    GLOBAL_CLOCK.tick(1.0/60.0)
    assert GLOBAL_CLOCK.time == time + 1.0/60.0
    assert GLOBAL_CLOCK.ticks == ticks + 1
    assert GLOBAL_CLOCK.delta_time == 1.0/60.0

    GLOBAL_CLOCK.set_max_deltatime(1.0/100.0)
    GLOBAL_CLOCK.tick(1.0 / 60.0)
    assert GLOBAL_CLOCK.time == time + 1.0/60.0 + 1.0 / 100.0
    assert GLOBAL_CLOCK.ticks == ticks + 2
    assert GLOBAL_CLOCK.delta_time == 1.0/100.0

    GLOBAL_CLOCK.set_max_deltatime()

    with pytest.raises(ValueError):
        GLOBAL_FIXED_CLOCK.tick(1.0)